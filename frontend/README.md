# PawMap Frontend

This is the purely Native (Vanilla) HTML, CSS, and JavaScript frontend for the PawMap project. It completely eliminates the need for modern complex frameworks like React or build tools like Vite.

## Architecture

The frontend is broken down into simple foundational web technologies:

- **`index.html`:** The single-page shell that houses the map container, authentication modals, search boxes, and adding forms using standard `<dialog>` and `<div>` elements.
- **`styles.css`:** Contains all the styling rules for the UI overlays, dialogs, and map markers.
- **`app.js`:** The core logic file handling:
  - **Leaflet.js Integration:** Renders interactive maps, plots SVG markers based on animal coordinate data, and calculates visual roaming ranges (radii). Uses the `leaflet-draw` plugin to allow polygon searches.
  - **Auth State:** Manages UI visibility based on whether `currentUser` exists.
  - **API Fetching:** Uses the native `fetch()` API to communicate with the Flask backend to process logins, load points, and upload multipart `<form>` data for images.
  - **Nominatim Search:** Utilizes OpenStreetMap's Nominatim geolocation API to provide a live search box for addresses, shifting the map camera accordingly.

## Setup & Running

Because this application relies on the Flask backend to handle Appwrite authentication routing and securely upload media, the easiest way to run the frontend is through the backend server.

1. Ensure the backend is set up and running on port `3000` (see `backend/README.md`).
2. Open a web browser and navigate to:
   ```text
   http://127.0.0.1:3000
   ```
   Flask is configured to automatically serve `index.html` and the associated static `assets/`, `styles.css`, and `app.js` files perfectly.

### Active Development

If you only want to work on frontend UI/CSS tweaks and do not need full API functionality, you can open `index.html` with an extension like **Live Server** in VS Code. However, API requests to `/api/*` will fail unless you configure a local proxy. Relying on the Flask server for active runtime is recommended.
