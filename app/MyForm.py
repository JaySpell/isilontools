__author__ = 'jspell'
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField,
    validators, BooleanField, RadioField, PasswordField, IntegerField)
from wtforms.validators import (DataRequired, Required,
    Regexp, Length, NumberRange, InputRequired, Optional)

class MyForm(FlaskForm):
    #name = StringField('name'),
    cust_fname = StringField('cfname',
        validators=[
            InputRequired(message="Enter customer first name..",),
            Regexp(
                r'^[a-zA-Z]+$',
                message=("Customer name should contain only letters..."))
        ])
    cust_lname = StringField('lname',
        validators=[
            InputRequired(message="Enter customer last name..."),
            Regexp(
                r'^[a-zA-Z\s\-]+$',
                message=("Customer name should contain only letters..."))
        ])
    space_add = IntegerField('aspace',
        validators=[
            NumberRange(min=0, max=500,
                message=("Can add space up to 500GB...")
            ),
            Optional()
        ])
    cost_center = StringField('ccenter',
        validators=[
            InputRequired(message="Cost center required..."),
            Regexp(
                r'^[0-9]+$',
                message=("Cost center should be numbers only..."))
        ])
    work_order = StringField('worder',
        validators=[
            InputRequired(message="Please enter a work order..."),
            Regexp(
                r'^[Ww]{1}[Oo]{1}\d+',
                message=("Please enter valid work order.. WO0000111..."))
        ])

class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_.]+$',
                message=("Username should be one word, letters, numbers"
                        " and underscores only.")
                )
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired(),
            Length(min=6),
        ])

class QuotaForm(FlaskForm):
    name = StringField('name',
        validators=[
            DataRequired(message='Must enter at least 4 characters...'),
            Length(min=4),
        ])

class RadioForm(FlaskForm):
    itemid = RadioField(validators=[DataRequired()])
