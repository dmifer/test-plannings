from fastapi import (
    APIRouter, HTTPException, Request, BackgroundTasks, Depends
)
from pymongo.database import Database

from models.Planning import InputPlanning
from controllers.planning_crud import DBPlanning, DBUsers, DBTeams
from controllers.planning import (
    planning_approval,
    notify_users,
    insert_change,
    generate_notification_text,
    check_notifications,
)

from mongodb import get_db
from utils import PLANNING_PENDING


router = APIRouter(
    prefix="/api/planning",
    tags=["planning"],
)


@router.post("/create_plannings")
async def create_plannings(
    obj: InputPlanning,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Database = Depends(get_db)
):

    dbplanning = DBPlanning(db)
    dbusers = DBUsers(db)
    dbteams = DBTeams(db)
    user = request.state.email

    if not user:
        raise HTTPException(status_code=400, detail="Authorization error")

    notifications = {"text": "", "show_to": []}
    users = list(dbusers.all())
    insertions = dbplanning.insert_plannings(plannings=obj.planning, user=user)
    plannings = list(dbplanning.get_plannings(ids=insertions.inserted_ids))

    for planning in plannings:

        pl = planning["_id"]
        approvals, status = planning_approval(
            db=db,
            planning_id=str(pl),
            creator=user,
            user=planning["user"],
            status=PLANNING_PENDING,
            payload=planning,
        )
        dbplanning.update_planning(pl, approvals, status)

        text = generate_notification_text(planning, users)
        notifications["text"] = text
        insert_change(
            db=db,
            data={"text": text},
            planning_id=pl,
            manager=planning.get("author"),
            assigner=planning.get("user")
        )

        if check_notifications(dbusers, status, planning["user"], "personal"):
            notifications["show_to"].append(planning["user"])

        user_team_members = dbteams.get_user_team_members(planning["user"])
        if user_team_members:
            for team_member in user_team_members["members"]:

                if check_notifications(dbusers, status, team_member, "team"):
                    if team_member not in notifications["show_to"]:
                        notifications["show_to"].append(team_member)

        if check_notifications(dbusers, status, planning["author"], "owner"):
            if planning["author"] not in notifications["show_to"]:
                notifications["show_to"].append(planning["author"])

        if len(notifications["show_to"]) > 0:
            # notifications["show_to"] = ",".join(notifications["show_to"])
            background_tasks.add_task(notify_users, db, [notifications])
            # await notify_users(db, notifications)

    return {"message": "Inserted successfully"}
