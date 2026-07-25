import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'replace_with_a_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///leaddesk.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Updated Data Model with created_at timestamp
class Lead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='New')
    created_at = db.Column(db.DateTime, default=datetime.utcnow) # NEW COLUMN

# Create tables
with app.app_context():
    db.create_all()

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

@app.route('/admin')
def admin():
    # UPDATED: Now orders by the exact time created, newest first
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return render_template('admin.html', leads=leads)

@app.route('/update_status/<int:id>', methods=['POST'])
def update_status(id):
    lead = Lead.query.get_or_404(id)
    new_status = request.form.get('status')
    if new_status in ['New', 'Contacted', 'Closed']:
        lead.status = new_status
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)