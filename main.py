"""Customer Churn Prediction & Analytics API."""
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from starlette.middleware.cors import CORSMiddleware

from local_ai import (
    LANGUAGES,
    chat_response,
    detect_language,
    recommendations_response,
)
from ml_engine import DEFAULT_CSV, engine, init_engine
from reports import build_excel_export, build_pdf_report

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
JWT_SECRET = os.environ["JWT_SECRET"]
ADMIN_EMAIL = os.environ["ADMIN_EMAIL"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]
EMERGENT_LLM_KEY = os.environ["EMERGENT_LLM_KEY"]

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

app = FastAPI(title="Churn Analytics API")
api = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("churn")


# ============ MODELS ============
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class PredictIn(BaseModel):
    CreditScore: float = 600
    Age: float = 35
    Tenure: float = 5
    Balance: float = 0
    NumOfProducts: float = 1
    HasCrCard: float = 1
    IsActiveMember: float = 1
    EstimatedSalary: float = 50000
    Geography: str = "France"
    Gender: str = "Male"


class AIRecRequest(BaseModel):
    profile: dict
    prediction: dict


class ChatIn(BaseModel):
    message: str
    session_id: str | None = None


# ============ AUTH ============
def make_token(email: str, role: str = "admin") -> str:
    payload = {
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


async def current_user(authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return data
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token") from None


async def ensure_default_admin():
    existing = await db.users.find_one({"email": ADMIN_EMAIL})
    if not existing:
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
        await db.users.insert_one({
            "id": str(uuid.uuid4()),
            "email": ADMIN_EMAIL,
            "password": hashed,
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Default admin user created: %s", ADMIN_EMAIL)


@api.post("/auth/login")
async def login(body: LoginIn):
    user = await db.users.find_one({"email": body.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not bcrypt.checkpw(body.password.encode(), user["password"].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_token(user["email"], user.get("role", "admin"))
    return {"token": token, "email": user["email"], "role": user.get("role", "admin")}


@api.post("/auth/register")
async def register(body: RegisterIn):
    if await db.users.find_one({"email": body.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()
    await db.users.insert_one({
        "id": str(uuid.uuid4()),
        "email": body.email,
        "password": hashed,
        "role": "admin",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    token = make_token(body.email)
    return {"token": token, "email": body.email, "role": "admin"}


@api.get("/auth/me")
async def me(user=Depends(current_user)):
    return {"email": user["email"], "role": user.get("role", "admin")}


# ============ DATASET ============
@api.get("/dataset/status")
async def dataset_status():
    if engine.df is None:
        return {"loaded": False}
    return {"loaded": True, "source": engine.source, "rows": int(len(engine.df)), "columns": int(len(engine.df.columns))}


@api.get("/dataset/preview")
async def dataset_preview(n: int = 10):
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.preview(n)


@api.get("/dataset/cleaning")
async def dataset_cleaning():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.cleaning_summary()


@api.get("/dataset/history")
async def dataset_history(user=Depends(current_user)):
    # user unused but required for auth
    _ = user
    docs = await db.dataset_uploads.find({}, {"_id": 0}).sort("uploaded_at", -1).to_list(100)
    return docs


@api.post("/dataset/upload")
async def dataset_upload(file: UploadFile = File(...), user=Depends(current_user)):
    content = await file.read()
    path = DEFAULT_CSV.parent / file.filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    try:
        engine.load_csv(path, source_label=file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to load CSV: {e}") from e
    doc = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "rows": int(len(engine.df)),
        "size_bytes": len(content),
        "uploaded_by": user["email"],
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "metrics": engine.metrics,
    }
    await db.dataset_uploads.insert_one(doc)
    return {"ok": True, "rows": int(len(engine.df)), "metrics": engine.metrics}


# ============ ANALYTICS ============
@api.get("/analytics/kpis")
async def analytics_kpis():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.kpis()


@api.get("/analytics/monthly-trend")
async def analytics_monthly():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.monthly_trend()


@api.get("/analytics/distribution/{kind}")
async def analytics_distribution(kind: str):
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    if kind == "age":
        return engine.age_groups()
    if kind == "gender":
        return engine.distribution("Gender")
    if kind == "geography":
        return engine.distribution("Geography")
    if kind == "credit":
        return engine.credit_buckets()
    if kind == "balance":
        return engine.balance_buckets()
    if kind == "tenure":
        return engine.tenure_dist()
    if kind == "products":
        return engine.products_dist()
    raise HTTPException(status_code=400, detail="Unknown distribution")


@api.get("/analytics/correlation")
async def analytics_correlation():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.correlation()


@api.get("/analytics/feature-importance")
async def feature_importance():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.feature_importance


@api.get("/analytics/segmentation")
async def segmentation():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.segmentation()


@api.get("/analytics/model-metrics")
async def model_metrics():
    return engine.metrics


# ============ PREDICTION ============
@api.post("/predict")
async def predict(body: PredictIn):
    if engine.model is None:
        raise HTTPException(status_code=400, detail="Model not trained")
    result = engine.predict_single(body.model_dump())
    log = {
        "id": str(uuid.uuid4()),
        "input": body.model_dump(),
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    await db.prediction_logs.insert_one({**log})
    return result


@api.get("/predict/logs")
async def prediction_logs(limit: int = 50, user=Depends(current_user)):
    _ = user  # user unused but required for auth
    docs = await db.prediction_logs.find({}, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    return docs


@api.get("/customers/risk")
async def high_risk(limit: int = 50):
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    return engine.high_risk_customers(limit)


@api.get("/customers/{customer_id}")
async def customer_detail(customer_id: int):
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    data = engine.find_customer(customer_id)
    if not data:
        raise HTTPException(status_code=404, detail="Customer not found")
    return data




# ============ AI RECOMMENDATIONS & CHATBOT (Local AI + Multi-lingual) ============
@api.get("/ai/languages")
async def ai_languages():
    """Return supported languages."""
    return {"languages": LANGUAGES, "default": "en"}


@api.post("/ai/recommendations")
async def ai_recommendations(
    body: AIRecRequest,
    accept_language: str = Header(None),
):
    lang = detect_language({"accept-language": accept_language})
    data = await recommendations_response(body.profile, body.prediction, lang)
    return data


@api.post("/ai/chat")
async def ai_chat(
    body: ChatIn,
    accept_language: str = Header(None),
):
    session = body.session_id or str(uuid.uuid4())
    kpis = engine.kpis() if engine.df is not None else {}
    lang = detect_language({"accept-language": accept_language})
    text = await chat_response(body.message, kpis, lang)
    await db.chat_history.insert_one({
        "id": str(uuid.uuid4()),
        "session_id": session,
        "user": body.message,
        "assistant": text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    return {"session_id": session, "response": text}


# ============ EMAIL ALERTS (simulated) ============
@api.post("/alerts/send")
async def send_alert(body: dict, user=Depends(current_user)):
    _ = user  # user unused but required for auth
    doc = {
        "id": str(uuid.uuid4()),
        "customer_id": body.get("customer_id"),
        "email": body.get("email", "customer@bank.com"),
        "message": body.get("message", "High churn risk alert"),
        "status": "SIMULATED-SENT",
        "sent_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.alerts.insert_one({**doc})
    return doc


@api.get("/alerts")
async def list_alerts(user=Depends(current_user)):
    _ = user  # user unused but required for auth
    return await db.alerts.find({}, {"_id": 0}).sort("sent_at", -1).to_list(100)


# ============ REPORTS ============
@api.get("/reports/pdf")
async def report_pdf():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    buf = build_pdf_report(engine)
    return StreamingResponse(
        buf, media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="churn_report.pdf"'},
    )


@api.get("/reports/excel")
async def report_excel():
    if engine.df is None:
        raise HTTPException(status_code=400, detail="Dataset not loaded")
    buf = build_excel_export(engine)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="churn_dashboard.xlsx"'},
    )


@api.get("/")
async def root():
    return {"service": "churn-analytics", "status": "ok"}


# ============ BOOTSTRAP ============
app.include_router(api)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_start():
    await ensure_default_admin()
    try:
        init_engine()
        if engine.df is not None:
            logger.info("Loaded dataset rows=%s metrics=%s", len(engine.df), engine.metrics)
    except Exception:
        logger.exception("Failed to initialize ML engine")


@app.on_event("shutdown")
async def on_stop():
    client.close()
