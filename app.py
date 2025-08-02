from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from functools import wraps
from werkzeug.security import check_password_hash
import os
import logging

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)

# Configurations
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
    raise ValueError("ADMIN_USERNAME and ADMIN_PASSWORD_HASH must be set in the environment variables.")
print("USERNAME from .env:", ADMIN_USERNAME)
print("HASH from .env:", ADMIN_PASSWORD_HASH)

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
db = SQLAlchemy(app)

# DB Model
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    tech = db.Column(db.PickleType, nullable=False)
    link = db.Column(db.String(255), nullable=False)

# Create DB
with app.app_context():
    db.create_all()

# Routes
@app.route("/projects", methods=["GET"])
def get_projects():
    try:
        projects = Project.query.all()
        return jsonify([
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "tech": p.tech,
                "link": p.link
            } for p in projects
        ]), 200
    except Exception as e:
        logging.error("Error loading projects: %s", e)
        return jsonify({"error": "Failed to load projects"}), 500

@app.route("/projects", methods=["POST"])
def add_project():
    try:
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
    except Exception as e:
        logging.error("Error adding project: %s", e)
        return jsonify({"error": "Failed to add project"}), 500

@app.route("/projects/<int:project_id>", methods=["DELETE"])
@require_auth
def delete_project(project_id):
    project = Project.query.get(project_id)
    if project is None:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": "Project deleted"}), 200

@app.route("/contact", methods=["POST"])
def contact():
    try:
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
    except Exception as e:
        logging.error("Error sending email: %s", e)
        return jsonify({"error": "Failed to send email"}), 500

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
