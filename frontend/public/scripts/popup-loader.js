async function loadPopup() {
  try {
    // Fetch popup HTML
    const response = await fetch("./popup-modal.html");
    const html = await response.text();

    // Inject popup into DOM
    document.body.insertAdjacentHTML("beforeend", html);

    // Load popup CSS
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "./styles/popup.css";
    document.head.appendChild(link);

    // Initialize popup functionality
    initializePopup();

  } catch (error) {
    console.error("Failed to load popup:", error);
  }
}

function initializePopup() {
  const overlay = document.getElementById("info-popup-overlay");
  const closeBtn = document.getElementById("close-popup");

  if (!overlay) {
    console.error("Popup overlay not found");
    return;
  }

  // Show popup
  overlay.classList.remove("hidden");

  // Close popup button
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      overlay.classList.add("hidden");
      console.log("Popup closed");
    });
  }

  // Close on ESC
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      overlay.classList.add("hidden");
    }
  });

  // Close when clicking outside popup
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) {
      overlay.classList.add("hidden");
    }
  });
}

// Load popup
loadPopup();