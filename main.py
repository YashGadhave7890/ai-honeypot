from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import os, re, time

app = FastAPI()
API_KEY = os.getenv("API_KEY", "changeme")

# -------- Request Model (Flexible to avoid 422 errors) --------
class MessageRequest(BaseModel):
    conversation_id: Optional[str] = "default"
    message: Optional[str] = ""
    history: Optional[List[Dict]] = []

# -------- Scam Detection --------
SCAM_KEYWORDS = [
    "otp", "urgent", "account blocked", "verify now", "kyc",
    "suspend", "click link", "send money", "upi", "refund",
    "prize", "lottery", "reward"
]

def detect_scam(message: str):
    score = sum(word in message.lower() for word in SCAM_KEYWORDS)
    return {
        "is_scam": score > 0,
        "confidence": min(0.6 + score * 0.1, 0.99)
    }

# -------- Agent Reply Generator --------
def generate_agent_reply():
    replies = [
        "Okay… I’m not very good with banking. What should I do first?",
        "Can you send the details again?",
        "Where exactly do I send the money?",
        "Is this your official company account?",
        "Sorry I didn’t understand… can you explain slowly?"
    ]
    return replies[int(time.time()) % len(replies)]

# -------- Intelligence Extraction --------
def extract_intel(text: str):
    return {
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text),
        "upi_ids": re.findall(r'\b[\w.-]+@[\w.-]+\b', text),
        "phone_numbers": re.findall(r'\b\d{10}\b', text),
        "emails": re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text),
        "phishing_links": re.findall(r'https?://\S+', text),
        "payment_instructions": re.findall(r'(send|transfer|pay).{0,40}', text, re.I)
    }

# -------- Honeypot Endpoint --------
@app.post("/honeypot")
def honeypot(req: MessageRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start = time.time()

    message = req.message or ""
    history = req.history or []

    detection = detect_scam(message)

    if detection["is_scam"]:
        reply = generate_agent_reply()
        intel = extract_intel(message)
        agent_active = True
    else:
        reply = "Okay, thank you for the information."
        intel = {}
        agent_active = False

    return {
        "is_scam": detection["is_scam"],
        "confidence": detection["confidence"],
        "agent_activated": agent_active,
        "reply_message": reply,
        "engagement_metrics": {
            "turn_count": len(history) + 1,
            "response_time_ms": int((time.time() - start) * 1000)
        },
        "extracted_intelligence": intel
    }
