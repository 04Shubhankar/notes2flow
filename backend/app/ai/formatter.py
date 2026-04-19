import json
from app.ai.ollama_client import ask_ollama, Ollama_client_error

FORMATTER_SYSTEM_PROMPT ="""
Return ONLY a JSON object. No explanation. No markdown. No code fences.

Structure:
{
  "nodes": [{"text": "...", "importance": 1-5}],
  "html": "<h1>...</h1><h2>...</h2><ul><li>...</li></ul>"
}

Importance: 5=main topic, 3=subtopic, 2=bullet point, 1=detail.

The Heading of the HTML should be the most important node. Subheadings should be less important. Bullet points should be least important. The HTML structure should reflect the importance hierarchy.
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