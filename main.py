from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import os, re, time

app = FastAPI()
API_KEY = os.getenv("API_KEY", "changeme")

class MessageRequest(BaseModel):
    conversation_id: str
    message: str
    history: list

SCAM_KEYWORDS = ["otp","urgent","account blocked","verify now","kyc","suspend","click link","send money","upi"]

def detect_scam(message):
    score = sum(word in message.lower() for word in SCAM_KEYWORDS)
    return {"is_scam": score > 0, "confidence": min(0.6 + score*0.1, 0.99)}

def generate_agent_reply():
    replies = [
        "Okay… I’m not very good with banking. What should I do first?",
        "Can you send the details again?",
        "Where do I send the money?",
        "Is this your company account?"
    ]
    return replies[int(time.time()) % len(replies)]

def extract_intel(text):
    return {
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text),
        "upi_ids": re.findall(r'\b[\w.-]+@[\w.-]+\b', text),
        "phishing_links": re.findall(r'https?://\S+', text)
    }

@app.post("/honeypot")
def honeypot(req: MessageRequest, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start = time.time()
    detection = detect_scam(req.message)

    if detection["is_scam"]:
        reply = generate_agent_reply()
        intel = extract_intel(req.message)
        active = True
    else:
        reply = "Okay, thank you for the information."
        intel = {}
        active = False

    return {
        "is_scam": detection["is_scam"],
        "confidence": detection["confidence"],
        "agent_activated": active,
        "reply_message": reply,
        "engagement_metrics": {
            "turn_count": len(req.history) + 1,
            "response_time_ms": int((time.time() - start) * 1000)
        },
        "extracted_intelligence": intel
    }
