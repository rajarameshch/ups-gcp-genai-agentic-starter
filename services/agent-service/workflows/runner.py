import uuid
from typing import Dict, Any
from shared.shared.logging import configure_logging
from .workflows import WORKFLOWS

logger = configure_logging("workflow-runner")

async def run_workflow(workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
    trace_id = str(uuid.uuid4())
    wf = WORKFLOWS.get(workflow_id)
    if not wf:
        return {"status": "not_found", "trace_id": trace_id, "output": {"error": "Unknown workflow"}}

    try:
        out = await wf(inputs)
        return {"status": "ok", "trace_id": trace_id, "output": out}
    except Exception as e:
        logger.exception("Workflow failed")
        return {"status": "error", "trace_id": trace_id, "output": {"error": str(e)}}
