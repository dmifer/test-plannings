import pandas as pd
from mongodb import db
from datetime import datetime, timedelta
from bson.objectid import ObjectId

from controllers import common as CommonUtils

from utils import (
    PLANNING_APPROVED,
    PLANNING_CHANGE_REQUIRED,
    PLANNING_PENDING,
    PLANNING_DECLINED,
    APPROVAL_MESSAGES,
    GATE_REDIRECT_LINK,
)



async def approvalNotification(users, planning_id, status=PLANNING_PENDING, meta={}):
    planning = db["planning"].find_one({"_id": ObjectId(planning_id)})
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
            # Users
            first_name, last_name = CommonUtils.extract_name_from_email(user)
            user_fn = f"{first_name} {last_name}"

            # Authors
            fname, lname = CommonUtils.extract_name_from_email(planning["author"])
            author_fn = f"{fname} {lname}"

            # Approver
            fname, lname = CommonUtils.extract_name_from_email(meta.get("approver"))
            approver_fn = f"{fname} {lname}"

            message = f'Planning created by {author_fn} to {user_fn} for \
project "{planning.get("project")}" for {planning["hours"]} hours \
from {planning["dayStart"]} to {planning["dayFinish"]} was approved by {approver_fn}.'

            await CommonUtils.sendTemplateMail(
                {
                    "template": "planning.html",
                    "replacers": {
                        "[main_message]": message,
                        "[receiver]": f"{first_name} {last_name}",
                        "[invitation_link]": GATE_REDIRECT_LINK,
                    },
                    "receiver": user,
                    "title": "Compass Bookings",
                }
            )

    db["notifications"].insert_many(notifications)



async def notify_users(data):
    insert_objects = []
    for planning in data:
        for user in planning["show_to"]:
            insert_objects.append(
                {
                    "show_to": user,
                    "text": planning["text"],
                    "type": "notification",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                }
            )
            first_name, last_name = CommonUtils.extract_name_from_email(user)
            await CommonUtils.sendTemplateMail(
                {
                    "template": "planning.html",
                    "replacers": {
                        "[main_message]": planning["text"],
                        "[receiver]": f"{first_name} {last_name}",
                        "[invitation_link]": GATE_REDIRECT_LINK,
                    },
                    "receiver": user,
                    "title": "Compass Bookings",
                }
            )
    db["notifications"].insert_many(insert_objects)

def get_full_name(email):
    user = db["users"].find_one({"email": email})
    return f'{user["firstname"]} {user["lastname"]}'


def find_object_by_id(array, target_id):
    result = [obj for obj in array if obj["_id"] == target_id]
    return result[0] if result else None


def insertChange(data, planning_id, manager, assigner):
    text = data["text"]
    text = text.replace(manager, get_full_name(manager))
    text = text.replace(assigner, get_full_name(assigner))

    if data.get("type") != "conflict":
        db["messages"].insert(
            {
                "planning_id": str(planning_id),
                "message": text,
                "change": True,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )


def planningApproval(
    planning_id: str, creator: str, user: str, status: str, payload: dict = {}
):
    approvals = []

    users_team = db["teams"].find_one(
        {
            "$or": [
                {"approvers": {"$in": [user]}},
                {"has_access": {"$in": [user]}},
                {"members": {"$in": [user]}},
                {"partners": {"$in": [user]}},
                {"hrs": {"$in": [user]}},
                {"internal_booking_levels": {"$elemMatch": {"$in": [user]}}},
                {"external_booking_levels": {"$elemMatch": {"$in": [user]}}},
            ]
        }
    )
    creators_team = db["teams"].find_one(
        {
            "$or": [
                {"approvers": {"$in": [creator]}},
                {"has_access": {"$in": [creator]}},
                {"members": {"$in": [creator]}},
                {"partners": {"$in": [creator]}},
                {"hrs": {"$in": [creator]}},
                {"internal_booking_levels": {"$elemMatch": {"$in": [creator]}}},
                {"external_booking_levels": {"$elemMatch": {"$in": [creator]}}},
            ]
        }
    )

    if payload.get("project") == "Leaves":

        creators_approvers_levels = creators_team.get("internal_booking_levels", {})
        users_approvers_levels = users_team.get("internal_booking_levels", {})

        if creators_approvers_levels == {}:
            creators_team["approvers"] = []

        if users_approvers_levels == {}:
            entities_to_empty = ["approvers", "partners", "has_access", "hrs"]
            for i in entities_to_empty:
                users_team[i] = []

        amount_users_levels = len(users_approvers_levels)
        creator_level = find_level_user(creator, users_approvers_levels)

        if creator_level == amount_users_levels:
            approvals = []
            status = PLANNING_APPROVED
        else:
            approvals = users_approvers_levels.get(str(creator_level + 1))
            status = PLANNING_PENDING
            approvalNotification(approvals, planning_id, status)


    else:
        creators_approvers_levels = creators_team.get("external_booking_levels", {})
        users_approvers_levels = users_team.get("external_booking_levels", {})

        amount_users_levels = len(users_approvers_levels)
        creator_level = find_level_user(creator, users_approvers_levels)

        if creator_level == amount_users_levels:
            approvals = []
            status = PLANNING_APPROVED
        else:
            approvals = users_approvers_levels.get(str(creator_level + 1))
            status = PLANNING_PENDING
            approvalNotification(approvals, planning_id, status)

    return approvals, status


def find_level_user(user, level_dict):
    for key, value in level_dict.items():
        if user in value:
            return int(key)
    return 0
