import random

def handler(event, context):
    app = event.get("application", {})
    
    # Simulate credit score (real case would call external API)
    credit_score = random.randint(550, 800)

    return {
        "application": app,
        "credit_score": credit_score
    }
