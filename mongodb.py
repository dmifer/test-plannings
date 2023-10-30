from pymongo import MongoClient

from utils import MONGO_URL, MONGODB_DB_NAME

# client = MongoClient(MONGO_URL)
# db = client[MONGODB_DB_NAME]


# collections = {
#     "users": db["users"],
#     "teams": db["teams"],
#     "planning": db["planning"],
#     "notifications": db["notifications"],
# }


def get_db():
    client = MongoClient(MONGO_URL)
    db = client[MONGODB_DB_NAME]
    try:
        yield db
    finally:
        client.close()
