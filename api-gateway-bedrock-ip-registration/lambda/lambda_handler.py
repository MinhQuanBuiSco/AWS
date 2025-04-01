import json
import boto3
import os

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['BEDROCK_REGION'])

def handler(event, context):
    try:
        # Parse the input from the API Gateway (e.g., query string or body)
        body = event.get('body')
        if not body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No input provided'})
            }

        # Parse the input (assuming JSON body)
        input_data = json.loads(body) if isinstance(body, str) else body
        user_prompt = input_data.get('prompt', 'Generate a short response')
        system_prompt = input_data.get('system_prompt', 'You are a helpful assistant.')

        # Invoke Bedrock model using converse API (Sonnet 3.5)
        model_id = os.environ['MODEL_ID']  # e.g., "anthropic.claude-3-sonnet-20240229-v1:0"
        response = bedrock_runtime.converse(
            modelId=model_id,
            system=[{"text": system_prompt}],  # Removed "type", use "text" directly as key
            messages=[{
                "role": "user",
                "content": [{"text": user_prompt}]  # Removed "type", use "text" directly as key
            }],
            inferenceConfig={
                "maxTokens": 1000,
                "temperature": 0.5,
                "topP": 0.9
            }
        )

        # Extract the response text
        response_content = response['output']['message']['content']
        response_text = response_content[0]['text'] if response_content and isinstance(response_content, list) and 'text' in response_content[0] else "No response generated"

        return {
            'statusCode': 200,
            'body': json.dumps({'response': response_text})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }