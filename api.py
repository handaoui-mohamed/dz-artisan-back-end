#!/usr/bin/env python
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Job types
JOB_TYPES = ['electrician', 'builder', 'constructor', 'plumber']


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(60), unique=True)
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.String(300))
    job = db.Column('job_type', db.Enum(*JOB_TYPES, name='job_type'))
    # google map lat/lgt
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['full_name']
    address = request.form['address']
    email = request.form['email']
    phone_number = request.form['phone_number']
    description = request.form['description']
    job = request.form['job']
    latitude = request.form['latitude']
    longitude = request.form['longitude']

    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username, full_name=full_name, address=address, job=job,
                email=email, phone_number=phone_number, description=description,
                latitude=latitude, longitude=longitude)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'address': user.address,
                'email': user.email,
                'phone_number': user.phone_number,
                'description': user.description,
                'job': user.job,
                'position': {
                    'latitude': user.latitude,
                    'longitude': user.longitude
                }
            }), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({
                'id': user.id,
                'username': user.username,
                'full_name': user.full_name,
                'address': user.address,
                'email': user.email,
                'phone_number': user.phone_number,
                'description': user.description,
                'job': user.job,
                'position': {
                    'latitude': user.latitude,
                    'longitude': user.longitude
                }
            })


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/profile')
@auth.login_required
def get_resource():
    return jsonify({
        'id': g.user.id,
        'username': g.user.username,
        'full_name': g.user.full_name,
        'address': g.user.address,
        'email': g.user.email,
        'phone_number': g.user.phone_number,
        'description': g.user.description,
        'job': g.user.job,
        'position': {
            'latitude': g.user.latitude,
            'longitude': g.user.longitude
        }
    })


@app.route('/api/search', methods=['POST'])
def search():
    print request.form['job']
    # TODO: search using pagination: very important!
    # query_obj = {
    #     'job': request.form['job'] or JOB_TYPES,
    # }

    # location = {
    #     'latitude': request.form['latitude'],
    #     'longitude': request.form['longitude']
    # }
    #
    # if request.form['email']:
    #     query_obj['email'] = request.form['email']
    users = User.query.filter(User.job == request.form['job']).all()
    print users
    return jsonify({'elements': len(users)})

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
