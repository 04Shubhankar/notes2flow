from bs4 import BeautifulSoup
from app.ai.ollama_client import ask_ollama, Ollama_client_error

FORMATTER_SYSTEM_PROMPT = FORMATTER_SYSTEM_PROMPT = """
You are a note formatting engine. Convert raw input text into structured HTML notes.

OUTPUT RULES:
- Use ONLY these tags: <h1>, <h2>, <ul>, <li>
- No attributes on any tag
- No other tags allowed: no <h3>, <b>, <p>, <br>, <strong>
- Return ONLY raw HTML — no explanation, no markdown, no code fences

STRUCTURE RULES:
- <h1> = one major theme or domain (1–2 words max). One <h1> per major topic.
- <h2> = one distinct concept, subtopic, or idea within that theme. Use a NEW <h2> for every semantically distinct idea — even if ideas are related. More <h2>s is always better than fewer.
- <ul><li> = one fact, detail, or point per <li> under each <h2>
- Every <h1> must appear before its related <h2> tags
- Every <h2> must have at least one <ul><li>

H2 TRIGGER RULE — THIS IS CRITICAL:
Create a new <h2> every time the input shifts to a different aspect, property, cause, effect, type, step, or example — even within the same topic. When in doubt, split into more <h2>s rather than fewer. A flat structure with few <h2>s is always wrong.

CONTENT RULES:
- Preserve the original meaning of every point exactly — do not paraphrase or invert meaning
- Each <li> must be a complete, self-contained statement
- Remove filler words (also, basically, essentially, very, really, just) only if meaning is unchanged
- Do not add new information
- Do not merge two distinct points into one <li>
- If a point includes an explanation, keep both in the same <li>

PRIORITY ORDER (when rules conflict):
1. Correct tag structure
2. Meaning preserved
3. Conciseness

EXAMPLE:
Input:
"Photosynthesis is the process by which plants make food using sunlight. It occurs in the chloroplasts. The inputs are sunlight, water, and carbon dioxide. The output is glucose and oxygen. Without sunlight, photosynthesis cannot occur. Plants in dark conditions stop producing food."

Output:
<h1>Photosynthesis</h1>
<h2>Definition</h2>
<ul><li>Process by which plants make food using sunlight</li></ul>
<h2>Location</h2>
<ul><li>Occurs in the chloroplasts of plant cells</li></ul>
<h2>Inputs</h2>
<ul><li>Sunlight, water, and carbon dioxide are required</li></ul>
<h2>Outputs</h2>
<ul><li>Produces glucose and oxygen</li></ul>
<h2>Light Dependency</h2>
<ul><li>Cannot occur without sunlight — plants in dark conditions stop producing food</li></ul>
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