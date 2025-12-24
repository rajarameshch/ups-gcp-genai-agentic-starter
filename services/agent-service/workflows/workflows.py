from typing import Dict, Any
from agents.tools import track_shipment, create_claim, lookup_policy

async def shipment_exception_triage(inputs: Dict[str, Any]) -> Dict[str, Any]:
    tracking_id = inputs.get("tracking_id")
    if not tracking_id:
        return {"next": "need_tracking_id"}

    tracking = await track_shipment(tracking_id)
    status = tracking.get("status", "")
    if "Exception" in status:
        policy = await lookup_policy("exception handling")
        return {"tracking": tracking, "policy": policy, "recommendation": "Offer proactive options and create claim if needed."}
    return {"tracking": tracking, "recommendation": "No exception detected. Provide ETA and latest scan."}

async def claims_intake(inputs: Dict[str, Any]) -> Dict[str, Any]:
    tracking_id = inputs.get("tracking_id", "UNKNOWN")
    issue = inputs.get("issue", "unspecified")
    email = inputs.get("contact_email", "customer@example.com")
    claim = await create_claim(tracking_id, issue, email)
    return {"claim": claim, "next": "collect_supporting_docs"}

async def billing_refund_policy(inputs: Dict[str, Any]) -> Dict[str, Any]:
    topic = inputs.get("topic", "refund policy")
    return {"policy": await lookup_policy(topic)}

WORKFLOWS = {
    "shipment_exception_triage": shipment_exception_triage,
    "claims_intake": claims_intake,
    "billing_refund_policy": billing_refund_policy,
}
