# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, TextAreaField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length
from .models import User

class UserForm(Form):
    nickname = StringField('nickname', validators=[DataRequired()])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=150)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return False

        if self.nickname.data == self.original_nickname:
            return True

        user = User.query.filter_by(nickname=self.nickname.data).first()

        if user != None:
            self.nickname.errors.append('This nickname is already in use. Please choose another one.')
            return False
        return True