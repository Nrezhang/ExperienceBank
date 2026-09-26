#!/usr/bin/env bash
set -euo pipefail

command -v terraform >/dev/null || { echo "Install Terraform first." >&2; exit 1; }
command -v aws >/dev/null || { echo "Install AWS CLI first." >&2; exit 1; }
command -v npm >/dev/null || { echo "Install Node.js/npm first." >&2; exit 1; }

CALLER_ARN=$(aws sts get-caller-identity --query Arn --output text)
if [[ "$CALLER_ARN" == *":root" ]]; then
  echo "The active AWS credentials are for the root user. Configure an IAM Identity Center or assumed-role profile before deploying." >&2
  exit 1
fi

terraform -chdir=infra init
terraform -chdir=infra apply

npm --prefix web ci
npm --prefix web run build

WEB_BUCKET=$(terraform -chdir=infra output -raw web_bucket_name)
DISTRIBUTION_ID=$(terraform -chdir=infra output -raw distribution_id)
SITE_URL=$(terraform -chdir=infra output -raw site_url)
LAMBDA_FUNCTION=$(terraform -chdir=infra output -raw lambda_function_name)
API_TMP_DIR=$(mktemp -d /private/tmp/experiencebank-api.XXXXXX)
API_ZIP="$API_TMP_DIR/api.zip"
trap 'rm -f "$API_ZIP"; rmdir "$API_TMP_DIR"' EXIT
zip -j "$API_ZIP" backend/app.py >/dev/null

aws s3 sync web/dist/ "s3://$WEB_BUCKET" --delete
aws lambda update-function-code --function-name "$LAMBDA_FUNCTION" --zip-file "fileb://$API_ZIP" >/dev/null
aws lambda wait function-updated --function-name "$LAMBDA_FUNCTION"
aws cloudfront create-invalidation --distribution-id "$DISTRIBUTION_ID" --paths "/*" >/dev/null

echo "Deployed: $SITE_URL"
