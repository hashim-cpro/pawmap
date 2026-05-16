// API Base Constants
let APPWRITE_ENDPOINT = "https://cloud.appwrite.io/v1";
let PROJECT_ID = "";
let BUCKET_ID = "animal_media";

// Fetch config from backend for dynamic variables
const fetchConfig = async () => {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    APPWRITE_ENDPOINT = data.endpoint;
    PROJECT_ID = data.project_id;
  } catch (err) {
    console.error("Could not fetch config from backend", err);
  }
};

// Current App State
window.pawmapState = {
  currentUser: null,
  isSelectingLocation: false,
  selectedLocation: null,
};

// Check if user is logged in
const checkAuth = async () => {
  try {
    const res = await fetch("/api/auth/me");
    if (res.ok) {
      const data = await res.json();
      window.pawmapState.currentUser = data.user;
    } else {
      window.pawmapState.currentUser = null;
    }
  } catch {
    window.pawmapState.currentUser = null;
  }
};

const logout = async () => {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.href = "index.html";
  } catch (e) {
    console.error("Logout failed", e);
  }
};

// Initializing the configuration for other modules
fetchConfig();
