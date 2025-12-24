from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
from shared.shared.models import ChatRequest, ChatResponse, WorkflowRunRequest, WorkflowRunResponse
from shared.shared.logging import configure_logging

logger = configure_logging("api-gateway")

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8081")
RETRIEVAL_SERVICE_URL = os.getenv("RETRIEVAL_SERVICE_URL", "http://localhost:8082")

app = FastAPI(title="UPS GenAI API Gateway", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth hook scaffold (enterprise) ---
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # TODO: validate JWT / mTLS / IAP headers as required by UPS enterprise standards
    # Example:
    # token = request.headers.get("Authorization", "")
    # if not token: raise HTTPException(401, "Unauthorized")
    return await call_next(request)

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{AGENT_SERVICE_URL}/v1/chat", json=req.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return ChatResponse(**r.json())

@app.post("/v1/workflows/run", response_model=WorkflowRunResponse)
async def run_workflow(req: WorkflowRunRequest):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{AGENT_SERVICE_URL}/v1/workflows/run", json=req.model_dump())
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return WorkflowRunResponse(**r.json())

@app.post("/v1/docs/ingest")
async def ingest(payload: dict):
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(f"{RETRIEVAL_SERVICE_URL}/v1/ingest", json=payload)
        if r.status_code != 200:
            raise HTTPException(r.status_code, r.text)
        return r.json()
