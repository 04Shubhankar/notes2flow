const overlay = document.getElementById("info-popup-overlay");
const closeBtn = document.getElementById("close-popup");

closeBtn.addEventListener("click", () => {
  overlay.classList.add("hidden");
});

window.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    overlay.classList.add("hidden");
  }
});