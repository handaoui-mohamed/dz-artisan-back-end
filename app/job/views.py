from app import db, app
from flask import abort, request, jsonify, g
from app.user.models import User
from app.job.models import Job

# add auth required and verify admin role

# new Job
@app.route('/api/job', methods=['POST'])
def new_job():
    name = request.get_json().get('name')
    description = request.get_json().get('description')

    if name is None or Job.query.filter_by(name=name).first() is not None:
        abort(400)    # missing arguments or existing one

    job = Job(name=name, description=description)
    db.session.add(job)
    db.session.commit()
    return jsonify({'element': job.to_json()}), 201


@app.route('/api/job/<int:id>', methods=['GET', 'PUT'])
def edit_job(id):
    job = Job.query.get(id)
    if job is None:
        abort(400)

    if request.method == 'GET':    
        return jsonify({'element': job.to_json()})
    
    name = request.get_json().get('name')
    description = request.get_json().get('description', job.description)

    new_job = False
    existing_job = Job.query.filter_by(name=name).first()
    if (existing_job is None) or (existing_job.id == job.id and not (name == job.name)): new_job =True
      
    if new_job and name: job.name = name
    job.description = description
    db.session.add(job)
    db.session.commit()
    return jsonify({'element': job.to_json()})


@app.route('/api/jobs')
def get_jobs():
    return jsonify({'elements': [element.to_json() for element in Job.query.all()]})
