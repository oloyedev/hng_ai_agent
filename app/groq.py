import os
import httpx
from dotenv import load_dotenv

load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


async def analyze_contract(text: str) -> str:
    """
    Send contract text to Groq model for structured contract analysis and classification.
    Handles all error and response edge cases safely.
    """
    prompt = f"""
You are the Contract Clarity Agent.

Analyze the following contract text and return your analysis as a valid JSON object.

Contract Text:
{text}

Return JSON with these exact keys:
- "contract_type": a short label for the contract (e.g. "NDA", "Service Agreement", "Employment Contract", "Lease", "Sales Contract", or "Unknown")
- "ambiguous_terms": list of terms or phrases that may cause confusion or lack definition
- "risk_clauses": list of clauses that heavily favor one side or create potential legal risk
- "simplified_summary": a clear, plain-English summary of the key parts of the contract
- "recommendations": a few practical suggestions to make the contract more balanced or understandable

Format the response as strict JSON only, without explanations or markdown.
    """

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are an expert legal contract analyst."},
            {"role": "user", "content": prompt}
        ]
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
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
