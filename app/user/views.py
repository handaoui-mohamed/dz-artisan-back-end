from app import db, app
from app.user.models import User
from app.user.forms import UserForm
from app.job.models import Job
from flask import abort, request, jsonify, g, send_from_directory, url_for, make_response
from config import YEAR, DAY, SECRET_KEY
import jwt
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from functools import wraps
from werkzeug.datastructures import MultiDict

# JWT AUTh process start
def create_token(user, days=1):
    payload = {
        'sub': user.id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=days)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token.decode('unicode_escape')


def parse_token(req):
    token = req.headers.get('Authorization').split()[1]
    return jwt.decode(token, SECRET_KEY, algorithms='HS256')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('Authorization'):
            response = jsonify(message='Missing authorization header')
            response.status_code = 401
            return response

        try:
            payload = parse_token(request)
        except DecodeError:
            response = jsonify(message='Token is invalid')
            response.status_code = 401
            return response
        except ExpiredSignature:
            response = jsonify(message='Token has expired')
            response.status_code = 401
            return response

        g.user_id = payload['sub']
        g.user = User.query.get(g.user_id)
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/users', methods=['POST'])
def new_user():
    data = request.get_json(force=True)
    form = UserForm(MultiDict(mapping=data))
    if form.validate():
        for fieldName, errorMessages in form.errors.iteritems():
            print fieldName
            for err in errorMessages:
                print err
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        remember_me = data.get('remember_me', False)
        user = User(username=username.lower(), email=email.lower())
        user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        duration = DAY if not remember_me else YEAR
        token = create_token(user, duration)
        return (jsonify({'token': token.decode('ascii'), 'user_id': user.id}), 201,
               {'Location': url_for('get_users', id=user.id, _external=True)})
    return jsonify({"form_errors": form.errors}), 400


@app.route('/api/users/<int:id>')
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        abort(404)
    return jsonify({'element':user.to_json()})

@app.route('/api/users/<string:username>')
def get_user_by_username(username):
    user = User.query.filter_by(username=username).first();
    if not user:
        abort(404)
    return jsonify({'element':user.to_json()})


@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify({'elements': [element.to_json() for element in users]})



@app.route('/api/login', methods=['POST'])
def get_auth_token():
    data = request.get_json(force=True)
    username = data.get('username')
    password = data.get('password')
    remember_me = data.get('remember_me', False)
    duration = DAY if not remember_me else YEAR
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        abort(404)
    g.user = user
    token = create_token(g.user, duration)
    return jsonify({'token': token.decode('ascii'), 'user': g.user.to_json()})


@app.route('/api/profile', methods=['GET', 'PUT'])
@login_required
def profile():
    if request.method == 'GET':
        return jsonify({'element':g.user.to_json()})

    if request.method == 'PUT':
        user = g.user
        data = request.get_json(force=True)
        form = UserForm(MultiDict(mapping=data))
        if form.validate():
            password = data.get('password')
            full_name = data.get('full_name', user.full_name)
            address = data.get('address', user.address)
            email = data.get('email', user.email)
            phone_number = data.get('phone_number', user.phone_number)
            description = data.get('description', user.description)
            jobs = data.get('jobs', user.jobs)
            latitude = data.get('latitude', user.latitude)
            longitude = data.get('longitude', user.longitude)

            if data.get('jobs') is not None: user.add_jobs(jobs)

            if full_name is not None : user.full_name=full_name.lower()
            if address is not None: user.address=address.lower()
            if email is not None: user.email=email.lower()
            user.phone_number=phone_number
            user.description=description
            user.latitude=latitude
            user.longitude=longitude
            if password: user.hash_password(password)
            db.session.add(user)
            db.session.commit()
            return (jsonify({'element':user.to_json()}), 201,
                    {'Location': url_for('get_users', id=user.id, _external=True)})
        return jsonify({"form_errors": form.errors}), 400


@app.route('/api/search', methods=['POST'])
@app.route('/api/search/<int:page>', methods=['POST'])
def search(page=1):
    data = request.get_json(force=True)
    item_per_page = data.get('limit', 6)
    jobs = data.get('jobs', Job.query.all())
    search_area = data.get('search_area', 5)

    location = data.get('location')
    print location
    location_search = False
    if location and location['latitude'] and location['longitude']:
        location_search = True

    users = []
    for user in User.query.all():
        if location_search and user.latitude and user.longitude:
            user_location = {
                'latitude': float(user.latitude),
                'longitude': float(user.longitude)
            }
            if haversine(user_location, location, search_area) and jobs_intersection(user.jobs, jobs):
                users.append(user)
        else:
            if jobs_intersection(user.jobs, jobs):
                users.append(user)

    users = [users[i:i+item_per_page] for i in range(0, len(users), item_per_page)]
    total_pages = len(users)
    users = users[page-1] if (page <= len(users)) else []
    return jsonify({'total_pages': total_pages,'elements': [element.to_json() for element in users]})


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


def jobs_intersection(user_jobs, jobs_list):
    if len(jobs_list) == 0 and len(user_jobs) > 0: return True
    if len(jobs_list) != len(user_jobs): return False
    for job in jobs_list:
        for user_job in user_jobs:
            if job['name'] != user_job.name:
                return False
    return True
