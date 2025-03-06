# VPC and networking variables
variable "vpc_id" {
  description = "ID of the VPC where the RDS instance will be deployed"
  type        = string
}

variable "private_data_subnet_ids" {
  description = "List of private subnet IDs for the DB subnet group"
  type        = list(string)
}

# Database instance configuration
variable "db_instance_class" {
  description = "Instance type for the RDS database"
  type        = string
  default     = "db.m5.large"
}

variable "db_allocated_storage" {
  description = "Allocated storage size in GB for the database"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "Maximum storage size in GB for auto-scaling"
  type        = number
  default     = 500
}

variable "db_name" {
  description = "Name of the database to create"
  type        = string
  default     = "freight_price_agent"
}

variable "db_username" {
  description = "Master username for the database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Master password for the database"
  type        = string
  sensitive   = true
}

variable "db_multi_az" {
  description = "Whether to enable Multi-AZ deployment for high availability"
  type        = bool
  default     = true
}

# Backup and maintenance configuration
variable "db_backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 30
}

variable "db_backup_window" {
  description = "Daily time range during which backups are created"
  type        = string
  default     = "03:00-06:00"
}

variable "db_maintenance_window" {
  description = "Weekly time range during which system maintenance can occur"
  type        = string
  default     = "sun:06:00-sun:09:00"
}

# Database engine configuration
variable "db_engine_version" {
  description = "Version of PostgreSQL to use"
  type        = string
  default     = "13.7"
}

# Storage configuration
variable "db_storage_type" {
  description = "Type of storage to use (gp2, gp3, io1)"
  type        = string
  default     = "gp3"
}

variable "db_storage_encrypted" {
  description = "Whether to encrypt the database storage"
  type        = bool
  default     = true
}

# Protection settings
variable "db_deletion_protection" {
  description = "Whether to enable deletion protection"
  type        = bool
  default     = true
}

variable "db_skip_final_snapshot" {
  description = "Whether to skip final snapshot when database is deleted"
  type        = bool
  default     = false
}

variable "db_final_snapshot_identifier" {
  description = "Name of the final snapshot when database is deleted"
  type        = string
  default     = null
}

# Update behavior
variable "db_apply_immediately" {
  description = "Whether to apply changes immediately or during maintenance window"
  type        = bool
  default     = false
}

# Monitoring and insights
variable "db_monitoring_interval" {
  description = "Interval in seconds for enhanced monitoring"
  type        = number
  default     = 60
}

variable "db_performance_insights_enabled" {
  description = "Whether to enable Performance Insights"
  type        = bool
  default     = true
}

variable "db_performance_insights_retention_period" {
  description = "Retention period for Performance Insights data in days"
  type        = number
  default     = 7
}

# Version management
variable "db_auto_minor_version_upgrade" {
  description = "Whether to automatically upgrade minor versions"
  type        = bool
  default     = true
}

variable "db_allow_major_version_upgrade" {
  description = "Whether to allow major version upgrades"
  type        = bool
  default     = false
}

# Security
variable "app_security_group_ids" {
  description = "List of security group IDs for application tier that need database access"
  type        = list(string)
  default     = []
}

# Resource naming and tagging
variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
  default     = "freight-price-agent"
}

variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "tags" {
  description = "Map of tags to apply to all resources"
  type        = map(string)
  default     = {}
}