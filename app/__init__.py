# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api

# flask app
app = Flask(__name__)
app.config.from_object('config')

# flask api
api = Api(app)

# database
db = SQLAlchemy(app)

# login manager
lm = LoginManager()
lm.init_app(app)

# import APIs
from app.user import views
from app.login import views

# import models
# from app.job.models import Job
from app.user.models import User



