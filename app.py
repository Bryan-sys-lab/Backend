# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from dotenv import load_dotenv
from functools import wraps
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
import os
import logging

from models import db, Project, Experience, Education

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

# Config
app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///projects.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER"),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL") == "True",
)

# Logging
logging.basicConfig(level=logging.INFO)

# Auth
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD_HASH must be set in .env")

def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or auth.username != ADMIN_USERNAME or not check_password_hash(ADMIN_PASSWORD_HASH, auth.password):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# Init extensions
mail = Mail(app)
db.init_app(app)
migrate = Migrate(app, db)

# ----------- Routes -----------

@app.route("/projects", methods=["GET"])
def get_projects():
    projects = Project.query.all()
    return jsonify([{
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "tech": p.tech,
        "link": p.link
    } for p in projects]), 200

@app.route("/projects", methods=["POST"])
def add_project():
    data = request.get_json()
    new_project = Project(
        name=data["name"],
        description=data["description"],
        tech=data["tech"],
        link=data["link"]
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"status": "Project added"}), 201

@app.route("/projects/<int:project_id>", methods=["DELETE"])
@require_auth
def delete_project(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200

@app.route("/experience", methods=["GET"])
def get_experience():
    experience = Experience.query.all()
    return jsonify([{
        "id": e.id,
        "title": e.title,
        "company": e.company,
        "location": e.location,
        "start": e.start,
        "end": e.end,
        "description": e.description
    } for e in experience]), 200

@app.route("/experience", methods=["POST"])
@require_auth
def add_experience():
    data = request.get_json()
    exp = Experience(
        title=data["title"],
        company=data["company"],
        location=data.get("location"),
        start=data["start"],
        end=data.get("end"),
        description=data.get("description")
    )
    db.session.add(exp)
    db.session.commit()
    return jsonify({"id": exp.id}), 201

@app.route("/experience/<int:exp_id>", methods=["DELETE"])
@require_auth
def delete_experience(exp_id):
    exp = Experience.query.get(exp_id)
    if not exp:
        return jsonify({"error": "Experience not found"}), 404
    db.session.delete(exp)
    db.session.commit()
    return jsonify({"message": "Experience deleted"}), 200

@app.route("/education", methods=["GET"])
def get_education():
    education = Education.query.all()
    return jsonify([{
        "id": e.id,
        "degree": e.degree,
        "institution": e.institution,
        "start": e.start,
        "end": e.end,
        "description": e.description
    } for e in education]), 200

@app.route("/education", methods=["POST"])
@require_auth
def add_education():
    data = request.get_json()
    edu = Education(
        degree=data["degree"],
        institution=data["institution"],
        start=data["start"],
        end=data.get("end"),
        description=data.get("description")
    )
    db.session.add(edu)
    db.session.commit()
    return jsonify({"id": edu.id}), 201

@app.route("/education/<int:edu_id>", methods=["DELETE"])
@require_auth
def delete_education(edu_id):
    edu = Education.query.get(edu_id)
    if not edu:
        return jsonify({"error": "Education not found"}), 404
    db.session.delete(edu)
    db.session.commit()
    return jsonify({"message": "Education deleted"}), 200

@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json() if request.is_json else request.form
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")
    if not name or not email or not message:
        return jsonify({"error": "All fields are required"}), 400
    msg = Message(
        subject="New Contact from Portfolio",
        recipients=[os.getenv("MAIL_USERNAME")],
        body=f"From: {name} <{email}>\n\n{message}"
    )
    mail.send(msg)
    return jsonify({"status": "Message sent"}), 200

@app.route("/api/welcome")
def welcome():
    return {"message": "Welcome to my portfolio!"}

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
