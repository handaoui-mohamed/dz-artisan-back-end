#!/usr/bin/env python 
import os
from flask import Flask, abort, request, jsonify, g, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from werkzeug import secure_filename

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'k@tj5C:!uj7B}vtJi2p7a0_vGu["x418E=_wU&WohA#>lRYWkX))q5T}h9M_!kp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])


# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

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

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'address': self.address,
            'email': self.email,
            'phone_number': self.phone_number,
            'description': self.description,
            'job': self.job,
            'position': {
                'latitude': self.latitude,
                'longitude': self.longitude
            }
        }


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
    return (jsonify({'element':user.to_json()}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'element':user.to_json()})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/profile')
@auth.login_required
def get_resource():
    return jsonify({'element':g.user.to_json()})


@app.route('/api/search', methods=['POST'])
def search():
    # TODO: search using pagination: very important!
    # pagination = {
    #     'page': request.form['page'] or 1,
    #     'limit': request.form['limit'] or 10
    # }
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
    return jsonify({'elements': [element.to_json() for element in User.query.all()]})



# Route that will process the file upload
@app.route('/api/upload', methods=['POST'])
@auth.login_required
def upload():
    uploaded_files = request.files.getlist("file[]")
    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filenames.append(filename)
    #associate the uploaded file to the the current user (g.user)
    #send a respons containg the user and its uploded files
    return jsonify({'element':g.user.to_json()})

@app.route('/api/uploads/<string:filename>')
def get_file():
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
