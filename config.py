# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))
WTF_CSRF_ENABLED = True
SECRET_KEY = 'k@tj5C:!uj7B}vtJi2p7a0_vGu["x418E=_wU&WohA#>lRYWkX))q5T}h9M_!kp'
if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_COMMIT_ON_TEARDOWN=True
SQLALCHEMY_TRACK_MODIFICATIONS=True
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
HOST_URL = 'https://dz-artisan-api.herokuapp.com/api/'
CORS_HEADERS = 'Content-Type'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
YEAR = 365
DAY = 24
