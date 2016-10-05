from app import db, app
from flask import abort, request, jsonify, g
from app.user.models import User
from app.job.models import Job

# new Job
@app.route('/api/job', methods=['POST'])
def new_job():
    name = request.form.get('name')
    description = request.form.get('description')
    if name is None or Job.query.filter_by(name=name).first() is not None:
        abort(400)    # missing arguments or existing one
    job = Job(name=name, description=description)
    db.session.add(job)
    db.session.commit()
    return jsonify({'element': job.to_json_min()}), 201


@app.route('/api/job/<int:id>', methods=['PUT'])
def edit_job(id):
    job = Job.query.get(id)
    if job is None:
        abort(400)
    name = request.form.get('name') or job.name
    description = request.form.get('description') or job.description
    if name is None or Job.query.filter_by(name=name).first() is not None:
        abort(400)    # missing arguments or existing one
    job.name = name
    job.description = description
    db.session.add(job)
    db.session.commit()
    return jsonify({'element': job.to_json_min()})


# @app.route('/api/job/<string:name>')
# def get_job(name):
#     jobs = Job.query.filter_by(name=name).all()
#     return jsonify({'elements': [element.to_json() for element in jobs]})


@app.route('/api/jobs')
def get_jobs():
    return jsonify({'elements': [element.to_json() for element in Job.query.all()]})
