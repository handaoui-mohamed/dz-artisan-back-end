# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators, FloatField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length
from app.user.models import User


class UserForm(FlaskForm):
    username = StringField('username',validators=[
        DataRequired('Le nom d\'utilisateur est nécessaire'), 
        Length(min=1,max=32,message="Le nom d\'utilisateur doit être > 1 et < 32 caractères")
    ])
    email = EmailField('email', [
        validators.DataRequired('L\'addresse Email est nécessaire'), 
        validators.Email('L\'addresse Email doit être valide')
    ])
    password = PasswordField('password', validators=[
        Length(min=8,message="Le nom mot de passe doit être > 8 caractères"), 
        DataRequired('Le mot de passe est nécessaire')
    ])
    address = StringField('address', validators=[
        Length(max=200,message="L\'addresse doit être < 200 caractères")
    ])
    full_name = StringField('full_name', validators=[
        Length(max=100,message="Le nom et prénom doivent être < 100 caractères")
    ])
    phone_number = StringField('phone_number', validators=[
        Length(max=14,message="Le numéro téléphone doit être < 14 numéro")
    ])
    description = StringField('description', validators=[
        Length(max=1000,message="La description doit être < 1000 caractères")
    ])
    latitude = FloatField('latitude')
    longitude = FloatField('longitude')