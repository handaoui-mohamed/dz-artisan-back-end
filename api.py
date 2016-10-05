#!/usr/bin/env python 
import os
from flask import Flask, abort, request, jsonify, g, send_from_directory, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from werkzeug import secure_filename
from math import radians, cos, sin, asin, sqrt

# initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = 'k@tj5C:!uj7B}vtJi2p7a0_vGu["x418E=_wU&WohA#>lRYWkX))q5T}h9M_!kp'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['HOST_URL'] = 'http://localhost:5000/api/'

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Job types
JOB_TYPES = [u'electrician', u'builder', u'constructor', u'plumber']


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True, unique=True)
    password_hash = db.Column(db.String(64))
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(60))
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    description = db.Column(db.String(300))
    job = db.Column('job_type', db.Enum(*JOB_TYPES, name='job_type'))
    # google map lat/lgt
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    # files uploads
    files = db.relationship('Upload', backref='user', lazy='dynamic')

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
            },
            'files':  [element.to_json() for element in self.files.all()]
        }
    
    def __repr__(self):
        return '<User N=%s username=%s location=(%s,%s)>' % (self.id, self.username, self.latitude, self.longitude)


# file upload
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    path = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def to_json(self):
        return {
            'id': self.id,
            'path': '%s'%os.path.join(app.config['HOST_URL'], self.path),
            'name': self.name,
            'user_id': self.user_id
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
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    remember_me = request.form.get('remember_me') or False

    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    duration = 24*3600 if not remember_me else 30*24*3600
    token = user.generate_auth_token(duration)
    return (jsonify({'token': token.decode('ascii'), 'user_id': user.id}), 201,
           {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    print user.files.all()
    if not user:
        abort(400)
    return jsonify({'element':user.to_json()})


@app.route('/api/login', methods=['POST'])
@auth.login_required
def get_auth_token():
    remember_me = request.form.get('remember_me') or False
    duration = 24*3600 if not remember_me else 30*24*3600
    token = g.user.generate_auth_token(duration)
    return jsonify({'token': token.decode('ascii'), 'user_id': g.user.id})


@app.route('/api/profile')
@auth.login_required
def profile():
    return jsonify({'element':g.user.to_json()})

@app.route('/api/edit', methods=['PUT'])
@auth.login_required
def edit():
    user = g.user
    password = request.form.get('password')
    full_name = request.form.get('full_name') or user.full_name
    address = request.form.get('address') or user.address
    email = request.form.get('email') or user.email
    phone_number = request.form.get('phone_number') or user.phone_number
    description = request.form.get('description') or user.description
    job = request.form.get('job') or user.job
    latitude = request.form.get('latitude') or user.latitude
    longitude = request.form.get('longitude') or user.longitude

    user.full_name=full_name
    user.address=address
    user.job=job
    user.email=email
    user.phone_number=phone_number
    user.description=description
    user.latitude=latitude
    user.longitude=longitude
    if password:
        user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    return (jsonify({'element':user.to_json()}), 201,
            {'Location': url_for('get_user', id=user.id, _external=True)})



@app.route('/api/search', methods=['POST'])
@app.route('/api/search/<int:page>', methods=['POST'])
def search(page=1):
    item_per_page = int(request.form.get('limit') or 10)
    jobs = [request.form.get('job')] or JOB_TYPES
    search_area = request.form.get('search_area') or 5

    location = {
        'latitude': float(request.form.get('latitude')),
        'longitude': float(request.form.get('longitude'))
    }

    users = []
    for user in User.query.all():
        user_location = {
            'latitude': float(user.latitude),
            'longitude': float(user.longitude)
        }
        if haversine(user_location, location, search_area) and jobs_intersection(user.job, jobs):
            users.append(user)
    users = [users[i:i+item_per_page] for i in range(0, len(users), item_per_page)]
    users = users[page-1] if (page <= len(users)) else []
    return jsonify({'elements': [element.to_json() for element in users]})



# Route that will process the file upload
@app.route('/api/upload', methods=['POST'])
@auth.login_required
def upload():
    uploaded_files = request.files.getlist("file[]")
    user_id = request.form['user_id']   
    filenames = []
    for file in uploaded_files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            directory = os.path.join(app.config['UPLOAD_FOLDER'], '%s/'%g.user.username)
            if not os.path.exists(directory):
                os.makedirs(directory)
            file_path = os.path.join(directory, filename)
            i = 0
            while os.path.exists(file_path):
                filename = "%s%s"%(i,filename)
                file_path = os.path.join(directory, filename)
            file.save(file_path)
            uploaded_file = Upload(name=filename,path=file_path,user_id=user_id)
            db.session.add(uploaded_file)
            db.session.commit()
            filenames.append(filename)
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_file(id):
    file = Upload.query.get(id)
    if file and file.user_id == g.user.id:
        db.session.delete(file)
        db.session.commit()
        os.remove(file.path)
    return jsonify({'element':g.user.to_json()})


@app.route('/api/uploads/<string:username>/<string:filename>')
def get_file(username, filename):
    directory = os.path.join(app.config['UPLOAD_FOLDER'], '%s/'%username)
    return send_from_directory(directory, filename)


def haversine(location1, location2, search_area):
    lat1 = location1['latitude']
    lon1 = location1['longitude']
    lat2 = location2['latitude']
    lon2 = location2['longitude']
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6367 * c
    return km >= search_area


def jobs_intersection(user_job, job_list):
        return len(set([user_job]).intersection(job_list)) > 0

if __name__ == '__main__':
    if not os.path.exists('db.sqlite'):
        db.create_all()
    app.run(debug=True)
