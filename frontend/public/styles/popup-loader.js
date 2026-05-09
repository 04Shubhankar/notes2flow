async function loadPopup() {
  const response = await fetch("./components/popup/popup.html");
  const html = await response.text();

  document.body.insertAdjacentHTML("beforeend", html);

  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "./components/popup/popup.css";
  document.head.appendChild(link);

  const script = document.createElement("script");
  script.src = "./components/popup/popup.js";
  document.body.appendChild(script);
}

loadPopup();