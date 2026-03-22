console.log("Notes to Flow loaded");

const toolbar = document.getElementById("editor-toolbar");
const editor = document.getElementById("editor");
const flowPanel = document.getElementById("flow-panel");
const generateBtn = document.getElementById("generate-flow");

let latestPayload = null;

/* -------------------- TOOLBAR -------------------- */

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
  const lines = editor.innerText
    .split(/\r?\n/)
    .map(line => line.trim())
    .filter(line => line.length > 0);

  latestPayload = {
    nodes: lines.map(line => ({
      text: line,
      importance: 2
    })),
    ai_review: false
  };

  console.log("Prepared payload:");
  console.log(JSON.stringify(latestPayload, null, 2));
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
          source: String(edge.from_node),
          target: String(edge.to_node)
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