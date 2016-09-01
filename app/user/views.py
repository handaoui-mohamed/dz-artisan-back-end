from app import api
from app.user.api import UserListApi


api.add_resource(UserListApi, '/users')