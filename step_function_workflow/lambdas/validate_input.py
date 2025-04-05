
def handler(event, context):
    required_fields = ["applicant_id", "name", "age", "income", "loan_amount"]
    app = event.get("application", {})

    missing = [f for f in required_fields if f not in app]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    
    if app.get("age", 0) < 18:
        raise ValueError("Applicant must be at least 18 years old")

    return {
        "application": app
    }
