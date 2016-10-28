#!flask/bin/python
from app import db
from app.user.models import User
from app.user.models import Job
import json

jobs = Job.query.all()

with open("users.json", "r") as users_json:
    users = json.load(users_json)

for user in users:
    # create a new user
    new_user = User(username=user["username"],email=user["email"])
    user.hash_password("123456789")
    db.session.add(new_user)
    db.session.commit()

    #update the new user credentials
    new_user.full_name = user['full_name']
    new_user.address = user['address']
    new_user.phone_number = user['phone_number']
    new_user.description = user['description']

    # update user job list
    new_user.jobs = user['jobs']

    # update user position
    new_user.latitude = user['latitude']
    new_user.longitude = user['longitude']

    # upload profile image

    # upload job pictures

    db.session.add(new_user)
    db.session.commit()
