from typing import List, Optional
from uuid import uuid4
import json
from .a2a import (
    A2AMessage, TaskResult, TaskStatus, Artifact,
    MessagePart, MessageConfiguration
)
from .groq import analyze_contract


async def process_contract_messages(
    messages: List[A2AMessage],
    context_id: Optional[str] = None,
    task_id: Optional[str] = None,
    config: Optional[MessageConfiguration] = None
) -> TaskResult:
    """Process messages and return structured contract analysis."""

    context_id = context_id or str(uuid4())
    task_id = task_id or str(uuid4())

    # Extract user’s text
    user_message = messages[-1]
    contract_text = ""
    for part in user_message.parts:
        if part.kind == "text":
            contract_text = (part.text or "").strip()
            break

    if not contract_text:
        raise ValueError("No contract text provided")

    # Analyze via Groq
    raw_result = await analyze_contract(contract_text)

    # Parse structured JSON
    try:
        parsed = json.loads(raw_result)
        contract_type = parsed.get("contract_type", "Unknown")
        simplified_summary = parsed.get("simplified_summary", "")
        recommendations = parsed.get("recommendations", "")
        ambiguous_terms = parsed.get("ambiguous_terms", [])
        risk_clauses = parsed.get("risk_clauses", [])
    except Exception:
        # fallback if model returns plain text
        contract_type = "Unknown"
        simplified_summary = raw_result
        recommendations = ""
        ambiguous_terms = []
        risk_clauses = []

    # Build human-readable report
    readable_report = (
        f"**Contract Type:** {contract_type}\n\n"
        f"**Simplified Summary:**\n{simplified_summary}\n\n"
        f"**Ambiguous Terms:** {', '.join(ambiguous_terms) if ambiguous_terms else 'None found'}\n\n"
        f"**Risk Clauses:** {', '.join(risk_clauses) if risk_clauses else 'None found'}\n\n"
        f"**Recommendations:**\n{recommendations}"
    )

    # Build A2A-compatible response
    response_message = A2AMessage(
        role="agent",
        parts=[MessagePart(kind="text", text=readable_report)],
        taskId=task_id
    )

    artifacts = [
        Artifact(name="classification", parts=[MessagePart(kind="text", text=contract_type)]),
        Artifact(name="analysis", parts=[MessagePart(kind="text", text=raw_result)])
    ]

    history = messages + [response_message]

    return TaskResult(
        id=task_id,
        contextId=context_id,
        status=TaskStatus(state="completed", message=response_message),
        artifacts=artifacts,
        history=history
    )
