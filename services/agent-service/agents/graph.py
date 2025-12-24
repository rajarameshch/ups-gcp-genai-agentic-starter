import uuid
from typing import Dict, Any, Literal

from langgraph.graph import StateGraph, END
from shared.shared.logging import configure_logging
from .llm import get_llm
from .tools import track_shipment, create_claim, lookup_policy

logger = configure_logging("agent-graph")

# --- State schema (plain dict for simplicity) ---
# keys: message, reply, route, tool_result, trace_id, metadata, session_id

SYSTEM_PROMPT = """You are an enterprise UPS assistant.
- Be concise and action-oriented.
- If user asks about a shipment, request/confirm tracking ID and use tools.
- If user reports an issue, propose next steps and optionally create a claim.
- If a policy question, consult policy tool.
- Do not hallucinate UPS internal info; if uncertain, say what you need."""


async def router(state: Dict[str, Any]) -> Dict[str, Any]:
    msg = (state.get("message") or "").lower()
    trace_id = state.get("trace_id") or str(uuid.uuid4())
    state["trace_id"] = trace_id

    # Very simple routing. Replace with LLM-based intent classifier.
    if "claim" in msg or "lost" in msg or "damaged" in msg:
        state["route"] = "claims"
    elif "policy" in msg or "refund" in msg or "insurance" in msg:
        state["route"] = "policy"
    elif "track" in msg or "tracking" in msg or "where is" in msg:
        state["route"] = "tracking"
    else:
        state["route"] = "general"
    return state


async def general_node(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()
    reply = await llm.complete(SYSTEM_PROMPT, [{"role": "user", "content": state.get("message", "")}])
    state["reply"] = reply
    return state


async def tracking_node(state: Dict[str, Any]) -> Dict[str, Any]:
    # naive extraction of tracking id
    msg = state.get("message", "")
    tokens = [t.strip(".,!?") for t in msg.split()]
    tracking_id = None
    for t in tokens:
        if len(t) >= 10 and any(c.isdigit() for c in t):
            tracking_id = t
            break
    if not tracking_id:
        state["reply"] = "Please share the tracking number (e.g., 1Z...)."
        return state

    result = await track_shipment(tracking_id)
    state["tool_result"] = result
    state["reply"] = f"Tracking {tracking_id}: {result['status']}. Estimated delivery: {result['eta']}."
    return state


async def claims_node(state: Dict[str, Any]) -> Dict[str, Any]:
    msg = state.get("message", "")
    # crude extraction
    tracking_id = next((t.strip(".,!?") for t in msg.split() if len(t) >= 10 and any(c.isdigit() for c in t)), "UNKNOWN")
    result = await create_claim(tracking_id=tracking_id, issue="Customer reported shipment issue", contact_email="customer@example.com")
    state["tool_result"] = result
    state["reply"] = (
        f"I can help file a claim. Draft claim created: {result['claim_id']} for tracking {result['tracking_id']}. "
        "Please confirm contact email and issue details to submit."
    )
    return state


async def policy_node(state: Dict[str, Any]) -> Dict[str, Any]:
    topic = state.get("message", "")
    result = await lookup_policy(topic)
    state["tool_result"] = result
    state["reply"] = f"Policy summary (stub): {result['summary']}"
    return state


def build_graph():
    sg = StateGraph(dict)

    sg.add_node("router", router)
    sg.add_node("general", general_node)
    sg.add_node("tracking", tracking_node)
    sg.add_node("claims", claims_node)
    sg.add_node("policy", policy_node)

    sg.set_entry_point("router")

    def route_decider(state: Dict[str, Any]) -> Literal["general", "tracking", "claims", "policy"]:
        return state.get("route", "general")

    sg.add_conditional_edges(
        "router",
        route_decider,
        {
            "general": "general",
            "tracking": "tracking",
            "claims": "claims",
            "policy": "policy",
        },
    )

    for n in ["general", "tracking", "claims", "policy"]:
        sg.add_edge(n, END)

    return sg.compile()
