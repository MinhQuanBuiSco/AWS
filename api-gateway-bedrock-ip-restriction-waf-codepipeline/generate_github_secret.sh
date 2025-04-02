export $(cat .env | xargs)

aws secretsmanager create-secret \
  --name github-token \
  --description "GitHub token for CodePipeline"

aws secretsmanager put-secret-value \
  --secret-id github-token \
  --secret-string "$GITHUB_TOKEN"

aws ssm put-parameter --name "/my/ip" --value "$YOUR_IP_ADDRESS" --type String
