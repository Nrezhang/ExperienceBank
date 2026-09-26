# ExperienceBank

A small React + Python full stack starter hosted on AWS. Terraform creates a private S3 bucket for the React build, CloudFront for HTTPS and routing, an API Gateway HTTP API, a Python Lambda, and a DynamoDB table.

## Where the resources run

`aws_region` in `infra/terraform.tfvars` selects where Lambda, API Gateway, DynamoDB, the S3 bucket, and logs live. The example uses `us-east-1` (N. Virginia). CloudFront is global and serves visitors from nearby edge locations. ACM issues the CloudFront certificate in `us-east-1`, even when the app resources use another region. Cloudflare manages DNS; the app itself runs on AWS.

Every resource uses the `project_name` prefix, so it can coexist with your other project in the same AWS account. This starter uses local Terraform state in `infra/`; back it up and move it to a remote backend before multiple people or CI run Terraform. The GitHub CD workflow publishes app code only and does not use Terraform state. Do not commit state files.

## Prerequisites

- Terraform 1.6+, Node.js 20+, npm, and AWS CLI.
- AWS access through IAM Identity Center or an IAM role, not the root user.
- A Cloudflare DNS zone for your domain.

Check the AWS account before deploying:

```bash
aws sts get-caller-identity
```

In this account, the current `default` CLI profile resolves to the root user. To create your first non-root administrator, sign in to the AWS console as root one last time, open **IAM Identity Center** in `us-east-1`, and choose **Enable with AWS Organizations**. Create your user, create an `AdministratorAccess` permission set, and assign your user to AWS account `767397760523`. Accept the invitation and set up MFA. Choose the *organization instance*: an account instance cannot grant AWS account access through permission sets. [AWS setup guide](https://docs.aws.amazon.com/singlesignon/latest/userguide/quick-start-default-idc.html)

Then configure a CLI profile and sign in:

```bash
aws configure sso --profile experience-bank
aws sso login --profile experience-bank
AWS_PROFILE=experience-bank aws sts get-caller-identity
```

The final command must show an assumed role ARN, not an ARN ending in `:root`. Run the deploy script with `AWS_PROFILE=experience-bank ./scripts/deploy.sh`; it refuses root credentials.

## Deploy the app

The local `infra/terraform.tfvars` is already set for `experiencebank.app` in `us-east-1`, with `enable_custom_domain = false`. It is ignored by Git. After non-root CLI access works, run:

```bash
AWS_PROFILE=experience-bank ./scripts/deploy.sh
```

Terraform will show the resource plan and ask you to approve it. The script builds React, uploads `web/dist` to S3, updates the Python Lambda, invalidates CloudFront, and prints the temporary `cloudfront.net` URL. AWS resources and traffic may incur charges; set an AWS Budget for this project.

For infrastructure changes, edit Terraform and run the script again from your trusted machine. For normal frontend or backend code changes after initial setup, GitHub CD publishes on successful CI for `main`.

## Connect a Cloudflare domain

Cloudflare is both your registrar and DNS provider. Keep the domain's nameservers on Cloudflare. You will add two separate CNAME records in Cloudflare **DNS → Records**:

1. After the initial Terraform apply, run `terraform -chdir=infra output -raw certificate_validation_cname_name` and `terraform -chdir=infra output -raw certificate_validation_cname_value`. Create a **CNAME** using those exact values. In Cloudflare's **Name** field, enter only the part before `experiencebank.app` if the dashboard automatically appends your zone (for example `_abc`, not `_abc.experiencebank.app.experiencebank.app`). Set **Proxy status: DNS only** (gray cloud). Leave this record in place for certificate renewal.
2. Check the certificate in AWS Certificate Manager in **N. Virginia (`us-east-1`)**. Wait until its status is **Issued**. The ARN is `terraform -chdir=infra output certificate_arn`.
3. Change `enable_custom_domain = true` in `infra/terraform.tfvars`, then run `AWS_PROFILE=experience-bank ./scripts/deploy.sh` again. CloudFront will attach the certificate and hostname.
4. Run `terraform -chdir=infra output -raw cloudfront_domain`. Add the website traffic CNAME in Cloudflare:

   | Type | Name | Target | Proxy |
   | --- | --- | --- | --- |
   | CNAME | `@` for `experiencebank.app` | the `dxxxxx.cloudfront.net` output | DNS only |

Cloudflare supports a CNAME at the root (`@`) through CNAME flattening. If the name already has an A, AAAA, or CNAME record, inspect it before replacing it so you do not interrupt another service. The certificate validation CNAME and traffic CNAME must both remain. You can choose Cloudflare proxying later, but DNS only makes CloudFront the direct HTTPS endpoint and keeps troubleshooting straightforward.

Check `https://experiencebank.app` after DNS and CloudFront finish propagating. The React page and `/api/items` should both work through the same hostname.

## CI and CD

`.github/workflows/ci.yml` tests Python, builds React, and validates Terraform on pull requests and pushes to `main`. After successful CI on `main`, `.github/workflows/deploy.yml` publishes the React build to S3 and the Python Lambda code, then waits for CloudFront invalidation. The deploy role uses GitHub OIDC temporary credentials and is restricted to this repository's immutable ID and `main` branch; no AWS access keys are stored in GitHub.

The CD workflow starts disabled until the AWS infrastructure exists. After the first Terraform apply, set these GitHub repository **Settings → Secrets and variables → Actions → Variables**:

| Variable | Value |
| --- | --- |
| `AWS_DEPLOY_ROLE_ARN` | `terraform -chdir=infra output -raw github_deploy_role_arn` |
| `AWS_DEPLOY_ENABLED` | `true` |

Once set, the next successful CI run on `main` triggers a deployment. You can also run **Deploy → Run workflow** in GitHub Actions. The existing GitHub OIDC provider in this AWS account is reused by Terraform.

## Local development

```bash
python3 -m unittest discover -s tests
npm --prefix web ci
npm --prefix web run build
```

For interactive local development, run `python3 backend/local.py` in one terminal and `npm --prefix web run dev` in another. Vite proxies `/api/items` to port 8000. The local API stores data in memory and resets when it stops.

## Notes

This is a public demo API without user accounts. Anyone who knows the URL can add or delete ideas. Add authentication before using it for private data. The GET handler scans the DynamoDB table and is intended for a small starter dataset; add pagination or a query based model as the app grows.

Terraform's local state is required to update or remove these resources. Back it up or configure a remote backend before using CI for infrastructure changes. The S3 bucket has `force_destroy = false`, so Terraform will not silently remove uploaded site files during destroy.
