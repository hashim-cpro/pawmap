import os
import datetime
import urllib.parse
import base64
import json
import requests
from functools import wraps
from flask import Flask, request, jsonify, session, abort, send_from_directory
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.account import Account
from appwrite.services.databases import Databases
from appwrite.exception import AppwriteException
from appwrite.id import ID
from appwrite.query import Query

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__, static_folder="../frontend", static_url_path="/")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-dev-key")

from appwrite.services.storage import Storage
from appwrite.input_file import InputFile

# Appwrite Config
ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")

DATABASE_ID = "pawmap_db"
ANIMALS_COLLECTION_ID = "animals"
BUCKET_ID = "animal_media"

# Initialize Admin Client (for bypassing auth on strict routes if needed)
admin_client = Client()
admin_client.set_endpoint(ENDPOINT)
admin_client.set_project(PROJECT_ID)
if API_KEY:
    admin_client.set_key(API_KEY)
admin_db = Databases(admin_client)


def get_user_client():
    """Initializes an Appwrite client attached to the currently active user session."""
    user_client = Client()
    user_client.set_endpoint(ENDPOINT)
    user_client.set_project(PROJECT_ID)

    session_secret = session.get("appwrite_session")
    if session_secret:
        user_client.set_session(session_secret)
    return user_client


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("appwrite_session"):
            return jsonify({"error": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


# --- Frontend Serving ---
@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route("/api/config", methods=["GET"])
def get_config():
    return jsonify({"endpoint": ENDPOINT, "project_id": PROJECT_ID}), 200


# --- AUTH ROUTES ---
def _login_with_requests(email, password):
    """Helper to bypass Appwrite SDK dropping the secret from response body"""
    url = f"{ENDPOINT}/account/sessions/email"
    headers = {"X-Appwrite-Project": PROJECT_ID}
    r = requests.post(url, json={"email": email, "password": password}, headers=headers)
    if r.status_code == 201:
        cookie_val = r.cookies.get(f"a_session_{PROJECT_ID}")
        if cookie_val:
            return cookie_val, r.json().get("userId")
    raise AppwriteException(r.json().get("message", "Login failed"), r.status_code)


@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "")

    user_client = Client()
    user_client.set_endpoint(ENDPOINT)
    user_client.set_project(PROJECT_ID)
    account = Account(user_client)

    try:
        user = account.create(ID.unique(), email, password, name)
        # Automatic login after registration
        secret, user_id = _login_with_requests(email, password)
        session["appwrite_session"] = secret
        session["user_id"] = user_id

        user_data = user.to_dict() if hasattr(user, "to_dict") else user
        return jsonify({"message": "Registration successful", "user": user_data}), 201
    except AppwriteException as e:
        return jsonify({"error": str(e)}), getattr(e, "code", 400)


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    try:
        secret, user_id = _login_with_requests(email, password)
        session["appwrite_session"] = secret
        session["user_id"] = user_id
        return jsonify({"message": "Login successful"}), 200
    except AppwriteException as e:
        return jsonify({"error": str(e)}), getattr(e, "code", 400)


@app.route("/api/auth/logout", methods=["POST"])
@login_required
def logout():
    user_client = get_user_client()
    account = Account(user_client)
    try:
        account.delete_session("current")
        session.clear()
        return jsonify({"message": "Logged out"}), 200
    except AppwriteException as e:
        session.clear()
        return jsonify({"error": str(e)}), e.code


@app.route("/api/auth/me", methods=["GET"])
@login_required
def get_me():
    user_client = get_user_client()
    account = Account(user_client)
    try:
        user = account.get()
        user_data = user.to_dict() if hasattr(user, "to_dict") else user
        return jsonify({"user": user_data}), 200
    except AppwriteException as e:
        session.clear()
        return jsonify({"error": str(e)}), e.code


# --- ANIMALS ROUTES ---
@app.route("/api/animals", methods=["GET"])
def get_animals():
    try:
        # Fetching all animals can be done via admin client so anonymous users can see map
        response = admin_db.list_documents(
            DATABASE_ID, ANIMALS_COLLECTION_ID, queries=[Query.order_desc("created_at")]
        )
        # In Appwrite SDK 18.x+, response is an object, so we convert documents to dicts for JSON
        documents = [
            doc.to_dict() if hasattr(doc, "to_dict") else doc
            for doc in response.documents
        ]
        return jsonify(documents), 200
    except AppwriteException as e:
        return jsonify({"error": str(e)}), e.code


@app.route("/api/animals/<animal_id>", methods=["GET"])
def get_animal(animal_id):
    try:
        response = admin_db.get_document(DATABASE_ID, ANIMALS_COLLECTION_ID, animal_id)
        # Convert model object to dict
        doc_data = response.to_dict() if hasattr(response, "to_dict") else response
        return jsonify(doc_data), 200
    except AppwriteException as e:
        return jsonify({"error": str(e)}), e.code


@app.route("/api/animals", methods=["POST"])
@login_required
def create_animal():
    data = dict(request.form)
    data["created_at"] = datetime.datetime.utcnow().isoformat()
    files = request.files.getlist("media")

    # Cast variables properly based on appwrite schema
    if "latitude" in data:
        data["latitude"] = float(data["latitude"])
    if "longitude" in data:
        data["longitude"] = float(data["longitude"])
    if "radius" in data:
        data["radius"] = int(data["radius"])

    user_client = get_user_client()
    user_db = Databases(user_client)
    user_storage = Storage(user_client)

    try:
        asset_ids = []
        for file in files:
            # Save file to a temporary location to pass to InputFile.from_path
            temp_path = (
                os.path.join("/tmp", file.filename)
                if os.name != "nt"
                else os.path.join(os.environ.get("TEMP", "C:\\temp"), file.filename)
            )
            file.save(temp_path)

            uploaded_file = user_storage.create_file(
                BUCKET_ID, ID.unique(), InputFile.from_path(temp_path)
            )
            asset_ids.append(uploaded_file["$id"])
            os.remove(temp_path)

        data["assets"] = asset_ids

        response = user_db.create_document(
            DATABASE_ID, ANIMALS_COLLECTION_ID, ID.unique(), data
        )
        doc_data = response.to_dict() if hasattr(response, "to_dict") else response
        return jsonify(doc_data), 201
    except AppwriteException as e:
        return jsonify({"error": str(e)}), e.code


if __name__ == "__main__":
    app.run(debug=True, port=3000)
