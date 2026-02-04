from fastapi import FastAPI, Header, HTTPException, Request
import os, time

app = FastAPI()
API_KEY = os.getenv("API_KEY", "changeme")

SCAM_KEYWORDS = [
    "otp", "urgent", "account blocked", "verify", "kyc",
    "suspend", "click", "send money", "upi", "refund",
    "prize", "lottery"
]

def detect_scam(text: str) -> bool:
    return any(word in text.lower() for word in SCAM_KEYWORDS)

def generate_reply(history_len: int) -> str:
    replies = [
        "Why is my account being suspended?",
        "I didn’t do anything wrong. What happened?",
        "Can you explain what I need to do?",
        "Is this from my bank officially?",
        "I am confused, please guide me."
    ]
    return replies[history_len % len(replies)]

@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    try:
        body = await request.json()
    except:
        body = {}

    message_obj = body.get("message", {})
    message_text = message_obj.get("text", "")
    history = body.get("conversationHistory", [])

    is_scam = detect_scam(message_text)

    if is_scam:
        reply = generate_reply(len(history))
    else:
        reply = "Okay, thank you for the information."

    return {
        "status": "success",
        "reply": reply
    }
