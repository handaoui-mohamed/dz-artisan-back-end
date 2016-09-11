from app import api
from app.login.api import LoginApi, LogoutApi

api.add_resource(LoginApi, '/login', endpoint='login')
api.add_resource(LogoutApi, '/logout', endpoint='logout')
