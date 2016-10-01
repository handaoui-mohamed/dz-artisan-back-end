from app import api
from app.login.api import LoginApi

api.add_resource(LoginApi, '/login', endpoint='login')
