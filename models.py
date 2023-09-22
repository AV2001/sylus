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
