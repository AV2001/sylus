from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


class User(db.Model):
    '''User Model'''

    __tablename__ = 'users'

    email = db.Column(db.Text, primary_key=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    password = db.Column(db.Text, nullable=False)

    @classmethod
    def register(cls, email, first_name, last_name, password):
        '''Register user with hashed password and return the user'''
        hashed_password = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed_password.decode('utf-8')
        return cls(email=email, first_name=first_name, last_name=last_name, password=hashed_utf8)

    @classmethod
    def authenticate(cls, email, password):
        '''Validate that user exists and password is correct. Return the user if both conditions are true.'''
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False
