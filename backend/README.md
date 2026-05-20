# PawMap Backend

This folder contains the Flask backend for PawMap. The backend is the bridge between the browser and Appwrite, so the frontend never needs to store Appwrite secrets or talk to Appwrite directly.

## What The Backend Does

- Handles register, login, logout, and current-user lookup.
- Stores the Appwrite session secret inside the Flask session cookie.
- Serves public report data to the map.
- Accepts report submissions from the frontend and uploads any attached media.
- Saves the returned file IDs into the Appwrite document so the frontend can load media later.

## Request Flow

The most important flow is the report submission path:

1. The browser sends a `POST /api/animals` request with form fields and files.
2. Flask reads the fields from `request.form` and the files from `request.files`.
3. Flask uploads each file to Appwrite Storage.
4. Flask stores the file IDs and report fields in the Appwrite Database.
5. Flask returns JSON to the frontend.

The map load path is simpler:

1. The frontend calls `GET /api/animals`.
2. Flask uses an admin Appwrite client to fetch all saved reports.
3. Flask flattens the Appwrite document shape so the frontend can read fields like `latitude`, `longitude`, `incident`, `radius`, and `assets` directly.

## Appwrite And Session Notes

- `app.py` uses two Appwrite client styles: an admin client for public reads and a user client for authenticated writes.
- `login_required` checks that the Flask session contains an Appwrite session secret.
- The backend now normalizes Appwrite responses before returning them to the frontend, which keeps the map renderer simple.

## Setup

1. Put a `.env` file in the project root, one level above this folder.
2. Add these values:

   ```ini
   APPWRITE_ENDPOINT=https://cloud.appwrite.io/v1
   APPWRITE_PROJECT_ID=your_project_id
   APPWRITE_API_KEY=your_api_key
   FLASK_SECRET_KEY=generate_a_random_long_string_here
   ```

3. Create and activate a virtual environment, or use the workspace venv at `D:\UNI\Project\.venv`.
4. Install dependencies with the venv interpreter, for example `D:\UNI\Project\.venv\Scripts\python.exe -m pip install -r requirements.txt`.
5. Run `python setup_appwrite.py` once to create the database, collection, and bucket.

## Run The Backend

Start the server from this folder with the same interpreter:

```bash
D:\UNI\Project\.venv\Scripts\python.exe app.py
```

If you prefer to use `python app.py`, make sure the same virtual environment is active in that terminal first.

The app is then available at `http://127.0.0.1:3000`.

## Key Files

- `app.py` - Flask app, routes, and Appwrite communication.
- `setup_appwrite.py` - One-time Appwrite schema bootstrap script.
- `requirements.txt` - Python dependencies.
