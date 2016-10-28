# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, validators
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Length


class ContactForm(FlaskForm):
    user_name = StringField('user_name',validators=[
        DataRequired('Votre Nom et Prénom sont nécessaires')
    ])
    email = EmailField('email', [
        validators.DataRequired('L\'addresse Email est nécessaire'),
        validators.Email('L\'addresse Email doit être valide')
    ])
    phone_number = StringField('phone_number', validators=[
        validators.DataRequired('Le numéro de téléphone est nécessaire'),
        Length(max=14, message="Le numéro téléphone doit être < 14 numéro")
    ])
    body = StringField('body', validators=[
        validators.DataRequired('Le message est nécessaire !!'),
        Length(max=1000, message="Le message doit être < 1000 caractères")
    ])
