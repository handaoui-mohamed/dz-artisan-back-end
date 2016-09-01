# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField, validators, PasswordField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class UserForm(Form):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    full_name = StringField('full_name', validators=[DataRequired()])
    email = EmailField('email', [validators.DataRequired(), validators.Email()])
    address = StringField('address')
    phone_number = StringField('phone_number', validators=[DataRequired()])
    description = TextAreaField('about_me', validators=[Length(min=0, max=300)])
