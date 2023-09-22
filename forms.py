from flask_wtf import FlaskForm
from wtforms.fields import StringField, EmailField, PasswordField
from wtforms.validators import InputRequired


class RegisterUserForm(FlaskForm):
    '''Register User Form'''

    first_name = StringField('First Name', validators=[InputRequired()])
    last_name = StringField('Last Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
