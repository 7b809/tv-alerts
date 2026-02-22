import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# ==========================
# LOAD ENV
# ==========================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["tradingview"]
collection = db["alerts"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==========================
# WEBHOOK ENDPOINT
# ==========================
@app.post("/api/webhook")
async def webhook(request: Request):
    data = await request.json()

    data["received_at"] = datetime.utcnow()

    collection.insert_one(data)

    return JSONResponse({"status": "saved"})

# ==========================
# FETCH ALERTS API
# ==========================
@app.get("/api/alerts")
def get_alerts():
    alerts = list(collection.find().sort("timestamp", -1).limit(100))
    for a in alerts:
        a["_id"] = str(a["_id"])
    return alerts

# ==========================
# DASHBOARD PAGE
# ==========================
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    alerts = list(collection.find().sort("timestamp", -1).limit(100))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "alerts": alerts
    })