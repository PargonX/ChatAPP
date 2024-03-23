from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

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
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return render_template('login.html', error='Invalid username or password.')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/chat')
def chat():
    if 'username' in session:
        messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
        return render_template('chat.html', messages=messages)
    else:
        return redirect(url_for('login'))

@app.route('/external-chat', methods=['POST'])
def external_chat():
    # Retrieve username and message from request data
    data = request.json
    username = data.get('username')
    message = data.get('message')
    if username and message:
        sender = username
        chat_message = ChatMessage(sender=sender, content=message)
        db.session.add(chat_message)
        db.session.commit()
        socketio.emit('message', {'sender': sender, 'content': message}, broadcast=True)
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid data format'}), 400

@app.route('/clear_chat', methods=['GET'])
def clear_chat():
    if request.method == 'GET':
        # Clear all chat messages
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
