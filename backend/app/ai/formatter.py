from bs4 import BeautifulSoup
from app.ai.ollama_client import ask_ollama, Ollama_client_error

FORMATTER_SYSTEM_PROMPT = FORMATTER_SYSTEM_PROMPT = """
You are a note structurer. Your only job is to reorganize text into HTML without losing ANY information.

STRICT RULES:
- Use ONLY these tags: <h1>, <h2>, <ul>, <li>
- Use ONE <h1> per major topic, which is the highest level of hierarchy. It should represent a main topic or theme that encompasses multiple related points.
- <h1> is preffered to be of single word but can be of maximum two words if it helps clarity. It should be a concise label that captures the essence of the topic.
- Every <h1> must appear before its related <h2> and <ul> tags
- If you cannot determine a topic name, infer one from the content — never skip the <h1>
- Multiple <h2> under each <h1> are allowed
- If multiple points are related to same main topic, group them under the same <h1> and use multiple <h2> for subtopics if needed
- <ul><li> under each <h2> for every single point, fact, definition, and detail
- Every <li> must be a complete, self-contained statement — keep enough words so the meaning is fully preserved
- If a point has an explanation attached, keep BOTH the point and its explanation in the same <li>
- DO NOT summarize, compress, merge, or drop any content
- DO NOT strip words or shorten sentences if it changes the meaning
- DO NOT add any new information or reword anything — copy the core fact as-is, only clean up grammar if necessary
- Make the points as concise as possible without losing meaning, but do not remove any words if it changes the meaning
- It must resemble a well-organized set of notes with clear hierarchy and structure, not a long paragraph or essay
- Reduce redundancy by grouping related points under the same <h1> and using multiple <h2> for subtopics if needed, but do not remove any points or details
- If a point is repeated multiple times, keep it only once but make sure to include all unique details and explanations attached to it in the same <li>
- Create easy to remember and grasp , short bullet points that capture the essence of each fact, definition, and detail, but do not remove any words if it changes the meaning for all html tags.
- You may remove filler words like "also", "additionally", "in order to", "basically", "essentially", "very", "really", "actually", "just", "quite", "somewhat", "a bit", "sort of", "kind of", etc. if it does not change the meaning, but do not remove any words if it changes the meaning
- Do not use <h3>, <h4>, <b>, <strong>, <p>, <br> tags
- No attributes on any tag
- Return ONLY raw HTML. No explanation. No markdown. No code fences.
- DO NOT paraphrase or reword the meaning of any point — copy the core fact as-is, only clean up grammar if necessary
- NEVER invert or alter the meaning of a statement. "No failure chance" must stay as "No failure chance", not be moved to a Risks section
- DO NOT paraphrase, reword, or alter the meaning of any statement — preserve the original wording as closely as possible
- NEVER move a point to a different section if it changes its meaning. "No failure chance" belongs under Benefits, not Risks


EXAMPLE 1:
Input:
Method A runs before execution. It uses more disk space. It is faster since dependencies are bundled. Method B runs at runtime. It uses less memory as resources are shared. It has higher failure risk. Loaders read binary object code and copy it into memory. They also allocate memory and resolve external references.

Output:
<h1>Linking Methods</h1><h2>Method A</h2><ul><li>Runs before execution begins</li><li>Uses more disk space due to bundled dependencies</li><li>Faster execution since all dependencies are included</li></ul><h2>Method B</h2><ul><li>Runs at runtime, not before execution</li><li>Uses less memory because resources are shared</li><li>Higher failure risk compared to Method A</li></ul><h1>Loaders</h1><h2>Core Function</h2><ul><li>Reads binary object code and copies it into memory</li><li>Allocates memory for program data</li><li>Resolves external references to other programs or libraries</li></ul>


"""

IMPORTANCE = {"h1": 1, "h2": 2, "li": 3}

def parse_html_to_nodes(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")
    nodes = []

    for tag in soup.find_all(["h1", "h2", "li"]):
        text = tag.get_text(strip=True)
        if text:
            nodes.append({
                "text": text,
                "importance": IMPORTANCE.get(tag.name, 2)
            })

    return nodes

def format_blob(raw_text: str) -> dict:
    if not raw_text or not raw_text.strip():
        raise ValueError("Input text cannot be empty")

    try:
        raw = ask_ollama(
            system_prompt=FORMATTER_SYSTEM_PROMPT,
            user_prompt=raw_text.strip()
        )
    except Ollama_client_error as e:
        raise RuntimeError(f"Formatter AI call failed: {e}") from e

    print("\n[FORMATTER RAW OUTPUT]")
    print(raw)

    # Strip markdown fences if model misbehaves
    cleaned = raw.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("html"):
                part = part[4:].strip()
            if "<" in part:
                cleaned = part.strip()
                break

    # Verify it looks like HTML
    if "<h1>" not in cleaned and "<h2>" not in cleaned:
        raise RuntimeError("Formatter did not return valid HTML")

    nodes = parse_html_to_nodes(cleaned)

    if not nodes:
        raise RuntimeError("No nodes could be parsed from HTML")

    return {"nodes": nodes, "html": cleaned}