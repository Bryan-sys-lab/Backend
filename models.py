from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Project model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech = db.Column(db.PickleType, nullable=False)  # List of technologies
    link = db.Column(db.String(255), nullable=False)

# Experience model
class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120))
    start = db.Column(db.String(20), nullable=False)  # e.g., "Jan 2022"
    end = db.Column(db.String(20))  # e.g., "Present" or "Dec 2023"
    description = db.Column(db.Text)

# Education model
class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(120), nullable=False)
    institution = db.Column(db.String(120), nullable=False)
    start = db.Column(db.String(20), nullable=False)
    end = db.Column(db.String(20))
    description = db.Column(db.Text)
