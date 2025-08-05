from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    tech = db.Column(db.PickleType)
    link = db.Column(db.String(255))
    image = db.Column(db.String(255))

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120))
    start = db.Column(db.String(20), nullable=False)
    end = db.Column(db.String(20))
    description = db.Column(db.Text)

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    degree = db.Column(db.String(120), nullable=False)
    institution = db.Column(db.String(120), nullable=False)
    start = db.Column(db.String(20), nullable=False)
    end = db.Column(db.String(20))
    description = db.Column(db.Text)
