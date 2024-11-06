from database import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import random
import json
import os
from datetime import datetime

app = Flask(__name__)

# Set up your database URI (for SQLite in this case)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use the correct path to your database
app.config['SECRET_KEY'] = 'your_secret_key'  # Needed for flash messages
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking

# Initialize the database
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Temporary storage file for conversations
def save_conversation(session_id, conversation_data):
    file_path = f"conversations/{session_id}.json"
    # Ensure directory exists
    if not os.path.exists("conversations"):
        os.makedirs("conversations")
    with open(file_path, 'w') as f:
        json.dump(conversation_data, f)

# Function to create and store session info
import random
from datetime import datetime

def create_session(user):
    session_id = random.randint(10000, 99999)  # Generate a 5-digit session ID
    session["session_id"] = session_id
    session["user_id"] = user.id
    session["session_counter"] = session.get("session_counter", 0) + 1  # Increase session counter

    # Create session data
    session_data = {
        "Session_ID": session_id,
        "USER_ID": user.id,
        "Start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "LLM": "Welcome to the session!",
        "counter": session["session_counter"],
        "End_time": None,
    }

    # Store session data in a file or database if needed
    save_conversation(session_id, session_data)

    # Return session_data so it can be used later
    return session_data

@app.route('/')
def index():
    return render_template('index.html')

# Route for handling registration
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Check if the email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already registered. Please log in.')
        return redirect(url_for('index'))

    # Create a new user with hashed password
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(name=name, email=email, password=hashed_password)

    # Add and commit the new user to the database
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful. Please log in.')
    return redirect(url_for('index'))

# Route for handling login
@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        session_data = create_session(user)
        flash(f"Welcome {user.name}! Session started.")
        return redirect(url_for('coming_soon', session_id=session_data["Session_ID"])), user
    else:
        flash('Invalid email or password. Please try again.')
        return redirect(url_for('index'))

    

# Route for coming soon page
@app.route('/coming_soon')
def coming_soon():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('index'))
    return render_template('coming_soon.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('session_id', None)
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create all tables if they don't already exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
