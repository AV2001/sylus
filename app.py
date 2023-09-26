import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, session, request
from models import db, User, Integration
from forms import RegisterUserForm, LoginUserForm

# Load the environment variables
load_dotenv()

# Create instance of Flask
app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)


@app.before_request
def require_login():
    allowed_routes = ['authenticate_user',
                      'register_user', 'home_page', 'dashbord']
    if request.endpoint not in allowed_routes and 'email' not in session and 'static' not in request.endpoint:
        return redirect('/')


@app.before_request
def prevent_logged_in_user_access():
    logged_in_routes = ['authenticate_user',
                        'register_user', 'home_page', 'dashboard']
    if 'email' in session and request.endpoint in logged_in_routes:
        return redirect('/chat')


# ROUTES
@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register_user():
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
    form = LoginUserForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.authenticate(email=email, password=password)
        if user:
            session['email'] = user.email
            return redirect('/chat')
        else:
            form.password.errors.append('Invalid email/password.')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def show_dashboard_page():
    '''Show the dashboard page.'''
    user = User.query.get(session['email'])
    integrations = Integration.query.all()
    return render_template('dashboard.html', user=user, integrations=integrations)


@app.route('/chat')
def show_chat_page():
    '''Show the chat page.'''
    user = User.query.get(session['email'])
    return render_template('chat.html', user=user)


@app.route('/logout', methods=['POST'])
def logout_user():
    session.pop('email')
    return redirect('/')
