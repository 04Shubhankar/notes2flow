# Model wrapper

import ollama
from typing import Optional

class Ollama_client_error(RuntimeError):
    """Raised When Client Fails"""
    pass

def ask_ollama(
        system_prompt: str,
        user_prompt: str,
        *,
        model: str = 'llama3.2:3b'
) -> str:
    if not system_prompt.strip():
        raise ValueError("system_prompt cannot be empty")
    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    try:
        stream = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True
        )

        chunks = []
        for chunk in stream:
            token = chunk.message.content
            if token:
                print(token, end="", flush=True)
                chunks.append(token)
        print()
        content = "".join(chunks)

    except Exception as e:
        raise Ollama_client_error(f"Ollama request failed: {e}") from e

    if not content or not isinstance(content, str):
        raise Ollama_client_error("Empty or invalid content from Ollama")

    return content
