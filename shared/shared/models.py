from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatResponse(BaseModel):
    reply: str
    session_id: Optional[str] = None
    trace_id: Optional[str] = None

class WorkflowRunRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = Field(default_factory=dict)

class WorkflowRunResponse(BaseModel):
    workflow_id: str
    status: str
    output: Dict[str, Any] = Field(default_factory=dict)
    trace_id: Optional[str] = None
