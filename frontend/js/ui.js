// Manage Auth UI Navigation
const setupNav = async () => {
  await checkAuth(); // Ensures window.pawmapState.currentUser is populated

  // First, try to handle top navigation if it exists
  const navLinks = document.getElementById("nav-links");
  if (navLinks) {
    if (window.pawmapState.currentUser) {
      navLinks.innerHTML = `
                <span>Hello, ${window.pawmapState.currentUser.name || "User"}</span>
                <button onclick="logout()">Logout</button>
            `;
      const fab = document.getElementById("fab-add-animal");
      if (fab) fab.classList.remove("hidden");
    } else {
      navLinks.innerHTML = `
                <a href="login.html">Login</a>
                <a href="register.html">Register</a>
            `;
      const fab = document.getElementById("fab-add-animal");
      if (fab) fab.classList.add("hidden");
    }
  }

  // Secondly, handle Auth Modals if a user just landed here logged in
  const authContainer = document.querySelector(".auth-container");
  if (authContainer && window.pawmapState.currentUser) {
    // If the user is on the login/register page but is already logged in,
    // redirect them back to the map index automatically.
    authContainer.innerHTML = `<h2 class="text-center">You are already logged in! Redirecting...</h2>`;
    setTimeout(() => (window.location.href = "index.html"), 1500);
  }
};

// Sighting Dialog Logic
const dialog = document.getElementById("animal-dialog");
const closeDialogBtn = document.getElementById("close-dialog");
const fabAdd = document.getElementById("fab-add-animal");
const toggleFormBtn = document.getElementById("toggle-form-btn");
const placePinsBtn = document.getElementById("place-pins-btn");
const animalForm = document.getElementById("animal-form");
const getLocBtn = document.getElementById("get-location-btn");
const locText = document.getElementById("selected-coords");
const mediaInput = document.getElementById("animal-media");
const mediaPreview = document.getElementById("media-preview");

let previewUrls = [];

const clearMediaPreviews = () => {
  previewUrls.forEach((url) => URL.revokeObjectURL(url));
  previewUrls = [];

  if (mediaPreview) {
    mediaPreview.innerHTML = "";
    mediaPreview.classList.add("hidden");
  }
};

const renderMediaPreviews = () => {
  if (!mediaInput || !mediaPreview) return;

  clearMediaPreviews();

  const files = Array.from(mediaInput.files || []);
  if (files.length === 0) return;

  files.forEach((file) => {
    const previewItem = document.createElement("div");
    previewItem.className = "media-preview-item";

    const previewUrl = URL.createObjectURL(file);
    previewUrls.push(previewUrl);

    if (file.type.startsWith("video/")) {
      const video = document.createElement("video");
      video.src = previewUrl;
      video.controls = true;
      video.playsInline = true;
      previewItem.appendChild(video);
    } else {
      const image = document.createElement("img");
      image.src = previewUrl;
      image.alt = file.name;
      previewItem.appendChild(image);
    }

    const caption = document.createElement("span");
    caption.textContent = file.name;
    previewItem.appendChild(caption);

    mediaPreview.appendChild(previewItem);
  });

  mediaPreview.classList.remove("hidden");
};

const showFormDialog = () => {
  if (!dialog) return;
  dialog.showModal();
  if (toggleFormBtn) toggleFormBtn.classList.add("hidden");
};

const hideFormDialog = ({ resetForm = false } = {}) => {
  if (!dialog) return;
  dialog.close();
  if (toggleFormBtn) toggleFormBtn.classList.remove("hidden");

  if (resetForm && animalForm) {
    animalForm.reset();
    window.pawmapState.selectedLocation = null;
    window.pawmapState.isSelectingLocation = false;
    if (locText) locText.innerText = "Select location on map or use button";
    clearMediaPreviews();
  }
};

if (fabAdd) {
  fabAdd.addEventListener("click", () => {
    if (!window.pawmapState.currentUser) {
      alert("Please login first.");
      return;
    }
    showFormDialog();
  });
}

if (toggleFormBtn) {
  toggleFormBtn.addEventListener("click", () => {
    showFormDialog();
  });
}

if (closeDialogBtn) {
  closeDialogBtn.addEventListener("click", () => {
    hideFormDialog();
  });
}

if (placePinsBtn) {
  placePinsBtn.addEventListener("click", () => {
    hideFormDialog();
  });
}

if (getLocBtn) {
  getLocBtn.addEventListener("click", () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          window.pawmapState.selectedLocation = {
            lat: pos.coords.latitude,
            lng: pos.coords.longitude,
            computedRadius: 0,
          };
          locText.innerText = `Selected: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
        },
        () => {
          alert("Failed to get your location.");
        },
      );
    } else {
      alert("Geolocation is not supported by your browser.");
    }
  });
}

if (mediaInput) {
  mediaInput.addEventListener("change", renderMediaPreviews);
}

if (animalForm) {
  animalForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Grab values
    const form = e.target;
    const formData = new FormData();
    formData.append("animal_name", form.querySelector("#animal-name").value);
    formData.append("animal_type", form.querySelector("#animal-type").value);
    formData.append("incident", form.querySelector("#animal-incident").value);
    formData.append("breed", form.querySelector("#animal-breed").value);

    const maxRange = { cat: 2000, dog: 3000, other: 2500 };
    let finalRadius =
      maxRange[form.querySelector("#animal-type").value] || 2500;

    // If multiple pins dictated a computed radius encompassing the area, use that.
    if (
      window.pawmapState.selectedLocation &&
      window.pawmapState.selectedLocation.computedRadius > 0
    ) {
      finalRadius = window.pawmapState.selectedLocation.computedRadius;
    }

    formData.append("radius", finalRadius);

    if (window.pawmapState.selectedLocation) {
      formData.append("latitude", window.pawmapState.selectedLocation.lat);
      formData.append("longitude", window.pawmapState.selectedLocation.lng);
    } else {
      alert("No location selected!");
      return;
    }

    const files = form.querySelector("#animal-media").files;
    for (let i = 0; i < files.length; i++) {
      formData.append("media", files[i]);
    }

    try {
      const res = await fetch("/api/animals", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        alert("Sighting reported successfully!");
        hideFormDialog({ resetForm: true });
        window.location.reload(); // Quick way to refresh map
      } else {
        const data = await res.json();
        alert("Error: " + data.error);
      }
    } catch (err) {
      console.error(err);
      alert("Failed to submit.");
    }
  });
}

// Check auth state on load.
// If the DOM is already ready, run it immediately, else wait
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", setupNav);
} else {
  setupNav();
}
