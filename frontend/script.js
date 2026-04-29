document.addEventListener("DOMContentLoaded", () => {
  console.log("Notes to Flow loaded");

  const toolbar = document.getElementById("editor-toolbar");
  const editor = document.getElementById("editor");
  const flowPanel = document.getElementById("flow-panel");
  const placeholder = document.getElementById("placeholder");
  const generateBtn = document.getElementById("generate-flow");
  const formatGenerateBtn = document.getElementById("format-generate-flow");
  const enableReviewCheckbox = document.getElementById("enable-ai-review");
  
  // Graph control buttons
  const zoomInBtn = document.getElementById("zoom-in");
  const zoomOutBtn = document.getElementById("zoom-out");
  const fitViewBtn = document.getElementById("fit-view");
  const resetPanBtn = document.getElementById("reset-pan");
  const exportPngBtn = document.getElementById("export-png");
  const exportSvgBtn = document.getElementById("export-svg");

  let latestPayload = null;
  let cy = null; // Global cytoscape instance

  /* -------------------- TOOLBAR -------------------- */
  formatGenerateBtn.addEventListener("click", async () => {
    const rawText = editor.innerText.trim();
    if (!rawText || rawText.length === 0) {
      alert("Please enter some text to format.");
      return;
    }

    try {
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

      editor.innerHTML = result.html;
      renderGraph(result.graph);
    } catch (error) {
      console.error("Format error:", error);
      alert("Failed to format notes: " + error.message);
    }
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
      case "h3":
        document.execCommand("formatBlock", false, "h3");
        break;
      case "h4":
        document.execCommand("formatBlock", false, "h4");
        break;
      case "ul":
        document.execCommand("insertUnorderedList");
        break;
    }

    editor.dispatchEvent(new Event("input", { bubbles: true }));
  });

  /* -------------------- INPUT PARSING -------------------- */
  enableReviewCheckbox.addEventListener("change", () => {
    if (latestPayload) {
      latestPayload.ai_review = enableReviewCheckbox.checked;
      console.log("AI Review enabled:", enableReviewCheckbox.checked);
    }
  });

  editor.addEventListener("input", () => {
    editor.querySelectorAll("p > ul, p > ol").forEach(list => {
      list.parentNode.insertAdjacentElement("afterend", list);
    });

    const nodes = [];
    editor.childNodes.forEach(child => {
      let text = "";
      let importance = 2;

      if (child.nodeName === "H1") {
        text = child.innerText.trim();
        importance = 1;
      } else if (child.nodeName === "H2") {
        text = child.innerText.trim();
        importance = 2;
      } else if (child.nodeName === "H3") {
        text = child.innerText.trim();
        importance = 3;
      } else if (child.nodeName === "H4") {
        text = child.innerText.trim();
        importance = 4;
      } else if (child.nodeName === "P") {
        const paraText = child.innerText.trim();
        if (paraText.startsWith("• ") || paraText.startsWith("- ") || /^\d+\.\s/.test(paraText)) {
          text = paraText;
          importance = 5;
        } else {
          text = paraText;
        }
      } else if (child.nodeName === "LI") {
        text = child.innerText.trim();
        importance = 5;
      } else if (child.nodeName === "UL" || child.nodeName === "OL") {
        child.querySelectorAll("li").forEach(li => {
          const t = li.innerText.trim();
          if (t.length > 0) {
            nodes.push({ text: t, importance: 5 });
          }
        });
        return;
      } else {
        text = child.innerText ? child.innerText.trim() : child.textContent.trim();
      }

      if (text.length > 0) nodes.push({ text, importance });
    });

    latestPayload = { nodes, ai_review: enableReviewCheckbox.checked };
  });

  /* -------------------- API CALL -------------------- */
  async function callParseApi(payload) {
    const response = await fetch("http://127.0.0.1:8000/graph/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
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

    try {
      const result = await callParseApi(latestPayload);
      console.log("Backend graph:", result.graph);
      renderGraph(result.graph);
    } catch (error) {
      console.error("Parse error:", error);
      alert("Failed to generate flow: " + error.message);
    }
  });

  /* -------------------- RENDER GRAPH -------------------- */
  function renderGraph(graph) {
    flowPanel.innerHTML = "";
    placeholder.style.display = "none";

    // Professional color palette for hierarchy levels
    const colorPalette = {
      1: { bg: "#1e3a8a", text: "#ffffff" },      // Dark blue (H1)
      2: { bg: "#2563eb", text: "#ffffff" },      // Blue (H2)
      3: { bg: "#3b82f6", text: "#ffffff" },      // Light blue (H3)
      4: { bg: "#60a5fa", text: "#ffffff" },      // Lighter blue (H4)
      5: { bg: "#93c5fd", text: "#1e293b" }       // Very light blue (list items)
    };

    cy = cytoscape({
      container: flowPanel,
      wheelSensitivity: 0.1,
      
      elements: [
        ...graph.nodes.map(node => ({
          data: {
            id: String(node.id),
            label: node.label,
            importance: node.importance
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
            "text-valign": "center",
            "text-halign": "center",
            "text-wrap": "wrap",
            "text-max-width": "140px",
            "font-size": "13px",
            "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto",
            color: "#ffffff",
            "background-color": "#2563eb",
            width: "160px",
            height: "60px",
            padding: "12px",
            shape: "roundrectangle",
            "border-width": "2px",
            "border-color": "rgba(0, 0, 0, 0.1)",
            "transition-property": "background-color, border-color",
            "transition-duration": "200ms"
          }
        },
        {
          selector: "node[importance = 1]",
          style: {
            "background-color": colorPalette[1].bg,
            color: colorPalette[1].text,
            "font-size": "14px",
            "font-weight": "bold",
            width: "180px",
            height: "70px",
            padding: "16px"
          }
        },
        {
          selector: "node[importance = 2]",
          style: {
            "background-color": colorPalette[2].bg,
            color: colorPalette[2].text,
            "font-size": "13px",
            "font-weight": "600",
            width: "170px",
            height: "65px",
            padding: "14px"
          }
        },
        {
          selector: "node[importance = 3]",
          style: {
            "background-color": colorPalette[3].bg,
            color: colorPalette[3].text,
            "font-size": "12px",
            width: "160px",
            height: "60px",
            padding: "12px"
          }
        },
        {
          selector: "node[importance = 4]",
          style: {
            "background-color": colorPalette[4].bg,
            color: colorPalette[4].text,
            "font-size": "11px",
            width: "150px",
            height: "55px",
            padding: "10px"
          }
        },
        {
          selector: "node[importance = 5]",
          style: {
            "background-color": colorPalette[5].bg,
            color: colorPalette[5].text,
            "font-size": "11px",
            width: "140px",
            height: "50px",
            padding: "8px"
          }
        },
        {
          selector: "node:hover",
          style: {
            "border-width": "3px",
            "border-color": "rgba(0, 0, 0, 0.3)"
          }
        },
        {
          selector: "node:selected",
          style: {
            "border-width": "3px",
            "border-color": "#fbbf24"
          }
        },
        {
          selector: "edge",
          style: {
            width: 2,
            "line-color": "#64748b",
            "target-arrow-color": "#64748b",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier",
            "arrow-scale": 1.5
          }
        },
        {
          selector: "edge:hover",
          style: {
            "line-color": "#334155",
            "target-arrow-color": "#334155",
            width: 3
          }
        }
      ],

      layout: {
        name: "breadthfirst",
        directed: true,
        padding: 50,
        spacingFactor: 1.3,
        avoidOverlap: true
      }
    });

    // Fit and center
    cy.fit();
    cy.center();

    // Enable interaction
    setupGraphInteraction();
  }

  /* -------------------- GRAPH INTERACTION -------------------- */
  function setupGraphInteraction() {
    if (!cy) return;

    // Zoom controls
    zoomInBtn.addEventListener("click", () => {
      cy.zoom(cy.zoom() * 1.2);
    });

    zoomOutBtn.addEventListener("click", () => {
      cy.zoom(cy.zoom() / 1.2);
    });

    fitViewBtn.addEventListener("click", () => {
      cy.fit();
    });

    resetPanBtn.addEventListener("click", () => {
      cy.center();
    });

    // Export controls
    exportPngBtn.addEventListener("click", () => {
      const pngData = cy.png({ scale: 2, full: true });
      downloadImage(pngData, "flowchart.png");
    });

    exportSvgBtn.addEventListener("click", () => {
      try {
        // Cytoscape has limited SVG export. Fallback: export as PNG
        const pngData = cy.png({ scale: 2, full: true });
        downloadImage(pngData, "flowchart.png");
        console.warn("SVG export via canvas fallback (PNG)");
      } catch (error) {
        console.error("SVG export error:", error);
        alert("SVG export not available. Using PNG instead.");
      }
    });

    // Mouse wheel zoom (smooth)
    cy.on("wheel", (e) => {
      if (e.originalEvent.ctrlKey || e.originalEvent.metaKey) {
        e.preventDefault();
        const scale = 1 + (e.originalEvent.deltaY > 0 ? -0.1 : 0.1);
        cy.zoom(cy.zoom() * scale);
      }
    });

    // Click to select
    cy.on("tap", "node", (e) => {
      console.log("Clicked node:", e.target.data());
    });
  }

  /* -------------------- EXPORT HELPER -------------------- */
  function downloadImage(dataUrl, filename) {
    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }

  // Show placeholder initially
  placeholder.style.display = "block";
});
