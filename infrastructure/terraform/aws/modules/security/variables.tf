# ---------------------------------------------------------------------------------------------------------------------
# SECURITY MODULE VARIABLES
# Defines input variables for the AWS security module that configures IAM roles, KMS keys, 
# security groups, and WAF settings for the Freight Price Movement Agent infrastructure.
# ---------------------------------------------------------------------------------------------------------------------

variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  default     = "freight-price-agent"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod) used for resource naming"
  type        = string
  default     = "dev"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "The environment value must be one of: dev, staging, prod."
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# NETWORK CONFIGURATION VARIABLES
# ---------------------------------------------------------------------------------------------------------------------

variable "vpc_id" {
  description = "ID of the VPC where security resources will be created"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for resources in public subnets"
  type        = list(string)
  default     = []
}

variable "private_app_subnet_ids" {
  description = "List of private application subnet IDs for app tier resources"
  type        = list(string)
  default     = []
}

variable "private_data_subnet_ids" {
  description = "List of private data subnet IDs for data tier resources"
  type        = list(string)
  default     = []
}

# ---------------------------------------------------------------------------------------------------------------------
# SECURITY FEATURE TOGGLES
# ---------------------------------------------------------------------------------------------------------------------

variable "enable_waf" {
  description = "Whether to enable WAF for API protection"
  type        = bool
  default     = true
}

variable "enable_bastion" {
  description = "Whether to create a bastion host for secure SSH access"
  type        = bool
  default     = false
}

# ---------------------------------------------------------------------------------------------------------------------
# SECURITY CONFIGURATION VARIABLES
# ---------------------------------------------------------------------------------------------------------------------

variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the bastion host"
  type        = list(string)
  default     = ["0.0.0.0/0"]
  
  validation {
    condition     = length(var.allowed_cidr_blocks) > 0
    error_message = "At least one CIDR block must be specified."
  }
}

variable "waf_rate_limit" {
  description = "Rate limit for WAF rules to prevent API abuse"
  type        = number
  default     = 100
  
  validation {
    condition     = var.waf_rate_limit >= 10 && var.waf_rate_limit <= 1000
    error_message = "WAF rate limit must be between 10 and 1000 requests per minute."
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# RESOURCE TAGGING
# ---------------------------------------------------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all security resources"
  type        = map(string)
  default     = {}
}