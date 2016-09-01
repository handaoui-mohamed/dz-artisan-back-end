# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length

class UserForm(Form):
    username = StringField('username', validators=[DataRequired()])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=150)])
