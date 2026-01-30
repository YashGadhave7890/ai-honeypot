from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os
import re
import time

app = FastAPI()

API_KEY = os.getenv("API_KEY", "changeme")

# -------- Request Model --------
class MessageRequest(BaseModel):
    conversation_id: str
    message: str
    history: list  # [{"role": "scammer"|"agent", "content": "..."}]

# -------- Simple Scam Detection (Hackathon Safe) --------
SCAM_KEYWORDS = [
    "otp", "urgent", "account blocked", "verify now",
    "bank update", "kyc", "suspend", "click link",
    "send money", "upi", "refund", "prize"
]

def detect_scam(message):
    score = sum(word in message.lower() for word in SCAM_KEYWORDS)
    return {
        "is_scam": score > 0,
        "confidence": min(0.5 + score * 0.1, 0.99),
        "reason": "Keyword-based detection"
    }

# -------- Agent Reply Generator --------
def generate_agent_reply():
    replies = [
        "Okay… I’m not very good with banking. What do I need to do exactly?",
        "Oh alright, where should I send it?",
        "Can you share the account details again?",
        "Is this your official company account?",
        "I didn’t understand… can you explain step by step?"
    ]
    return replies[int(time.time()) % len(replies)]

# -------- Intelligence Extraction --------
def extract_intel(text):
    urls = re.findall(r'https?://\S+', text)
    upi = re.findall(r'\b[\w.-]+@[\w.-]+\b', text)
    bank = re.findall(r'\b\d{9,18}\b', text)

    return {
        "bank_accounts": bank,
        "upi_ids": upi,
        "phone_numbers": re.findall(r'\b\d{10}\b', text),
        "emails": re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text),
        "phishing_links": urls,
        "payment_instructions": []
    }

# -------- Main Endpoint --------
@app.post("/honeypot")
def honeypot(req: MessageRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start = time.time()

    detection = detect_scam(req.message)

    if detection["is_scam"]:
        reply = generate_agent_reply()
        intel = extract_intel(req.message)
        agent_active = True
    else:
        reply = "Okay, thanks for the information."
        intel = {}
        agent_active = False

    return {
        "is_scam": detection["is_scam"],
        "confidence": detection["confidence"],
        "agent_activated": agent_active,
        "reply_message": reply,
        "engagement_metrics": {
            "turn_count": len(req.history) + 1,
            "response_time_ms": int((time.time() - start) * 1000)
        },
        "extracted_intelligence": intel
    }
