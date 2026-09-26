variable "project_name" {
  description = "Unique resource prefix, separate from your other AWS projects."
  type        = string
  default     = "experience-bank"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,30}$", var.project_name))
    error_message = "Use 3-31 lowercase letters, digits, or hyphens, starting with a letter."
  }
}

variable "aws_region" {
  description = "Region for the API, Lambda, DynamoDB, and S3 bucket."
  type        = string
  default     = "us-east-1"
}

variable "domain_name" {
  description = "Optional full hostname, such as app.example.com."
  type        = string
  default     = ""
}

variable "enable_custom_domain" {
  description = "Set true only after ACM reports the certificate as Issued."
  type        = bool
  default     = false
}
