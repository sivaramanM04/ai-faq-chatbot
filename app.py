from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import redirect
from flask import url_for

from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv

import google.generativeai as genai

import os

# =========================================
# LOAD ENV
# =========================================

load_dotenv()

# =========================================
# FLASK APP
# =========================================

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv(
    'SECRET_KEY'
)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL'
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# =========================================
# DATABASE
# =========================================

db = SQLAlchemy(app)

# =========================================
# GOOGLE OAUTH
# =========================================

oauth = OAuth(app)

google = oauth.register(

    name='google',

    client_id=os.getenv(
        "GOOGLE_CLIENT_ID"
    ),

    client_secret=os.getenv(
        "GOOGLE_CLIENT_SECRET"
    ),

    server_metadata_url=
    'https://accounts.google.com/.well-known/openid-configuration',

    client_kwargs={
        'scope': 'openid email profile'
    }

)

# =========================================
# LOGIN MANAGER
# =========================================

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# =========================================
# GEMINI CONFIG
# =========================================

genai.configure(

    api_key=os.getenv(
        'GEMINI_API_KEY'
    )

)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# =========================================
# DATABASE MODELS
# =========================================

class User(UserMixin, db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(200),
        nullable=False
    )

# =========================================

class ChatHistory(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        nullable=False
    )

    domain = db.Column(
        db.String(100)
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    response = db.Column(
        db.Text,
        nullable=False
    )

# =========================================
# USER LOADER
# =========================================

@login_manager.user_loader
def load_user(user_id):

    return User.query.get(
        int(user_id)
    )

# =========================================
# HOME ROUTE
# =========================================

@app.route('/')
def home():

    if current_user.is_authenticated:

        return redirect(
            url_for('chatbot')
        )

    return redirect(
        url_for('login')
    )

# =========================================
# REGISTER
# =========================================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        email = request.form['email']

        password = request.form['password']

        # CHECK EXISTING USER

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            return "Email already exists"

        # HASH PASSWORD

        hashed_password = generate_password_hash(
            password
        )

        # CREATE USER

        new_user = User(

            username=username,

            email=email,

            password=hashed_password

        )

        db.session.add(new_user)

        db.session.commit()

        return redirect(
            url_for('login')
        )

    return render_template(
        'register.html'
    )

# =========================================
# LOGIN
# =========================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        # FIND USER

        user = User.query.filter_by(
            email=email
        ).first()

        # CHECK PASSWORD

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for('chatbot')
            )

        else:

            return "Invalid Email or Password"

    return render_template(
        'login.html'
    )

# =========================================
# GOOGLE LOGIN
# =========================================

@app.route('/google-login')
def google_login():

    redirect_uri = url_for(
        'google_authorize',
        _external=True
    )

    return google.authorize_redirect(
        redirect_uri
    )

# =========================================
# GOOGLE AUTHORIZE
# =========================================

@app.route('/google-authorize')
def google_authorize():

    token = google.authorize_access_token()

    user_info = token['userinfo']

    email = user_info['email']

    username = user_info['name']

    # CHECK USER EXISTS

    user = User.query.filter_by(
        email=email
    ).first()

    # CREATE USER IF NOT EXISTS

    if not user:

        user = User(

            username=username,

            email=email,

            password=generate_password_hash(
                "google-login"
            )

        )

        db.session.add(user)

        db.session.commit()

    # LOGIN USER

    login_user(user)

    return redirect(
        url_for('chatbot')
    )

# =========================================
# LOGOUT
# =========================================

@app.route('/logout')
@login_required
def logout():

    logout_user()

    return redirect(
        url_for('login')
    )

# =========================================
# CHATBOT PAGE
# =========================================

@app.route('/chatbot')
@login_required
def chatbot():

    chats = ChatHistory.query.filter_by(
        user_id=current_user.id
    ).order_by(
        ChatHistory.id.desc()
    ).all()

    return render_template(

        'index.html',

        username=current_user.username,

        chats=chats

    )

# =========================================
# CHAT API
# =========================================

@app.route('/chat', methods=['POST'])
@login_required
def chat():

    data = request.get_json()

    user_message = data['message']

    domain = data['domain']

    try:

        prompt = f"""
        You are an AI assistant for {domain}.

        Answer only related to {domain}.

        Keep answers simple,
        professional,
        and accurate.

        User Question:
        {user_message}
        """

        response = model.generate_content(
            prompt
        )

        bot_reply = response.text

    except Exception as e:

        bot_reply = str(e)

        print(e)

    # SAVE CHAT

    new_chat = ChatHistory(

        user_id=current_user.id,

        domain=domain,

        message=user_message,

        response=bot_reply

    )

    db.session.add(new_chat)

    db.session.commit()

    return jsonify({

        'response': bot_reply

    })

# =========================================
# CREATE DATABASE
# =========================================

with app.app_context():

    db.create_all()

# =========================================
# RUN APP
# =========================================

if __name__ == '__main__':

    app.run(
        debug=True
    )