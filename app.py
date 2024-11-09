from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import random
from datetime import datetime
from database import register_new_user  # Import the user registration function

app = Flask(__name__)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model for SQLite DB
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Create session and handle user session data
def create_session(user):
    session_id = random.randint(10000, 99999)
    session["session_id"] = session_id
    session["user_id"] = user.id
    session["session_counter"] = session.get("session_counter", 0) + 1

    session_data = {
        "Session_ID": session_id,
        "USER_ID": user.id,
        "Start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "LLM": "Welcome to the session!",
        "counter": session["session_counter"],
        "End_time": None,
    }

    return session_data


# Home route (index page)
@app.route('/')
def index():
    return render_template('index.html')

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please log in.')
            return redirect(url_for('index'))

        # Hash the password and create a new user in SQLite
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        # Create a session for the new user
        session_data = create_session(new_user)
        session_id = session_data["Session_ID"]

        # Register user in SQLite using the database.py function
        register_new_user(session_id, new_user)

        flash('Registration successful! Please log in.')
        return redirect(url_for('index'))

    return render_template('index.html')


# User login and session creation
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session_data = create_session(user)
        flash(f"Welcome {user.name}! Session started.")
        return redirect(url_for('coming_soon', session_id=session_data["Session_ID"]))
    else:
        flash('Invalid email or password. Please try again.')
        return redirect(url_for('index'))

@app.route('/coming_soon')
def coming_soon():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('index'))
    return render_template('coming_soon.html')

# Initialize the SQLite database
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
