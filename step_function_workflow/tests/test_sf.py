import boto3
import json

sf = boto3.client('stepfunctions', region_name='ap-northeast-1')

response = sf.start_execution(
    stateMachineArn='arn:aws:states:ap-northeast-1:795684990677:stateMachine:LoanApplicationStateMachine0F382742-gotJmE4S4PTT',
    input=json.dumps({
        "application": {
            "applicant_id": "123456",
            "name": "Alice Johnson",
            "age": 34,
            "income": 85000,
            "loan_amount": 25000,
            "loan_purpose": "Car",
            "employment_status": "Full-time"
        }
    })
)

print(response)