from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User Roles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # student, reviewer, committee, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Scholarship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    eligibility_criteria = db.Column(db.Text)
    application_deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    documents_required = db.Column(db.Text)  # comma-separated list

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarship.id'), nullable=False)
    documents = db.Column(db.Text)  # store file paths comma-separated
    status = db.Column(db.String(50), default="Pending")  # Pending, Reviewed, Accepted, Rejected
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviews = db.relationship('Review', backref='application', lazy=True)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Float)
    comments = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
