import json
import os

from openai import OpenAI


def handler(event, context):
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    user_message = json.loads(event["body"])["message"]

    response = client.responses.create(model="gpt-4o", input=user_message)

    return {"statusCode": 200, "body": json.dumps({"reply": response.output_text})}
