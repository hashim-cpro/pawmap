# PawMap Frontend

This folder contains the vanilla HTML, CSS, and JavaScript UI for PawMap. There is no React or build step here. The browser loads static files, Leaflet draws the map, and `fetch()` calls send data to the Flask backend.

## Main Files

- `index.html` - The page shell, nav bar, map container, report dialog, and draft-pin HUD.
- `css/main.css` - Shared page styling.
- `css/map.css` - Map layout, custom pin styling, dialog layout, and preview styles.
- `js/api.js` - Shared app state plus auth and config loading.
- `js/ui.js` - Dialog logic, form handling, media preview generation, and submit requests.
- `js/map.js` - Leaflet map setup, report rendering, custom marker icons, circles, and popup content.

## How The Map Script Works

`js/map.js` is the important file for the visible map behavior:

1. It creates the Leaflet map and adds the tile layer.
2. It reads saved reports from `GET /api/animals`.
3. It normalizes the response shape, because the backend can return Appwrite documents either flattened or wrapped in `data`.
4. For each saved report, it creates a persistent custom pointer with `L.divIcon`.
5. It also draws a radius circle around the report center.
6. If a report contains multiple persisted sighting points, the script computes a center and a covering radius from those points.
7. Clicking either the pin or the circle opens the report popup.

## Draft Pins Versus Saved Reports

The app has two different pin systems:

- Draft pins are temporary markers the user places while preparing a report.
- Saved reports are the permanent pins loaded from the backend database.

The draft pin flow is controlled by `js/ui.js` and the saved report rendering is controlled by `js/map.js`. Keeping them separate makes it easier to build a report before it is saved, then show the final result after the backend confirms it.

## Communication With The Backend

The frontend talks to Flask using plain `fetch()` requests:

- `GET /api/config` loads Appwrite configuration values.
- `GET /api/auth/me` checks whether the user is signed in.
- `POST /api/auth/login`, `POST /api/auth/register`, and `POST /api/auth/logout` manage authentication.
- `GET /api/animals` loads all saved reports for the map.
- `POST /api/animals` sends a form submission with report fields and media files.

The browser uses `FormData` for the report submit request, which allows text fields and uploaded files in the same request.

## Map And Drawing Notes

Leaflet is doing the visual work in the browser:

- `L.marker` places the clickable report pointer.
- `L.circle` draws the report radius.
- `L.divIcon` gives the permanent pointer its custom look.
- The draft-pin HUD and map click handler let the user place temporary pins before submitting.
- The search box uses OpenStreetMap Nominatim to move the map camera to a typed location.

## Running The Frontend

You normally do not run this folder by itself. The recommended path is:

1. Start the backend from `backend/`.
2. Open `http://127.0.0.1:3000` in the browser.

If you open `index.html` with a static server instead, the UI will load, but `/api/*` requests will fail unless you provide a matching backend proxy.
