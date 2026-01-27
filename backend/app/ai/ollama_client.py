# Model wrapper

import ollama
from typing import Optional

class Ollama_client_error(RuntimeError):
    """Raised When Client Fails"""
    pass

def ask_ollama(
        system_prompt:str,
        user_prompt: str,
        *,
        model: str='llama3'
) -> str:
    if not system_prompt.strip():
        raise ValueError("system_prompt cannot be empty")


    if not user_prompt.strip:
        raise ValueError("system_prompt cannot be empty")

    try:
        response = ollama.chat(
            model = model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

    except Exception as e:
        raise Ollama_client_error(f"Ollama request failed: {e}") from e
    
    
    message = response.get("message")
    if not message:
        raise Ollama_client_error("Missing 'message' in Ollama response")

    content = message.get("content")
    if not content or not isinstance(content, str):
        raise Ollama_client_error("Empty or invalid content from Ollama")
    
    return content
