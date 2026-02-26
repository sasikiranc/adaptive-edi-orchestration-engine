from fastapi import FastAPI
from app.routing.rule_engine import RuleEngine
from app.normalizer.normalizer import build_canonical_message
import json
import numpy as np
from app.core.logging_config import setup_logging
import uuid
from fastapi import Request, Depends
from app.core.security import validate_token
from app.api.routers import rules, governance
from app.services.config_cache import load_config

setup_logging()

app = FastAPI()

app.include_router(rules.router)
app.include_router(governance.router)

@app.post("/route")
def route_message(request: Request, payload: dict, format_hint: str, user=Depends(validate_token)):
    try:
        canonical = build_canonical_message(payload,format_hint)
        engine = RuleEngine()
        request_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request_id = request.state.request_id
        result = engine.route_with_ai(canonical,request_id)
        return result
    except ValueError as e:
        return f"Error in payload: {e}"

@app.on_event("startup")
def startup():
    setup_logging()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    request_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Correlation-ID"] = request_id
    return response

@app.get("/metrics")
def metrics():
    return {
        "total_requests": total_requests,
        "rule_routes": rule_count,
        "ai_routes": ai_count,
        "manual_routes": manual_count
    }

@app.on_event("startup")
def startup_event():
    load_config()