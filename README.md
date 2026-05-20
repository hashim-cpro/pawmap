# PawMap

PawMap is a lost-and-found animal reporting app. The project has two layers:

- A Flask backend that talks to Appwrite, handles login sessions, stores reports, and uploads media.
- A vanilla frontend made with HTML, CSS, and JavaScript that renders the map, draws report pins and circles, and sends form submissions to the backend.

If you know basic HTML, CSS, JavaScript, and Python, this README explains how the pieces fit together without assuming Flask or Appwrite experience.

## How The App Works

1. The browser opens the frontend page and loads the map.
2. The frontend JavaScript checks whether the user is logged in by calling the backend.
3. When the user submits a report, the browser sends a `multipart/form-data` request to the Flask backend.
4. Flask forwards that data to Appwrite, uploads the media files, and saves the report document.
5. The map reads saved reports back from the backend and draws a custom pin plus a radius circle for each one.
6. Clicking a pin or circle opens a popup with the report details and media.

## Project Structure

- `backend/` - Flask app, Appwrite integration, API routes, and session handling.
- `frontend/` - Vanilla HTML/CSS/JS map UI.
- `dbsetup.sql` - Original database schema reference from the older version.
- `pawmap/` - The older reference implementation.
- This repository root is `pawmap_remaped`.

## Quick Start

1. Create a `.env` file in the project root, next to `backend/`.
2. Fill it with the Appwrite and Flask values expected by the backend.
3. Install the Python dependencies inside a virtual environment.
4. Run the backend from `backend/`.
5. Open the app in the browser at `http://127.0.0.1:3000`.

## Where To Read Next

- Read [backend/README.md](backend/README.md) to understand the Flask routes, authentication, and Appwrite communication.
- Read [frontend/README.md](frontend/README.md) to understand how the map, marker drawing, draft pins, and popups work.

#### command to get lines of code:` cloc --vcs=git .`
