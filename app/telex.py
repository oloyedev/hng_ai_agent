from fastapi import Request
from .reply_agent import generate_reply
from .utils import detect_tone

async def handle_telex_message(request: Request):
    data = await request.json()
    message_text = data.get("text", "")

    # detect tone
    tone = detect_tone(message_text)

    # generate context-aware reply
    reply = generate_reply(message_text, user_tone=tone)

    return {
        "text": reply,
        "action": "send_message",
        "metadata": {"tone": tone}
    }
