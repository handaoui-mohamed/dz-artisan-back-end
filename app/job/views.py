from app import db, app
from flask import abort, request, jsonify, g
from app.user.models import User
from app.job.models import Job

# add auth required and verify admin role

# new Job
@app.route('/api/jobs', methods=['GET', 'POST'])
def new_job():
    if request.method == 'GET':
        print 'here'
        return jsonify({'elements': [element.to_json() for element in Job.query.all()]})
    else:
        data = request.get_json(force=True)
        name = data.get('name')
        description = data.get('description')

        if name is None or Job.query.filter_by(name=name).first() is not None:
            abort(400)    # missing arguments or existing one

        job = Job(name=name, description=description)
        db.session.add(job)
        db.session.commit()
        return jsonify({'element': job.to_json()}), 201


@app.route('/api/jobs/<int:id>', methods=['GET', 'PUT'])
def edit_job(id):
    job = Job.query.get(id)
    if job is None:
        abort(400)

    if request.method == 'GET':    
        return jsonify({'element': job.to_json()})
    
    data = request.get_json(force=True)
    name = data.get('name')
    description = data.get('description', job.description)

    new_job = False
    existing_job = Job.query.filter_by(name=name).first()
    if (existing_job is None) or (existing_job.id == job.id and not (name == job.name)): new_job =True
      
    if new_job and name: job.name = name
    job.description = description
    db.session.add(job)
    db.session.commit()
    return jsonify({'element': job.to_json()})
