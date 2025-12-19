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

editor.addEventListener("input", () => {
  const structure = parseNotes(editor.innerHTML);
  console.log(structure);
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

