# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, BooleanField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

class LoginForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    remember_me = BooleanField('remember_me', default=False)