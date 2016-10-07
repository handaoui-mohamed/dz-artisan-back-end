from app import db, app, auth
from app.user.models import User
from app.job.models import Job
from flask import abort, request, jsonify, g, send_from_directory, url_for
from config import YEAR, DAY

@app.route('/api/user', methods=['POST'])
def new_user():
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    remember_me = request.form.get('remember_me', False)

    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    duration = DAY if not remember_me else YEAR
    token = user.generate_auth_token(duration)
    return (jsonify({'token': token.decode('ascii'), 'user_id': user.id}), 201,
           {'Location': url_for('get_user', id=user.id, _external=True)})


@app.route('/api/user/<int:id>')
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
@auth.login_required
def get_auth_token():
    remember_me = request.form.get('remember_me', False)
    duration = DAY if not remember_me else YEAR
    token = g.user.generate_auth_token(duration)
    return jsonify({'token': token.decode('ascii'), 'user_id': g.user.id})


@app.route('/api/profile', methods=['GET', 'PUT'])
@auth.login_required
def profile():
    if request.method == 'GET':
        return jsonify({'element':g.user.to_json()})
    
    if request.method == 'PUT':
        user = g.user
        password = request.form.get('password')
        full_name = request.form.get('full_name', user.full_name) 
        address = request.form.get('address', user.address)
        email = request.form.get('email', user.email)
        phone_number = request.form.get('phone_number', user.phone_number)
        description = request.form.get('description', user.description)
        jobs = request.form.get('jobs', user.jobs)
        latitude = request.form.get('latitude', user.latitude, type=float)
        longitude = request.form.get('longitude', user.longitude, type=float)

        if request.form.get('jobs') is not None: user.add_job(Job.query.get(job))
        
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
    item_per_page = request.form.get('limit', 10, type=int)
    jobs = request.form.get('jobs', JOB_TYPES)
    search_area = request.form.get('search_area', 5, type=int) or 5

    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
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