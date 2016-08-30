# -*- coding: utf-8 -*-
import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'ab59)o(a%v19t=3j#4bt4z=-=6z%f@psw&3)qmh-5rarm6d_z4'
SQLALCHEMY_TRACK_MODIFICATIONS =False

if os.environ.get('DATABASE_URL') is None:
    SQLALCHEMY_DATABASE_URI = ('sqlite:///' + os.path.join(basedir, 'app.db') +
                               '?check_same_thread=False')
else:
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# mail server settings
MAIL_SERVER = 'localhost'
MAIL_PORT = 2525
MAIL_USERNAME = None
MAIL_PASSWORD = None

# administrator list
ADMINS = ['dm_handaoui@esi.dz']

# # email server
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 465
# MAIL_USE_TLS = False
# MAIL_USE_SSL = True
# MAIL_USERNAME = 'handaoui.mohamed1@gmail.com'  # os.environ.get('MAIL_USERNAME')
# MAIL_PASSWORD = '03+04@1994'  # os.environ.get('MAIL_PASSWORD')
#
# # administrator list
# ADMINS = ['dm_handaoui@esi.dz']

# pagination
POSTS_PER_PAGE = 3

# full text search
WHOOSHEE_DIR = os.path.join(basedir, 'search.db')
WHOOSHEE_WRITER_TIMEOUT = 3
# Whoosh does not work on Heroku
WHOOSHEE_ENABLED = os.environ.get('HEROKU') is None

# available languages
LANGUAGES = {
    'en': 'English',
    'fr': 'Français'
}
