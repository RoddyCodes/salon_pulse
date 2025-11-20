from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. App Configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///salon_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 2. Database Schema (The Tables)

class Technician(db.Model):
    """Stores employee info and commission rates."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    commission_rate = db.Column(db.Float, default=0.60) 
    appointments = db.relationship('Appointment', backref='technician', lazy=True)

class Service(db.Model):
    """Stores the salon menu items."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50)) 
    appointments = db.relationship('Appointment', backref='service', lazy=True)

class Customer(db.Model):
    """Stores client details."""
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    notes = db.Column(db.Text)
    appointments = db.relationship('Appointment', backref='customer', lazy=True)

class Appointment(db.Model):
    """The central ledger of all transactions."""
    id = db.Column(db.Integer, primary_key=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey('technician.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    
    # Financials
    price_charged = db.Column(db.Float, nullable=False) 
    tip_amount = db.Column(db.Float, default=0.0)
    payment_method = db.Column(db.String(20)) 

# 3. Initialization
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")