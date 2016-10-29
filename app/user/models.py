# -*- coding: utf-8 -*-
from app import db, app
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from app.job.models import Job
from app.upload.models import Upload, ProfilePicture
from config import SECRET_KEY


UserJob = db.Table(
    'UserJob',
    db.Column('id', db.Integer, primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'))
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String)
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(60))
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.Text)
    jobs = db.relationship('Job', secondary=UserJob, backref='user')
    # google map lat/lgt
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    # files uploads
    files = db.relationship('Upload', backref='user', lazy='dynamic')
    # profile picture
    profile_image = db.relationship('ProfilePicture', backref='user', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(SECRET_KEY, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'address': self.address,
            'email': self.email,
            'phone_number': self.phone_number,
            'description': self.description,
            'jobs': [element.to_json() for element in self.jobs],
            'position': {
                'latitude': self.latitude,
                'longitude': self.longitude
            },
            'files':  [element.to_json(self.username) for element in self.files.all()],
            'profile_image':  [element.to_json(self.username) for element in self.profile_image.all()]
        }

    def add_jobs(self, jobs):
        self.jobs = []
        for job_id in jobs:
            self.jobs.append(Job.query.get(job_id))
        return self

    def add_job(self, job):
        self.jobs.append(job)
        return self

    def __repr__(self):
        return '<User N=%s username=%s location=(%s,%s)>' % (self.id, self.username, self.latitude, self.longitude)
