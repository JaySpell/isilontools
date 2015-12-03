__author__ = 'jspell'
from flask_wtf import Form
from wtforms import (StringField, SelectField,
    validators, BooleanField, RadioField, PasswordField)
from wtforms.validators import DataRequired, Required, Regexp, Length

class MyForm(Form):
    name = StringField('name', validators=[DataRequired()])
    size_in_gb = StringField('size', validators=[DataRequired()])
    itemid = RadioField(validators=[DataRequired()])
    cust_fname = StringField('cfname',
        validators=[
            DataRequired(message="Enter customer first name..",),
            Regexp(
                r'^[a-zA-Z]+$',
                message=("Customer name should contain only letters..."))
        ])
    cust_lname = StringField('lname',
        validators=[DataRequired(message="Enter customer last name...")])
    cost_center = StringField('ccenter',
        validators=[DataRequired(message="Cost center required...")])

class LoginForm(Form):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message=("Username should be one word, letters, numbers"
                        "and underscores only.")
                )
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6),
        ])

