from fastapi import APIRouter, HTTPException, Request, BackgroundTasks  # noqa
from mongodb import db
from models import Planning
from controllers import planning as PlanningController
from controllers import common as CommonUtils
import utils

router = APIRouter(
    prefix="/api/planning",
    tags=["planning"],
)

@router.post("/create_plannings")
async def create_plannings(
    obj: dict, request: Request, background_tasks: BackgroundTasks
):
    user = request.state.email
    if user:
        plannings = obj.get("planning")
        users = list(db["users"].find())

        for i in range(len(plannings)):
            plannings[i]["author"] = user

        planning_models = [
            Planning.Planning(**planning).dict() for planning in plannings
        ]
        insertions = db["planning"].insert_many(planning_models)
        notifications = {"text": "", "show_to": []}
        plannings = list(db["planning"].find({"_id": {"$in": insertions.inserted_ids}}))
        for pl in insertions.inserted_ids:
            planning = PlanningController.find_object_by_id(plannings, pl)

            start = CommonUtils.parseDate(planning["dayStart"])
            end = CommonUtils.parseDate(planning["dayFinish"])

            start = f"{start.day}".zfill(2) + "." + f"{start.month}".zfill(2)
            end = f"{end.day}".zfill(2) + "." + f"{end.month}".zfill(2)

            approvals, status = PlanningController.planningApproval(
                str(pl),
                user,
                planning["user"],
                utils.PLANNING_PENDING,
                planning,
            )

            db["planning"].update_one(
                {"_id": pl},
                {"$set": {"approvals": approvals, "status": status}},
            )
            text = f'{get_full_name_opt(planning.get("author"), users)} \
created booking \
for {get_full_name_opt(planning.get("user"), users)} \
for {planning.get("client")} ({planning.get("project")}), \
from {start} to {end}, for {planning["hours"]} hours.'

            notifications["text"] = text
            personal_notifications = db["users"].find_one({"email": planning["user"]})
            personal_notifications_statuses = list(
                personal_notifications["notifications"]["personal"]["statuses"]
            )
            personal_notifications = personal_notifications["notifications"][
                "personal"
            ]["enabled"]

            if (
                personal_notifications is True
                and status in personal_notifications_statuses
            ):
                notifications["show_to"].append(planning["user"])

            PlanningController.insertChange(
                {"text": text}, pl, planning.get("author"), planning.get("user")
            )

            query = {"members": planning["user"]}
            projection = {"members": 1, "_id": 0}
            user_team_members = db["teams"].find_one(query, projection)
            if user_team_members:
                for team_member in user_team_members["members"]:
                    team_notifications = db["users"].find_one({"email": team_member})
                    team_notifications_statuses = list(
                        team_notifications["notifications"]["team"].get("statuses")
                    )
                    team_notifications = team_notifications["notifications"]["team"][
                        "enabled"
                    ]
                    if team_notifications is True \
                            and status in team_notifications_statuses:
                        if team_member not in notifications["show_to"]:
                            notifications["show_to"].append(team_member)

            owner_notifications = db["users"].find_one({"email": planning["author"]})
            owner_notifications_statuses = list(
                owner_notifications["notifications"]["owner"]["statuses"]
            )
            owner_notifications = owner_notifications["notifications"]["owner"][
                "enabled"
            ]
            if owner_notifications is True and status in owner_notifications_statuses:
                if planning["author"] not in notifications["show_to"]:
                    notifications["show_to"].append(planning["author"])

            if len(notifications["show_to"]) > 0:
                # notifications["show_to"] = ",".join(notifications["show_to"])
                background_tasks.add_task(
                    PlanningController.notify_users, [notifications]
                )
                # await PlanningController.notify_users(notifications)

        return {"message": "Inserted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Authorization error")
    
def get_full_name_opt(email, users):
    user = list(filter(lambda x: x.get("email") == email, users))[0]
    return f'{user.get("firstname")} {user.get("lastname")}'