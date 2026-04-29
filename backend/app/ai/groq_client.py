from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

class Groq_client_error(RuntimeError):
    """Raised when Groq API call fails"""
    pass

# API key
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def ask_groq(
        system_prompt: str,
        user_prompt: str,
        *,
        model: str = 'llama-3.3-70b-versatile'
) -> str:
    if not system_prompt.strip():
        raise ValueError("system_prompt cannot be empty")
    if not user_prompt.strip():
        raise ValueError("user_prompt cannot be empty")

    try:
        print(f"[GROQ] Sending request to {model}...")
        
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            temperature=0.3,
            top_p=0.95,
            stream=False,
            max_tokens=4096,
        )
        
        content = response.choices[0].message.content
        print(content, flush=True)
        print(f"\n[GROQ] Response complete ({len(content)} chars)")
        
    except Exception as e:
        print(f"[GROQ ERROR] {e}")
        raise Groq_client_error(f"Groq request failed: {e}") from e

    if not content or not isinstance(content, str):
        raise Groq_client_error("Empty or invalid content from Groq")

    return content