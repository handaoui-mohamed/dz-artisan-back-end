from app import api
from app.user.api import UserDetailApi, UserListApi

api.add_resource(UserListApi, '/user', endpoint='users')
api.add_resource(UserDetailApi, '/user/<int:user_id>', endpoint='user')
