# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# WTF_CSRF_ENABLED = True
SECRET_KEY = 'ab59)o(a%v19t=3j#4bt4z=-=6z%f@psw&3)qmh-5rarm6d_z4'
SQLALCHEMY_TRACK_MODIFICATIONS =False

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
