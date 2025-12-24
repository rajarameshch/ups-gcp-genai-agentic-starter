from fastapi import FastAPI
from shared.shared.models import ChatRequest, ChatResponse, WorkflowRunRequest, WorkflowRunResponse
from shared.shared.logging import configure_logging
from agents.graph import build_graph
from workflows.runner import run_workflow

logger = configure_logging("agent-service")

app = FastAPI(title="UPS Agent Service", version="0.1.0")
graph = build_graph()

@app.get("/healthz")
def healthz():
    return {"ok": True, "graph": "ready"}

@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Graph returns a dict state
    state = {"message": req.message, "session_id": req.session_id, "metadata": req.metadata}
    out = await graph.ainvoke(state)
    return ChatResponse(reply=out.get("reply", ""), session_id=req.session_id, trace_id=out.get("trace_id"))

@app.post("/v1/workflows/run", response_model=WorkflowRunResponse)
async def workflow_run(req: WorkflowRunRequest):
    out = await run_workflow(req.workflow_id, req.inputs)
    return WorkflowRunResponse(
        workflow_id=req.workflow_id,
        status=out.get("status", "unknown"),
        output=out.get("output", {}),
        trace_id=out.get("trace_id"),
    )
