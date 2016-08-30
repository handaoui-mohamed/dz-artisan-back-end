#!flask/bin/python
from app import app
from flask_whooshee import Whooshee

w = Whooshee(app)
w.reindex()