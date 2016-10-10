from app import db, app
from app.user.models import User
from app.job.models import Job
from flask import abort, request, jsonify, g, send_from_directory, url_for, make_response
from config import YEAR, DAY, SECRET_KEY
import jwt
from jwt import DecodeError, ExpiredSignature
from datetime import datetime, timedelta
from functools import wraps

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
    username = request.get_json().get('username')
    password = request.get_json().get('password')
    email = request.get_json().get('email')
    remember_me = request.get_json().get('remember_me', False)

    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    duration = DAY if not remember_me else YEAR
    token = create_token(user, duration)
    return (jsonify({'token': token.decode('ascii'), 'user_id': user.id}), 201,
           {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'element':user.to_json()})


@app.route('/api/users')
def get_users():
    users = User.query.all()
    return jsonify({'elements': [element.to_json() for element in users]})



@app.route('/api/login', methods=['POST'])
def get_auth_token():
    form = request.get_json(force=True)
    username = form.get('username')
    password = form.get('password')
    remember_me = form.get('remember_me', False)
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
        password = request.get_json().get('password')
        full_name = request.get_json().get('full_name', user.full_name) 
        address = request.get_json().get('address', user.address)
        email = request.get_json().get('email', user.email)
        phone_number = request.get_json().get('phone_number', user.phone_number)
        description = request.get_json().get('description', user.description)
        jobs = request.get_json().get('jobs', user.jobs)
        latitude = request.get_json().get('latitude', user.latitude, type=float)
        longitude = request.get_json().get('longitude', user.longitude, type=float)

        if request.get_json().get('jobs') is not None: user.add_job(Job.query.get(job))
        
        user.full_name=full_name
        user.address=address
        user.email=email
        user.phone_number=phone_number
        user.description=description
        user.latitude=latitude
        user.longitude=longitude
        if password: user.hash_password(password)
        db.session.add(user)
        db.session.commit()
        return (jsonify({'element':user.to_json()}), 201,
                {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/search', methods=['POST'])
@app.route('/api/search/<int:page>', methods=['POST'])
def search(page=1):
    item_per_page = request.get_json().get('limit', 10, type=int)
    jobs = request.get_json().get('jobs', JOB_TYPES)
    search_area = request.get_json().get('search_area', 5, type=int) or 5

    latitude = request.get_json().get('latitude')
    longitude = request.get_json().get('longitude')
    location_search = False
    if latitude and longitude:
        location_search = True
        location = {
            'latitude': float(latitude),
            'longitude': float(longitude)
        }

    users = []
    for user in User.query.all():
        if location_search:
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
    users = users[page-1] if (page <= len(users)) else []
    return jsonify({'elements': [element.to_json() for element in users]})


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
        return len(set(user_job).intersection(job_list)) > 0