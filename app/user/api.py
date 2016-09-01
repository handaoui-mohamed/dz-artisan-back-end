from app import db
from flask_restful import Resource
from flask import request
from app.user.models import User
from app.user.forms import UserForm


class UserListApi(Resource):
    def get(self):
        return {'elements': [element.to_json() for element in User.query.all()]}

    def post(self):
        form = UserForm(request.form)
        if form.validate():
            user = User(username=form.username.data, password=form.password.data,
                        full_name=form.full_name.data, email=form.email.data, address=form.address.data,
                        phone_number=form.phone_number.data, desctition=form.description.data)
            db.session.add(user)
            db.session.commit()
            return user.to_json(), 201


class UserDetailApi(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        return user.to_json()