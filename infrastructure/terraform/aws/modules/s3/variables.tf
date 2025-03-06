# -------------------------------------------------------------
# Basic Configuration Variables
# -------------------------------------------------------------
variable "project_name" {
  description = "Name of the project used for S3 bucket naming"
  type        = string
  default     = "freight-price-agent"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod) used for S3 bucket naming"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, test, staging, or prod."
  }
}

variable "aws_region" {
  description = "AWS region for S3 bucket creation"
  type        = string
  default     = "us-west-2"
}

# -------------------------------------------------------------
# CSV Storage Lifecycle Configuration
# -------------------------------------------------------------
variable "csv_storage_expiration_days" {
  description = "Number of days after which CSV files should be deleted"
  type        = number
  default     = 1095  # 3 years retention
}

variable "csv_storage_standard_ia_transition_days" {
  description = "Number of days after which CSV files should transition to STANDARD_IA storage class"
  type        = number
  default     = 30
}

variable "csv_storage_glacier_transition_days" {
  description = "Number of days after which CSV files should transition to GLACIER storage class"
  type        = number
  default     = 90
}

# -------------------------------------------------------------
# Analysis Results Lifecycle Configuration
# -------------------------------------------------------------
variable "analysis_results_expiration_days" {
  description = "Number of days after which analysis results should be deleted"
  type        = number
  default     = 365  # 1 year retention
}

variable "analysis_results_standard_ia_transition_days" {
  description = "Number of days after which analysis results should transition to STANDARD_IA storage class"
  type        = number
  default     = 30
}

# -------------------------------------------------------------
# Archive Storage Lifecycle Configuration
# -------------------------------------------------------------
variable "archive_storage_expiration_days" {
  description = "Number of days after which archived data should be deleted"
  type        = number
  default     = 2555  # 7 years retention for compliance
}

variable "archive_storage_deep_archive_transition_days" {
  description = "Number of days after which archived data should transition to DEEP_ARCHIVE storage class"
  type        = number
  default     = 180
}

# -------------------------------------------------------------
# Security Configuration
# -------------------------------------------------------------
variable "enable_versioning" {
  description = "Whether to enable versioning for S3 buckets"
  type        = bool
  default     = true
}

variable "enable_encryption" {
  description = "Whether to enable server-side encryption for S3 buckets"
  type        = bool
  default     = true
}

variable "block_public_access" {
  description = "Whether to block all public access to S3 buckets"
  type        = bool
  default     = true
}

# -------------------------------------------------------------
# Tagging Configuration
# -------------------------------------------------------------
variable "tags" {
  description = "Tags to apply to all S3 resources"
  type        = map(string)
  default     = {}
}