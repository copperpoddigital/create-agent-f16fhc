# VPC CIDR block
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
  
  validation {
    condition     = can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/[0-9]{1,2}$", var.vpc_cidr))
    error_message = "The vpc_cidr value must be a valid CIDR notation."
  }
}

# Availability Zones
variable "availability_zones" {
  description = "List of availability zones to deploy resources across"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# Public Subnet CIDR blocks
variable "public_subnet_cidrs" {
  description = "List of CIDR blocks for public subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

# Private Application Subnet CIDR blocks
variable "private_app_subnet_cidrs" {
  description = "List of CIDR blocks for private application tier subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

# Private Data Subnet CIDR blocks
variable "private_data_subnet_cidrs" {
  description = "List of CIDR blocks for private data tier subnets (one per AZ)"
  type        = list(string)
  default     = ["10.0.21.0/24", "10.0.22.0/24", "10.0.23.0/24"]
}

# VPC Flow Logs
variable "enable_vpc_flow_logs" {
  description = "Flag to enable or disable VPC flow logs for network monitoring and security analysis"
  type        = bool
  default     = true
}

# DNS Hostnames
variable "enable_dns_hostnames" {
  description = "Flag to enable or disable DNS hostnames in the VPC"
  type        = bool
  default     = true
}

# DNS Support
variable "enable_dns_support" {
  description = "Flag to enable or disable DNS support in the VPC"
  type        = bool
  default     = true
}

# Resource Tags
variable "tags" {
  description = "Map of tags to apply to all resources created by this module"
  type        = map(string)
  default     = {}
}