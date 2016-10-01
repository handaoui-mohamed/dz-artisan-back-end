# -*- coding: utf-8 -*-
from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(65), unique=True)
    password = db.Column(db.String(65))
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(60), unique=True)
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.String(300))
    # job_id = db.Column(db.Integer, db.foreignKey('job.id'))

    def __repr__(self):
        return '<User N=%s username=%s full name=%s>' % (self.id, self.username, self.full_name)

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'address': self.address,
            'phone_number': self.phone_number,
            'description': self.description
        }
