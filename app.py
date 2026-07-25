import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'replace_with_a_super_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///leaddesk.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- AUTHENTICATION SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "error"

# --- DATA MODELS ---
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='New')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

# Create tables and a default admin user
with app.app_context():
    db.create_all()
    # Check if admin exists, if not, create it
    if not Admin.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('DigitalHeroes2026', method='pbkdf2:sha256')
        default_admin = Admin(username='admin', password_hash=hashed_pw)
        db.session.add(default_admin)
        db.session.commit()

# --- ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        budget = request.form.get('budget')
        message = request.form.get('message')

        if not name or not email or '@' not in email or not budget or not message:
            flash("Please provide valid information for all fields.", "error")
            return redirect(url_for('index'))

        new_lead = Lead(name=name, email=email, budget=budget, message=message)
        db.session.add(new_lead)
        db.session.commit()
        
        flash("Thank you! Your message has been received.", "success")
        return redirect(url_for('index'))
        
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Admin.query.filter_by(username=username).first()
        # Verify user exists and password hash matches
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/admin')
@login_required
def admin():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template('admin.html', leads=leads)

@app.route('/update_status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    lead = Lead.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['New', 'Contacted', 'Closed']:
        lead.status = new_status
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)