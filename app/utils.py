def detect_tone(message: str) -> str:
    """
    Basic tone detection from text.
    Later, you can enhance this with NLP or sentiment models.
    """
    casual_keywords = ["hey", "yo", "bro", "dude", "lol", "thanks", "cool"]
    formal_keywords = ["regards", "sincerely", "dear", "please", "thank you"]

    msg = message.lower()

    if any(word in msg for word in casual_keywords):
        return "casual"
    elif any(word in msg for word in formal_keywords):
        return "formal"
    else:
        return "neutral"
