from flask_restful import Resource
from flask import request, session, g
from app.user.models import User
from flask_login import login_user, current_user, logout_user
from datetime import datetime
from app import app, db, lm


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


# login API
class LoginApi(Resource):
    def get(self):
        return {'element': current_user}

    def post(self):
        form = request.form
        if (form['username'] and form['password']) and (g.user is None or not g.user.is_authenticated):
            user = User.query.filter_by(username=form['username'], password=form['password']) \
                   if '@' not in form['username'] else \
                   User.query.filter_by(email=form['username'], password=form['password'])
            if user:
                session['remember_me'] = form['remember_me']
                remember_me = False
                if 'remember_me' in session:
                    remember_me = session['remember_me']
                    session.pop('remember_me', None)
                login_user(user, remember=remember_me)
                return 200
        return {'error': 'bad password or username/email'}, 403


class LogoutApi(Resource):
    def post(self):
        logout_user()
        return 200
