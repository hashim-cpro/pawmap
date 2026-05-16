# PawMap Backend

This is the Python Flask backend for the PawMap project. It acts as a secure middleware and proxy between the frontend client and the Appwrite backend-as-a-service.

## Architecture

The backend is built with **Flask** and the **Appwrite Python SDK**.

Instead of exposing all Appwrite functionality and secrets to the frontend, Flask handles:

1. **Authentication:** Receives user credentials, validates them against Appwrite, and securely manages session tokens via an HTTP-only Flask session cookie.
2. **Data Proxying:**
   - Uses an **Admin Client** (with API Key) to fetch public data (like all animal sightings) for unauthenticated visitors.
   - Uses a **User Client** (with Session Secret) to securely proxy user actions (like adding a new sighting) so they are correctly attributed to the logged-in user under Appwrite's permission rules.
3. **Media Uploading:** Receives `multipart/form-data` containing images/videos from the frontend, securely streams them to the Appwrite Storage bucket, stores the returned File IDs in the Appwrite Database document, and returns success to the UI.
4. **Frontend Serving:** Serves the static HTML/CSS/JS files from the frontend directory for a unified local development experience.

## Prerequisites

- Python 3.10+
- An Appwrite Cloud account (or self-hosted instance)

## Setup Instructions

1. **Environment Setup:**
   Create a `.env` file in the root of the project (one level above this folder) using the provided `.env.template`:

   ```ini
   APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
   APPWRITE_PROJECT_ID=your_project_id
   APPWRITE_API_KEY=your_api_key
   FLASK_SECRET_KEY=generate_a_random_long_string_here
   ```

2. **Virtual Environment:**
   Initialize and activate a Python virtual environment:

   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\Activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   Install required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Appwrite Schema:**
   We have provided an automated script to create the necessary Database, Collections, attributes, and Storage bucket for this project.
   ```bash
   python setup_appwrite.py
   ```
   _Note: You only need to run this once!_

## Running the Server

Start the Flask development server:

```bash
python app.py
```

The application (both frontend UI and backend API) will be available at `http://127.0.0.1:3000`.

## Testing

To run the automated backend routes tests using `pytest`:

```bash
pytest test_app.py
```
