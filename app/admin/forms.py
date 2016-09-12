#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from flask_wtf import Form
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import Required, Email, EqualTo, Length, IPAddress
from wtforms import ValidationError
from ..models import User, Userlog

class CreateUserForm(Form):
    name = StringField("Username:", validators = [Required(), Length(1, 32)])
    password = StringField("Password:", validators = [Required(), Length(1, 8)])
    expired = SelectField("Expired:", choices=[('3d','3 days'), ('1m', '1 month'), ('3m', '3 months'), ('6m', '6 months'), ('1y', '1 year')],
                   validators=[Required()])
    checkout = StringField("Checkout day:", validators=[Required()])
    package  = SelectField("Package:", choices=[], validators=[Required()])
    submit = SubmitField("CreateUser")


