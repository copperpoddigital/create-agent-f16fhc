variable "vpc_id" {
  description = "The ID of the VPC where the ElastiCache cluster will be deployed"
  type        = string
}

variable "private_app_subnet_ids" {
  description = "List of private subnet IDs where the ElastiCache cluster will be deployed"
  type        = list(string)
}

variable "redis_node_type" {
  description = "The compute and memory capacity of the nodes in the Redis cluster"
  type        = string
  default     = "cache.t3.medium"
}

variable "redis_engine_version" {
  description = "The version number of the Redis engine to be used"
  type        = string
  default     = "6.x"
}

variable "redis_port" {
  description = "The port number on which the Redis cluster accepts connections"
  type        = number
  default     = 6379
}

variable "redis_parameter_group_name" {
  description = "The name of the parameter group to associate with the Redis cluster"
  type        = string
  default     = null
}

variable "redis_num_cache_nodes" {
  description = "The number of cache nodes in the Redis cluster"
  type        = number
  default     = 2
}

variable "redis_automatic_failover_enabled" {
  description = "Specifies whether automatic failover is enabled for the Redis cluster"
  type        = bool
  default     = true
}

variable "redis_multi_az_enabled" {
  description = "Specifies whether Multi-AZ is enabled for the Redis cluster"
  type        = bool
  default     = true
}

variable "redis_at_rest_encryption_enabled" {
  description = "Specifies whether encryption at rest is enabled for the Redis cluster"
  type        = bool
  default     = true
}

variable "redis_transit_encryption_enabled" {
  description = "Specifies whether encryption in transit is enabled for the Redis cluster"
  type        = bool
  default     = true
}

variable "redis_auth_token" {
  description = "The password used to access a password-protected Redis cluster"
  type        = string
  default     = ""
  sensitive   = true
}

variable "redis_snapshot_retention_limit" {
  description = "The number of days for which ElastiCache retains automatic snapshots"
  type        = number
  default     = 7
}

variable "redis_snapshot_window" {
  description = "The daily time range during which automated backups are created"
  type        = string
  default     = "03:00-05:00"
}

variable "redis_maintenance_window" {
  description = "The weekly time range during which maintenance on the cluster is performed"
  type        = string
  default     = "sun:23:00-mon:01:00"
}

variable "redis_auto_minor_version_upgrade" {
  description = "Specifies whether minor engine upgrades are applied automatically"
  type        = bool
  default     = true
}

variable "redis_apply_immediately" {
  description = "Specifies whether any modifications are applied immediately or during the maintenance window"
  type        = bool
  default     = false
}

variable "app_security_group_ids" {
  description = "List of security group IDs for the application that will access the Redis cluster"
  type        = list(string)
  default     = []
}

variable "tags" {
  description = "A map of tags to assign to the ElastiCache resources"
  type        = map(string)
  default     = {}
}