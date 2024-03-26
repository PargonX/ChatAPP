from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, BadSignature
import yaml

# Define the base URL for the application
app_base_url = 'http://example.com'  # Change example.com to your actual domain name or IP address

app = Flask(__name__)

# Load configuration from config.yml
with open('config.yml', 'r') as config_file:
    config_data = yaml.safe_load(config_file)

# Update Flask application configuration
for key, value in config_data.items():
    app.config[key] = value

db = SQLAlchemy(app)
socketio = SocketIO(app)
mail = Mail(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        # Check if the input is an email
        if '@' in username_or_email:
            user = User.query.filter_by(email=username_or_email).first()
        else:
            user = User.query.filter_by(username=username_or_email).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')) and user.email_verified:
            session['username'] = user.username
            return redirect(url_for('chat'))
        elif user and not user.email_verified:
            return render_template('login.html', error='Please verify your email before logging in.')
        else:
            return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(username=username, password=hashed_password, email=email, email_verified=False)
        db.session.add(new_user)
        db.session.commit()

        serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='email-verification')

        msg = Message('Email Verification', sender='pargon@vonix.network', recipients=[email])
        verification_url = f'{app_base_url}{url_for("verify_email", token=token)}'
        msg.body = f'Click the following link to verify your email: {verification_url}'
        mail.send(msg)

        flash('Registration successful! Please check your email to confirm your registration.', 'success')

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/verify_email/<token>')
def verify_email(token):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_verified = True
            db.session.commit()
            flash('Email verification successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Invalid token. Please try again.', 'error')
            return redirect(url_for('login'))
    except BadSignature:
        flash('Invalid or expired token. Please request a new verification email.', 'error')
        return redirect(url_for('login'))

@app.route('/chat')
def chat():
    if 'username' in session:
        messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
        return render_template('chat.html', messages=messages)
    else:
        return redirect(url_for('login'))

@app.route('/clear_chat', methods=['GET'])
def clear_chat():
    if request.method == 'GET':
        ChatMessage.query.delete()
        db.session.commit()
        return redirect(url_for('chat'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@socketio.on('message')
def handle_message(message):
    sender = session.get('username', 'Anonymous')
    chat_message = ChatMessage(sender=sender, content=message)
    db.session.add(chat_message)
    db.session.commit()
    emit('message', {'sender': sender, 'content': message}, broadcast=True)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
