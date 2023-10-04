import os
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, session, request
from flask_migrate import Migrate
from models import db, User, App, UserApps
from forms import RegisterUserForm, LoginUserForm
from O365.connection import Connection
from completion import get_completion

from O365 import Account


# Load the environment variables
load_dotenv()

# Create instance of Flask
app = Flask(__name__)

# CONFIGURATIONS
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

db.init_app(app)

migrate = Migrate(app, db)


@app.before_request
def require_login():
    allowed_routes = ['authenticate_user',
                      'register_user', 'home_page', 'dashboard', 'settings', 'delete_user']
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
            return redirect('/dashboard')
        else:
            form.password.errors.append('Invalid email/password.')
    return render_template('login.html', form=form)


@app.route('/dashboard')
def show_dashboard_page():
    '''Show the dashboard page.'''
    user = User.query.get(session['email'])
    apps = App.query.all()
    return render_template('dashboard.html', user=user, apps=apps)


@app.route('/dashboard/add-app/<int:app_id>', methods=['POST'])
def add_app(app_id):
    '''Add an app for the user.'''
    user_app = UserApps(
        user_email=session['email'], app_id=app_id)
    db.session.add(user_app)
    db.session.commit()
    return redirect('/dashboard')


@app.route('/chat')
def show_chat_page():
    '''Show the chat page.'''
    user = User.query.get(session.get('email'))
    return render_template('chat.html', user=user)


@app.route('/chat', methods=['POST'])
def process_chat_input():
    prompt = request.form['prompt']
    completion = get_completion(prompt)
    print(completion)
    return redirect('/chat')


@app.route('/settings')
def show_settings_page():
    '''Show the settings page.'''
    user = User.query.get(session['email'])
    return render_template('settings.html', user=user)


@app.route('/delete-user', methods=['POST'])
def delete_user():
    '''Delete a user.'''
    user = User.query.get(session['email'])
    db.session.delete(user)
    db.session.commit()
    session.pop('email')
    return redirect('/')


@app.route('/logout', methods=['POST'])
def logout_user():
    session.pop('email')
    return redirect('/')


# OUTLOOK FUNCTIONALITY AND ROUTES
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')


required_scopes = ['https://graph.microsoft.com/Mail.Read',
                   'https://graph.microsoft.com/Mail.ReadWrite', 'https://graph.microsoft.com/Mail.Send']


def get_authorization_url():
    con = Connection((CLIENT_ID, CLIENT_SECRET), scopes=required_scopes)
    consent_url, state = con.get_authorization_url(redirect_uri=REDIRECT_URI)

    # Save the state in the session to validate later
    session['oauth_state'] = state

    return consent_url


@app.route('/outlook-login')
def login():
    credentials = (CLIENT_ID, CLIENT_SECRET)
    account = Account(credentials)
    # redirect_uri = url_for('oauth_response', _external=True)
    auth_url = account.authenticate(
        scopes=required_scopes, redirect_uri=REDIRECT_URI)
    if auth_url:
        return redirect(auth_url)
    else:
        return 'Error generating authentication URL.', 500


@app.route('/oauth-response')
def oauth_response():
    token_url = request.url

    credentials = (CLIENT_ID, CLIENT_SECRET)
    account = Account(credentials)
    result = account.con.request_token(token_url, redirect_uri=REDIRECT_URI)

    if result:
        # Store the token in session or elsewhere securely
        session["token"] = account.con.token_backend.token
        flash('Outlook Authentication Successful', 'green')
        return redirect('/chat')
    else:
        flash('Outlook Authentication Failed', 'red')
        return redirect('/dashboard')
