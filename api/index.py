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

wt_collection = db["alerts"]
structure_collection = db["structure_alerts"]

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==========================================================
# 1️⃣ WAVETREND WEBHOOK
# ==========================================================
@app.post("/api/webhook")
async def wavetrend_webhook(request: Request):
    data = await request.json()
    data["received_at"] = datetime.utcnow()
    wt_collection.insert_one(data)
    return JSONResponse({"status": "wavetrend_saved"})

# ==========================================================
# 2️⃣ STRUCTURE WEBHOOK (SUPPORT / BREAKOUT)
# ==========================================================
@app.post("/api/structure")
async def structure_webhook(request: Request):
    data = await request.json()
    data["received_at"] = datetime.utcnow()
    structure_collection.insert_one(data)
    return JSONResponse({"status": "structure_saved"})

# ==========================================================
# DASHBOARD 1 - WAVETREND
# ==========================================================
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    alerts = list(wt_collection.find().sort("timestamp", -1).limit(100))
    return templates.TemplateResponse("index.html", {
        "request": request,
        "alerts": alerts
    })

# ==========================================================
# DASHBOARD 2 - STRUCTURE ALERTS
# ==========================================================
@app.get("/structure", response_class=HTMLResponse)
def structure_dashboard(request: Request):
    alerts = list(structure_collection.find().sort("timestamp", -1).limit(100))
    return templates.TemplateResponse("structure.html", {
        "request": request,
        "alerts": alerts
    })