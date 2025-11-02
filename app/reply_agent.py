# app/groq_agent.py
from groq import Groq
from dotenv import load_dotenv
import os
import re
import random

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def _extract_content_from_choice(choice) -> str | None:
    """
    Robust extractor for the Groq SDK response choice object.
    Handles multiple shapes: dict-like, attribute-like, or legacy shapes.
    Returns the message content string or None if not found.
    """
    # 1) dict-like access (choice could be a dict)
    try:
        if isinstance(choice, dict):
            # typical OpenAI-like structure
            msg = choice.get("message") or choice.get("text")
            if isinstance(msg, dict):
                # message: {"content": "..."}
                # sometimes "content" might be a string or list
                content = msg.get("content")
                if isinstance(content, str):
                    return content
                # if content is list/dict, attempt to join text parts
                if isinstance(content, list):
                    return " ".join(str(c) for c in content)
            if isinstance(msg, str):
                return msg
            if "text" in choice and isinstance(choice["text"], str):
                return choice["text"]
    except Exception:
        pass

    # 2) attribute-like access
    try:
        msg_obj = getattr(choice, "message", None)
        if msg_obj is not None:
            # try .content
            if hasattr(msg_obj, "content"):
                content = getattr(msg_obj, "content")
                # if content is mapping with 'text' or 'content'
                if isinstance(content, str):
                    return content
                if isinstance(content, dict):
                    return content.get("text") or content.get("content")
            # try .text
            if hasattr(msg_obj, "text"):
                txt = getattr(msg_obj, "text")
                if isinstance(txt, str):
                    return txt
    except Exception:
        pass

    # 3) fallback: try choice.text attribute
    try:
        if hasattr(choice, "text"):
            txt = getattr(choice, "text")
            if isinstance(txt, str):
                return txt
    except Exception:
        pass

    return None

def _clean_reply(text: str, tone: str) -> str:
    """
    Clean up the model reply:
    - Remove excessive whitespace
    - Ensure under 20 words (truncate politely)
    - Remove disallowed emojis for non-casual tones
    """
    if not text:
        return text

    # strip spurious newlines and leading/trailing whitespace
    txt = re.sub(r"\s+", " ", text).strip()

    # remove surrounding quotes if model wrapped reply
    if (txt.startswith('"') and txt.endswith('"')) or (txt.startswith("'") and txt.endswith("'")):
        txt = txt[1:-1].strip()

    # For non-casual tones, strip emojis (simple heuristic)
    if tone != "casual":
        # remove common emoji characters (basic)
        txt = re.sub(r"[\U0001F300-\U0001F6FF\U0001F900-\U0001F9FF\u2600-\u26FF]+", "", txt)
        txt = txt.strip()

    # truncate to 20 words max
    words = txt.split()
    if len(words) > 20:
        txt = " ".join(words[:20]).rstrip(" ,.;:") + "..."

    # final safety: if empty, fallback
    if not txt:
        return random.choice([
            "Thanks — I’ll take a look.",
            "I’ll check and get back to you shortly.",
            "Thanks for the update; I’ll handle it."
        ])

    return txt

def generate_reply(message: str, user_tone: str = "neutral") -> str:
    """
    Generate a short, polite, context-aware reply using Groq.
    Uses a robust extractor to handle different SDK response shapes.
    """
    prompt = f"""
You are a helpful assistant that writes a short, polite, context-aware reply.

Message: "{message}"
Tone: {user_tone}

Rules:
- Keep the response under 20 words.
- Match the tone (formal, casual, neutral).
- Be context-aware and avoid generic replies (no "Got it" alone).
- Avoid emojis unless the tone is casual.

Reply:
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=60,
            temperature=0.4,
        )
    except Exception as e:
        print("❌ Groq request failed:", e)
        return random.choice([
            "Sorry, I couldn't generate a response right now.",
            "I’m having trouble responding — I’ll check this soon."
        ])

    
    content = None
    try:
        choices = getattr(response, "choices", None) or response.get("choices", None)
        if choices and len(choices) > 0:
            content = _extract_content_from_choice(choices[0])
    except Exception as e:
        print("❌ Error extracting choices:", e)
        content = None

    
    if not content:
        try:
            
            text_repr = str(response)
           
            m = re.search(r'["\']([^"\']{5,200})["\']', text_repr)
            if m:
                content = m.group(1)
        except Exception:
            content = None

    if not content:
     
        return random.choice([
            "Thanks — I’ll take a look and get back to you.",
            "I’ll review this shortly and reply.",
            "Appreciate the update; I’ll handle it."
        ])

    
    reply = _clean_reply(content, user_tone)
    return reply
