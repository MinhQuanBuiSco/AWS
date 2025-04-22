def handler(event, context):
    app = event.get("application", {})
    credit_score = event.get("credit_score", 600)
    income = app.get("income", 0)
    loan_amount = app.get("loan_amount", 0)

    # Simple rule: if credit is good and income covers loan, it's low risk
    if credit_score >= 700 and income >= loan_amount * 2:
        risk = "low"
    else:
        risk = "high"

    return {"application": app, "credit_score": credit_score, "risk": risk}
