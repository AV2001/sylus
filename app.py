import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, session
from models import db, User
from forms import RegisterUserForm, LoginUserForm

# Load the enrivonment variables
load_dotenv()

# Create instance of Flask
app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# ROUTES
@app.route('/')
def home_page():
    if 'email' in session:
        return redirect('/dashboard')
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
    '''Register a user.'''
    form = RegisterUserForm()
    if form.validate_on_submit():
        first_name = form.first_name.data.title()
        last_name = form.last_name.data.title()
        email = form.email.data.lower()
        password = form.password.data
        new_user = User.register(
            first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Login below.', 'green')
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def authenticate_user():
    '''Authenticate a user.'''
    form = LoginUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.authenticate(email=email, password=password)
        if user:
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            form.password.errors.append('Invalid email/password.')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def show_dashbord():
    '''Show dashboard page.'''
    user = User.query.get(session['email'])
    return render_template('dashboard.html', user=user)


@app.route('/logout', methods=['POST'])
def logout_user():
    '''Logout user.'''
    session.pop('email')
    return redirect('/')
