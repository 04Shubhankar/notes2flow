// We will add logic here step by step
console.log("Notes to Flow loaded");
const toolbar = document.getElementById("editor-toolbar");

toolbar.addEventListener("click", (e) => {
  const action = e.target.dataset.action;
  if (!action) return;

  document.getElementById("editor").focus();

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

const editor = document.getElementById("editor");

let latestPayload = null;

editor.addEventListener("input", () => {
  const structure = parseNotes(editor.innerHTML);
  latestPayload = buildApiPayload(structure);

  console.log("Prepared payload (not sent):");
  console.log(JSON.stringify(latestPayload, null, 2));
});




function parseNotes(html) {
  const temp = document.createElement("div");
  temp.innerHTML = html;

  const nodes = [];
  let currentH1 = null;
  let currentH2 = null;

  temp.childNodes.forEach(node => {
    if (node.nodeName === "H1") {
      currentH1 = { title: node.innerText, children: [] };
      nodes.push(currentH1);
      currentH2 = null;
    }

    else if (node.nodeName === "H2" && currentH1) {
      currentH2 = { title: node.innerText, children: [] };
      currentH1.children.push(currentH2);
    }

    else if (node.nodeName === "UL") {
      const items = [...node.querySelectorAll("li")]
        .map(li => li.innerText);

      if (currentH2) currentH2.children.push(...items);
      else if (currentH1) currentH1.children.push(...items);
    }
  });

  return nodes;
}

function buildApiPayload(structure) {
  const nodes = [];

  function walk(item, importance) {
    // emit current node
    nodes.push({
      text: item.title,
      importance
    });

    // walk children if they exist
    if (item.children && item.children.length > 0) {
      item.children.forEach(child => {
        if (typeof child === "string") {
          nodes.push({
            text: child,
            importance: importance + 1
          });
        } else {
          walk(child, importance + 1);
        }
      });
    }
  }

  structure.forEach(h1 => walk(h1, 2));

  return {
    nodes,
    ai_review: false
  };
}



async function callParseApi(payload) {
  const response = await fetch("http://127.0.0.1:8000/graph/parse", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  return data;
}

const generateBtn = document.getElementById("generate-flow");

generateBtn.addEventListener("click", () => {
  if (!latestPayload) {
    alert("Nothing to generate yet");
    return;
  }

  callParseApi(latestPayload).then(result => {
    console.log("FINAL API response:");
    console.log(JSON.stringify(result, null, 2));
  });
});
