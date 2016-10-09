#!/usr/bin/env python 
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import basedir
from flask_cors import CORS


# initialization
app = Flask(__name__)
app.config.from_object('config')
# extensions
db = SQLAlchemy(app)

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
# import APIs
from app.user import views
from app.job import views
from app.upload import views

# import models
from app.user.models import User
from app.job.models import Job
from app.upload.models import Upload, ProfilePicture
