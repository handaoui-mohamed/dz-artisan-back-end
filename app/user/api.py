from app import db
from app.user.models import User
from flask_restful import Resource
from flask import jsonify, request
# from app.user.forms import UserForm

class UserListApi(Resource):
    def get(self):
        users = User(username='test', password='123456789', full_name='test test', email='test@test.test', address='test etedts test test', phone_number='0648946132165')
        db.session.add(users)
        db.session.commit()
        return jsonify(users.to_json())

    def post(self):
        req = request.form
        user = User(username=req['username'], password=req['password'], full_name=req['full_name'],
                    email=req['email'], address=req['address'], phone_number=req['phone_number'])
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_json())