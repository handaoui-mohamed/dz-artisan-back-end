#!flask/bin/python
from app import db
from app.job.models import Job
import json

with open("jobs.json", "r") as jobs_json:
    jobs = json.load(jobs_json)

for job in jobs:
    db.session.add(Job(name=job["name"],description=job["description"]))
    db.session.commit()
