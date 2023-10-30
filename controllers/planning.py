from datetime import datetime

from pymongo.database import Database

from controllers.common import (
    extract_name_from_email,
    send_template_mail,
    get_full_name_opt,
    parse_date,
)
from utils import (
    PLANNING_APPROVED,
    PLANNING_PENDING,
    APPROVAL_MESSAGES,
    GATE_REDIRECT_LINK,
)
from .planning_crud import (
    DBUsers, DBTeams, DBNotifications, DBPlanning, DBMessages
)


def generate_notification_text(planning: dict, users: list):

    start = parse_date(planning["dayStart"])
    end = parse_date(planning["dayFinish"])

    start = f"{start.day}".zfill(2) + "." + f"{start.month}".zfill(2)
    end = f"{end.day}".zfill(2) + "." + f"{end.month}".zfill(2)

    author_fname = get_full_name_opt(planning.get("author"), users)
    user_fname = get_full_name_opt(planning.get("user"), users)
    return (
        f'{author_fname} created booking for {user_fname} '
        f'for {planning.get("client")} ({planning.get("project")}), '
        f'from {start} to {end}, for {planning["hours"]} hours.'
    )


def check_notifications(dbusers: DBUsers, status: str, email: str, type: str):
    user = dbusers.get(email)
    notifications_statuses = list(
        user["notifications"][type]["statuses"]
    )
    notifications = user["notifications"][type]["enabled"]
    if notifications and status in notifications_statuses:
        return True
    return False


async def approval_notification(
    db: Database, users, planning_id, status=PLANNING_PENDING, meta={}
):
    dbplanning = DBPlanning(db)
    planning = dbplanning.get_planning(planning_id)
    message = APPROVAL_MESSAGES[status]
    notifications = []

    for user in users:
        notifications.append(
            {
                "show_to": user,
                "text": message,
                "meta": {"planning_id": str(planning_id)},
                "type": "notification",
                "client": planning.get("client"),
                "project": planning.get("project"),
                "date": datetime.now().strftime("%Y-%m-%d"),
            }
        )
        if meta.get("send_mail"):
            await send_notification(
                user=user,
                planning=planning,
                planning_id=planning_id,
                meta=meta
            )
    dbnotifications = DBNotifications(db)
    dbnotifications.create_notifications(notifications)


async def notify_users(db: Database, data):
    insert_objects = []
    for planning in data:
        for user in planning["show_to"]:
            insert_objects.append({
                "show_to": user,
                "text": planning["text"],
                "type": "notification",
                "date": datetime.now().strftime("%Y-%m-%d"),
            })
            await send_mail(user=user, message=planning["text"])

    dbnotifications = DBNotifications(db)
    dbnotifications.create_notifications(insert_objects)


def insert_change(db: Database, data, planning_id, manager, assigner):
    text = data["text"]
    text = text.replace(manager, get_full_name(db, manager))
    text = text.replace(assigner, get_full_name(db, assigner))

    if data.get("type") != "conflict":
        dbmessages = DBMessages(db)
        dbmessages.create_message({
            "planning_id": str(planning_id),
            "message": text,
            "change": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })


def planning_approval(
    db: Database,
    planning_id: str,
    creator: str,
    user: str,
    status: str,
    payload: dict = {}
):
    approvals = []

    dbteams = DBTeams(db)
    users_team = dbteams.get_user_teams(user=user)
    creators_team = dbteams.get_user_teams(user=creator)

    if payload.get("project") == "Leaves":
        creators_approvers_levels = creators_team.get(
            "internal_booking_levels", {})
        users_approvers_levels = users_team.get("internal_booking_levels", {})

        if creators_approvers_levels == {}:
            creators_team["approvers"] = []

        if users_approvers_levels == {}:
            entities_to_empty = ["approvers", "partners", "has_access", "hrs"]
            for i in entities_to_empty:
                users_team[i] = []

        approvals, status = gen_approvals_and_status(
            db=db,
            planning_id=planning_id,
            creator=creator,
            level_dict=users_approvers_levels
        )
    else:
        creators_approvers_levels = creators_team.get(
            "external_booking_levels", {})
        users_approvers_levels = users_team.get("external_booking_levels", {})

        approvals, status = gen_approvals_and_status(
            db=db,
            planning_id=planning_id,
            creator=creator,
            level_dict=users_approvers_levels
        )

    return approvals, status


def gen_approvals_and_status(
    db: Database, planning_id: str, creator: str, level_dict: dict
):

    amount_users_levels = len(level_dict)
    creator_level = find_level_user(creator, level_dict)

    if creator_level == amount_users_levels:
        approvals = []
        status = PLANNING_APPROVED
    else:
        approvals = level_dict.get(str(creator_level + 1))
        status = PLANNING_PENDING
        approval_notification(db, approvals, planning_id, status)

    return approvals, status


def find_level_user(user, level_dict: dict):
    for key, value in level_dict.items():
        if user in value:
            return int(key)
    return 0


async def send_notification(user, planning, meta):
    """ Send notification to users
    """
    user_fn = _extract_fullname_from_email(user)
    author_fn = _extract_fullname_from_email(planning["author"])
    approver_fn = _extract_fullname_from_email(meta.get("approver"))

    project = planning.get("project")
    hours = planning["hours"]
    day_start = planning["dayStart"]
    day_finish = planning["dayFinish"]

    message = (
        f'Planning created by {author_fn} to {user_fn} for '
        f'project "{project}" for {hours} hours from '
        f'{day_start} to {day_finish} was approved by {approver_fn}.'
    )

    await send_mail(user=user, message=message)


def _extract_fullname_from_email(email: str):
    first_name, last_name = extract_name_from_email(email)
    return f"{first_name} {last_name}"


async def send_mail(user, message):
    first_name, last_name = extract_name_from_email(user)
    await send_template_mail({
        "template": "planning.html",
        "replacers": {
            "[main_message]": message,
            "[receiver]": f"{first_name} {last_name}",
            "[invitation_link]": GATE_REDIRECT_LINK,
        },
        "receiver": user,
        "title": "Compass Bookings",
    })


def get_full_name(db: Database, email: str):
    dbusers = DBUsers(db)
    user = dbusers.get(email=email)
    firstname, lastname = user["firstname"], user["lastname"]
    return f"{firstname} {lastname}"


# def find_object_by_id(array, target_id):
#     result = [obj for obj in array if obj["_id"] == target_id]
#     return result[0] if result else None
