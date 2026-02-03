from fastapi import FastAPI, Header, HTTPException, Request
import os, re, time

app = FastAPI()
API_KEY = os.getenv("API_KEY", "changeme")

SCAM_KEYWORDS = [
    "otp", "urgent", "account blocked", "verify now", "kyc",
    "suspend", "click link", "send money", "upi", "refund",
    "prize", "lottery", "reward"
]

def detect_scam(message: str):
    score = sum(word in message.lower() for word in SCAM_KEYWORDS)
    return score > 0, min(0.6 + score * 0.1, 0.99)

def generate_agent_reply():
    replies = [
        "Okay… I’m not very good with banking. What should I do first?",
        "Can you send the details again?",
        "Where exactly do I send the money?",
        "Is this your official company account?",
        "Sorry I didn’t understand… can you explain slowly?"
    ]
    return replies[int(time.time()) % len(replies)]

def extract_intel(text: str):
    return {
        "bank_accounts": re.findall(r'\b\d{9,18}\b', text),
        "upi_ids": re.findall(r'\b[\w.-]+@[\w.-]+\b', text),
        "phone_numbers": re.findall(r'\b\d{10}\b', text),
        "emails": re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text),
        "phishing_links": re.findall(r'https?://\S+', text),
        "payment_instructions": re.findall(r'(send|transfer|pay).{0,40}', text, re.I)
    }

@app.post("/honeypot")
async def honeypot(request: Request, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    start = time.time()

    try:
        body = await request.json()
    except:
        body = {}

    message = str(body.get("message", ""))
    history = body.get("history", [])
    if not isinstance(history, list):
        history = []

    is_scam, confidence = detect_scam(message)

    if is_scam:
        reply = generate_agent_reply()
        intel = extract_intel(message)
        agent_active = True
    else:
        reply = "Okay, thank you for the information."
        agent_active = False
        intel = {
            "bank_accounts": [],
            "upi_ids": [],
            "phone_numbers": [],
            "emails": [],
            "phishing_links": [],
            "payment_instructions": []
        }

    return {
        "is_scam": bool(is_scam),
        "confidence": float(confidence),
        "agent_activated": bool(agent_active),
        "reply_message": str(reply),
        "engagement_metrics": {
            "turn_count": int(len(history) + 1),
            "response_time_ms": int((time.time() - start) * 1000)
        },
        "extracted_intelligence": intel
    }
