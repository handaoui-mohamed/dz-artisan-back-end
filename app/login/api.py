from flask_restful import Resource
from flask import request, g
from app.user.models import User


# login API
class LoginApi(Resource):

    def post(self):
        form = request.form
        if form['username'] and form['password']:
            user = User.query.filter_by(username=form['username'], password=form['password']) \
                   if '@' not in form['username'] else \
                   User.query.filter_by(email=form['username'], password=form['password'])
            if user:
                return {'element': user.to_json()}
        return {'error': 'bad password or username/email'}, 403
