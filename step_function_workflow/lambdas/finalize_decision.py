def handler(event, context):
    app = event.get("application", {})
    risk = event.get("risk", "high")

    if risk == "low":
        decision = "approved"
    else:
        decision = "pending_manual_review"

    return {
        "applicant_id": app.get("applicant_id"),
        "decision": decision,
        "risk": risk,
        "credit_score": event.get("credit_score")
    }
