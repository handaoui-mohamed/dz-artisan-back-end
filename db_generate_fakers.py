#!flask/bin/python
from app import db
from app.user.models import User
from app.user.models import Job
from app.upload.models import ProfilePicture, Upload
import json
import random

jobs = Job.query.all()

with open("users.json", "r") as users_json:
    users = json.load(users_json)

for user in users["users"]:
    # create a new user
    new_user = User(username=user["user_name"],email=user["email"])
    new_user.hash_password("123456789")
    db.session.add(new_user)
    db.session.commit()

    #update the new user credentials
    new_user.full_name = user['full_name']
    new_user.address = user['address']
    new_user.phone_number = user['phone_number']
    new_user.description = user['description']

    # update user job list
    new_user.add_jobs(random.sample(range(1,len(jobs)+1), random.randint(1,4)))

    # update user position
    new_user.latitude = user['latitude']
    new_user.longitude = user['longitude']

    # upload profile image
    db.session.add(ProfilePicture(name=user["profile_image"][0]["path"],user_id=new_user.id))

    # upload job pictures
    for file in user["files"]:
            db.session.add(Upload(name=file["path"], user_id=new_user.id))

    db.session.add(new_user)
    db.session.commit()
