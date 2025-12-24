from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from shared.shared.logging import configure_logging

logger = configure_logging("retrieval-service")

app = FastAPI(title="UPS Retrieval Service", version="0.1.0")

class Doc(BaseModel):
    id: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

# In-memory store for demo. Replace with Vertex AI Search, AlloyDB, BigQuery, or a vector DB.
DOC_STORE: Dict[str, Doc] = {}

@app.get("/healthz")
def healthz():
    return {"ok": True, "docs": len(DOC_STORE)}

@app.post("/v1/ingest")
def ingest(payload: Dict[str, Any]):
    docs = payload.get("documents", [])
    count = 0
    for d in docs:
        doc = Doc(**d)
        DOC_STORE[doc.id] = doc
        count += 1
    return {"ingested": count}

@app.post("/v1/retrieve")
def retrieve(payload: Dict[str, Any]):
    query = (payload.get("query") or "").lower()
    # naive keyword match
    hits: List[Doc] = []
    for doc in DOC_STORE.values():
        if query and query in doc.text.lower():
            hits.append(doc)
    return {"hits": [h.model_dump() for h in hits[:5]]}
