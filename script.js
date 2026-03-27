document.addEventListener("DOMContentLoaded", () => {
console.log("Notes to Flow loaded");

const toolbar = document.getElementById("editor-toolbar");
const editor = document.getElementById("editor");
const flowPanel = document.getElementById("flow-panel");
const generateBtn = document.getElementById("generate-flow");
const formatGenerateBtn = document.getElementById("format-generate-flow");
let latestPayload = null;

/* -------------------- TOOLBAR -------------------- */
formatGenerateBtn.addEventListener("click", async () => {
  const rawText = editor.innerText.trim();
  if(!rawText || rawText.length === 0) {
    alert("Please enter some text to format.");
    return;
  }

  const response = await fetch("http://127.0.0.1:8000/graph/format", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText })
  });

  const result = await response.json();
  if (!response.ok || !result.graph) {
    alert("Formatting failed: " + (result.detail || "Unknown error"));
    return;
  }

  editor.innerHTML = result.html; // Clear current content

  renderGraph(result.graph);
});


toolbar.addEventListener("click", (e) => {
  const action = e.target.dataset.action;
  if (!action) return;

  editor.focus();

  switch (action) {
    case "bold":
      document.execCommand("bold");
      break;
    case "italic":
      document.execCommand("italic");
      break;
    case "h1":
      document.execCommand("formatBlock", false, "h1");
      break;
    case "h2":
      document.execCommand("formatBlock", false, "h2");
      break;
    case "ul":
      document.execCommand("insertUnorderedList");
      break;
  }
});

/* -------------------- INPUT PARSING -------------------- */
/* SIMPLE + STABLE: one visible line = one node */

editor.addEventListener("input", () => {
  const nodes = [];
  editor.childNodes.forEach(child => {
    let text = "";
    let importance = 2;

    if (child.nodeName === "H1") {
      text = child.innerText.trim();
      importance = 5;
    } else if (child.nodeName === "H2") {
      text = child.innerText.trim();
      importance = 3;
    } else if (child.nodeName === "UL" || child.nodeName === "OL") {
      child.querySelectorAll("li").forEach(li => {
        const t = li.innerText.trim();
        if (t.length > 0) nodes.push({ text: t, importance: 2 });
      });
      return;
    } else {
      text = child.innerText ? child.innerText.trim() : child.textContent.trim();
    }

    if (text.length > 0) nodes.push({ text, importance });
  });

  latestPayload = { nodes, ai_review: false };
});

/* -------------------- API CALL -------------------- */

async function callParseApi(payload) {
  const response = await fetch("http://127.0.0.1:8000/graph/parse", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return await response.json();
}

/* -------------------- GENERATE FLOW -------------------- */

generateBtn.addEventListener("click", async () => {
  if (!latestPayload || latestPayload.nodes.length === 0) {
    alert("Nothing to generate yet");
    return;
  }

  const result = await callParseApi(latestPayload);
  console.log("Backend graph:", result.graph);

  renderGraph(result.graph);
});

/* -------------------- RENDER GRAPH -------------------- */

function renderGraph(graph) {
  flowPanel.innerHTML = "";

  const cy = cytoscape({
    container: flowPanel,

    elements: [
      ...graph.nodes.map(node => ({
        data: {
          id: String(node.id),
          label: node.label
        }
      })),
      ...(graph.edges || []).map(edge => ({
        data: {
          id: edge.id,
          source: String(edge.source),
          target: String(edge.target)
        }
      }))
    ],

    style: [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "background-color": "#2563eb",
          color: "#ffffff",
          "text-valign": "center",
          "text-halign": "center",
          "font-size": "14px",
          width: "label",
          height: "label",
          padding: "12px"
        }
      },
      {
        selector: "edge",
        style: {
          width: 2,
          "line-color": "#888",
          "target-arrow-color": "#888",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier"
        }
      }
    ],

    layout: {
      name: "breadthfirst",
      directed: true,
      padding: 60,
      spacingFactor: 1.5
    }
  });

  cy.fit();
  cy.center();
}

});