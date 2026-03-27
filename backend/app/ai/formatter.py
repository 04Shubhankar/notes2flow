import json
from app.ai.ollama_client import ask_ollama, Ollama_client_error

FORMATTER_SYSTEM_PROMPT = """
You are a note-structuring assistant.

The user will give you a blob of unstructured text.
Your job is to organize it into a clear hierarchy and return ONLY a JSON object.

Return ONLY valid JSON. No explanations. No markdown. No code fences.

The JSON must have exactly this structure:
{
  "nodes": [
    { "text": "<heading or point>", "importance": <integer 1-5> }
  ],
  "html": "<formatted HTML string using only h1, h2, h3, ul, li, p tags>"
}

Importance scale:
- 5 = main topic (h1)
- 3 = subtopic (h2)
- 2 = supporting point (h3 or bullet)
- 1 = detail

Rules:
- Every node must have a non-empty text and a valid importance integer
- The html field must reflect the same hierarchy as the nodes
- Do NOT include any key other than "nodes" and "html"
- Do NOT wrap in markdown or code fences
"""

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

    # Strip accidental markdown fences if model misbehaves
    cleaned = raw.strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.strip().startswith("{") or part.strip().startswith("["):
                cleaned = part.strip()
                break
    # Extract JSON object if there's text before/after it
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end+1]

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Formatter returned invalid JSON: {e}")

    nodes = parsed.get("nodes")
    html = parsed.get("html")

    if not isinstance(nodes, list) or not nodes:
        raise RuntimeError("Formatter returned no nodes")

    if not isinstance(html, str) or not html.strip():
        raise RuntimeError("Formatter returned no html")

    return {"nodes": nodes, "html": html}