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

    # Relationships
    integrations = db.relationship('Integration', backref='users')

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

    @property
    def full_name(self):
        '''Return the full name of the user.'''
        return f'{self.first_name.title()} {self.last_name.title()}'

    @property
    def initials(self):
        '''Return the initials of the user.'''
        return f'{self.first_name[0]}{self.last_name[0]}'


class Integration(db.Model):
    '''Integration Model'''

    __tablename__ = 'integrations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False, unique=True)
