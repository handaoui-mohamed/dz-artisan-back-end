# from app import db
#
# JOB_TYPES = ['kdlfj','dhfgjdf','jgdflkgj']
#
# class Job(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     type = db.Column('job_type', db.Enum(*JOB_TYPES, name='job_type'))
#     users = db.relationship('User', backref='user', lazy='dynamic')