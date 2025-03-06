# ------------------------------------------------------------------------
# General Project Variables
# ------------------------------------------------------------------------

variable "project_name" {
  description = "Name of the project used for resource naming and tagging"
  type        = string
  default     = "freight-price-agent"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod) used for resource naming and configuration"
  type        = string
  default     = "dev"
}

# ------------------------------------------------------------------------
# AWS Configuration Variables
# ------------------------------------------------------------------------

variable "aws_region" {
  description = "Primary AWS region for resource deployment"
  type        = string
  default     = "us-west-2"
}

variable "secondary_aws_region" {
  description = "Secondary AWS region for disaster recovery"
  type        = string
  default     = "us-east-1"
}

variable "allowed_account_ids" {
  description = "List of allowed AWS account IDs to prevent accidental deployment to wrong accounts"
  type        = list(string)
  default     = []
}

# ------------------------------------------------------------------------
# Networking Variables
# ------------------------------------------------------------------------

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use for multi-AZ deployment"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets (one per availability zone)"
  type        = list(string)
  default     = ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_app_subnet_cidrs" {
  description = "CIDR blocks for private application tier subnets (one per availability zone)"
  type        = list(string)
  default     = ["10.0.10.0/24", "10.0.11.0/24", "10.0.12.0/24"]
}

variable "private_data_subnet_cidrs" {
  description = "CIDR blocks for private data tier subnets (one per availability zone)"
  type        = list(string)
  default     = ["10.0.20.0/24", "10.0.21.0/24", "10.0.22.0/24"]
}

# ------------------------------------------------------------------------
# Database Variables
# ------------------------------------------------------------------------

variable "db_instance_class" {
  description = "Instance type for the RDS database"
  type        = string
  default     = "db.m5.large"
}

variable "db_allocated_storage" {
  description = "Allocated storage for the RDS database in GB"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum storage limit for autoscaling the RDS database in GB"
  type        = number
  default     = 500
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "freight_price_agent"
}

variable "db_username" {
  description = "Master username for the PostgreSQL database"
  type        = string
  default     = "postgres"
  sensitive   = true
}

variable "db_password" {
  description = "Master password for the PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Whether to enable Multi-AZ deployment for the RDS database"
  type        = bool
  default     = true
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "enable_deletion_protection" {
  description = "Whether to enable deletion protection for critical resources"
  type        = bool
  default     = true
}

# ------------------------------------------------------------------------
# Caching Variables
# ------------------------------------------------------------------------

variable "cache_node_type" {
  description = "Instance type for the ElastiCache Redis cluster"
  type        = string
  default     = "cache.m5.large"
}

variable "cache_num_nodes" {
  description = "Number of cache nodes in the ElastiCache Redis cluster"
  type        = number
  default     = 2
}

# ------------------------------------------------------------------------
# Compute (ECS) Variables
# ------------------------------------------------------------------------

variable "ecs_task_cpu" {
  description = "CPU units for ECS tasks (1024 = 1 vCPU)"
  type        = number
  default     = 1024
}

variable "ecs_task_memory" {
  description = "Memory for ECS tasks in MiB"
  type        = number
  default     = 2048
}

variable "app_min_capacity" {
  description = "Minimum number of tasks for the application services"
  type        = number
  default     = 2
}

variable "app_max_capacity" {
  description = "Maximum number of tasks for the application services"
  type        = number
  default     = 10
}

variable "app_cpu_threshold" {
  description = "CPU utilization threshold for scaling application services"
  type        = number
  default     = 70
}

# ------------------------------------------------------------------------
# Application Variables
# ------------------------------------------------------------------------

variable "app_image" {
  description = "Docker image for the application services"
  type        = string
}

variable "app_port" {
  description = "Port on which the application listens"
  type        = number
  default     = 8080
}

# ------------------------------------------------------------------------
# Tagging Variables
# ------------------------------------------------------------------------

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Project   = "Freight Price Movement Agent"
    ManagedBy = "Terraform"
  }
}