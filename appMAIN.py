from database import Flask, request, redirect, url_for, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
import secrets

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///use rs.db'

# Initialize SQLAlchemy with app context
db = SQLAlchemy(app)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    
    # Check if the user already exists
    existing_user = UserData.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already registered. Please log in.")
        return redirect(url_for('index'))
    
    # Create new user
    new_user = UserData(name=name, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    flash("Registration successful!")
    return redirect(url_for('coming_soon'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = UserData.query.filter_by(email=email, password=password).first()
    
    if user:
        session['user_id'] = user.id
        session['user_name'] = user.name
        flash("Login successful!")
        return redirect(url_for('coming_soon'))
    else:
        flash("Invalid credentials, please try again.")
        return redirect(url_for('index'))

@app.route('/coming-soon')
def coming_soon():
    return render_template('coming_soon.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Initialize the database before running the app
    app.run(debug=True)