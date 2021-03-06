from pymongo import MongoClient
import urllib.parse
import logging
from pladmed.models.user import User
from bson.objectid import ObjectId

class UsersCollection:
    def __init__(self, db):
        self.usersCol = db.users
        self.usersCol.create_index("email", unique=True)
    
    def create_user(self, email, password, is_superuser, credits_):
        user = User({
            "email": email,
            "credits": credits_,
            "is_superuser": is_superuser
        })

        user.set_password(password)

        _id = self.usersCol.insert_one(user.__dict__)

        user._id = str(_id.inserted_id)

        return user

    def find_user(self, email):
        user_data = self.usersCol.find_one({"email": email})

        if not user_data:
            return None

        return User({
            "_id": str(user_data["_id"]),
            "email": user_data["email"],
            "password": user_data["password"],
            "credits": user_data["credits"],
            "is_superuser": user_data["is_superuser"]
        })

    def find_user_by_id(self, id):
        try:
            user_data = self.usersCol.find_one({"_id": ObjectId(id)})

            return User({
                "_id": str(user_data["_id"]),
                "email": user_data["email"],
                "password": user_data["password"],
                "credits": user_data["credits"],
                "is_superuser": user_data["is_superuser"]
            })
        except:
            return None   

    def change_credits(self, user, credits_):
        self.usersCol.update_one(
            {"_id": ObjectId(user._id)},
            {"$set": {"credits": credits_}}
        )

        user.credits = credits_

        return user

    def change_password(self, user, password_):
        self.usersCol.update_one(
            {"_id": ObjectId(user._id)},
            {"$set": {"password": password_}}
        )

        user.password = password_

        return user
