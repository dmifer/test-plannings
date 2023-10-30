from pymongo.database import Database, Collection
from bson.objectid import ObjectId

from models.Planning import Planning


class DBPlanning:

    collection: Collection

    def __init__(self, db: Database) -> None:
        self.collection = db["planning"]

    def update_planning(self, pl, approvals, status):
        self.collection.update_one(
            {"_id": pl},
            {"$set": {"approvals": approvals, "status": status}},
        )

    def insert_plannings(self, plannings: list[Planning], user: str):
        for planning in plannings:
            planning.author = user

        return self.collection.insert_many([
            planning.dict() for planning in plannings
        ])

    def get_plannings(self, ids):
        return self.collection.find({"_id": {"$in": ids}})

    def get_planning(self, id):
        return self.collection.find_one({"_id": ObjectId(id)})


class DBNotifications:

    collection: Collection

    def __init__(self, db: Database) -> None:
        self.collection = db["notifications"]

    def create_notifications(self, notifications: list):
        return self.collection.insert_many(notifications)


class DBMessages:

    collection: Collection

    def __init__(self, db: Database) -> None:
        self.collection = db["messages"]

    def create_message(self, message: dict):
        return self.collection.insert(message)


class DBUsers:

    collection: Collection

    def __init__(self, db: Database) -> None:
        self.collection = db["users"]

    def all(self):
        return self.collection.find()

    def get(self, email):
        return self.collection.find_one({"email": email})


class DBTeams:

    collection: Collection

    def __init__(self, db: Database) -> None:
        self.collection = db["teams"]

    def get_user_team_members(self, members):
        query = {"members": members}
        projection = {"members": 1, "_id": 0}
        return self.collection.find_one(query, projection)

    def get_user_teams(self, user):
        return self.collection.find_one({
            "$or": [
                {"approvers": {"$in": [user]}},
                {"has_access": {"$in": [user]}},
                {"members": {"$in": [user]}},
                {"partners": {"$in": [user]}},
                {"hrs": {"$in": [user]}},
                {"internal_booking_levels": {"$elemMatch": {"$in": [user]}}},
                {"external_booking_levels": {"$elemMatch": {"$in": [user]}}},
            ]
        })
