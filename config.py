# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))
WTF_CSRF_ENABLED = True
SECRET_KEY = 'k@tj5C:!uj7B}vtJi2p7a0_vGu["x418E=_wU&WohA#>lRYWkX))q5T}h9M_!kp'
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_COMMIT_ON_TEARDOWN=True
SQLALCHEMY_TRACK_MODIFICATIONS=True
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
HOST_URL = 'http://localhost:5000/api/'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
