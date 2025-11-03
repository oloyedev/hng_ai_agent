import os
import httpx
from dotenv import load_dotenv

load_dotenv()

# Load credentials and model
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


async def analyze_contract(text: str) -> str:
    """
    Send contract text to Groq model for structured contract analysis and classification.
    Handles all error and response edge cases safely.
    """
    prompt = f"""
You are the Contract Clarity Agent. 
Your task is to analyze this contract and return ONLY valid JSON with the following structure:

{{
  "contract_type": "short label (e.g. NDA, Service Agreement, etc.)",
  "ambiguous_terms": ["list", "of", "vague", "terms"],
  "risk_clauses": ["list", "of", "risky", "clauses"],
  "simplified_summary": "plain-English summary of the main points",
  "recommendations": "practical suggestions for clarity or balance"
}}

Contract Text:
{text}
    """

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a legal contract analyst."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=50.0) as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )
        data = response.json()

        print("🔍 Groq raw response:", data)

    
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"].strip()
            return content

        elif "error" in data:
            err_message = data["error"].get("message", "Unknown Groq API error")
            raise ValueError(f"Groq API error: {err_message}")

        else:
            raise ValueError(f"Unexpected Groq response: {data}")
