#!/usr/bin/env python 
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth


# initialization
app = Flask(__name__)
app.config.from_object('config')
# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# import APIs
from app.user import views
from app.job import views
from app.upload import views

# import models
from app.user.models import User
from app.job.models import Job
from app.upload.models import Upload



