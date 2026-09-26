output "site_url" {
  value = var.enable_custom_domain ? "https://${var.domain_name}" : "https://${aws_cloudfront_distribution.site.domain_name}"
}

output "cloudfront_domain" {
  description = "Cloudflare traffic CNAME target."
  value       = aws_cloudfront_distribution.site.domain_name
}

output "distribution_id" {
  value = aws_cloudfront_distribution.site.id
}

output "web_bucket_name" {
  value = aws_s3_bucket.web.id
}

output "lambda_function_name" {
  value = aws_lambda_function.api.function_name
}

output "api_endpoint" {
  value = aws_apigatewayv2_api.api.api_endpoint
}

output "certificate_validation_cname_name" {
  value = var.domain_name == "" ? null : one(aws_acm_certificate.site[0].domain_validation_options).resource_record_name
}

output "certificate_validation_cname_value" {
  value = var.domain_name == "" ? null : one(aws_acm_certificate.site[0].domain_validation_options).resource_record_value
}

output "certificate_arn" {
  value = var.domain_name == "" ? null : aws_acm_certificate.site[0].arn
}

output "github_deploy_role_arn" {
  value = aws_iam_role.github_deploy.arn
}
