from typing import Optional

from pydantic import BaseModel, EmailStr
from bson.objectid import ObjectId


class Planning(BaseModel):

    _id: ObjectId
    user: EmailStr
    client: str
    project: str
    dayStart: str
    dayFinish: str
    hours: str
    task: Optional[str]
    author: Optional[str]
    distributed: Optional[bool]
    daily_hours: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "_id": ObjectId("5e73d2e514235240d42222e1"),
                "user": "username@gmail.com",
                "client": "IBM",
                "project": "Data Analysis",
                "dayStart": "22.01.2022",
                "dayFinish": "22.12.2023",
                "hours": "40",
            }
        }


class InputPlanning(BaseModel):

    planning: list[Planning]
