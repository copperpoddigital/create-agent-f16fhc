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

variable "vpc_id" {
  description = "ID of the VPC where ECS resources will be deployed"
  type        = string
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for the load balancer"
  type        = list(string)
  default     = []
}

variable "private_app_subnet_ids" {
  description = "List of private subnet IDs for the ECS tasks"
  type        = list(string)
  default     = []
}

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

variable "service_names" {
  description = "List of service names to create"
  type        = list(string)
  default     = ["data_ingestion", "analysis", "presentation", "integration"]
}

variable "service_cpu_thresholds" {
  description = "Map of CPU utilization thresholds for auto-scaling each service"
  type        = map(number)
  default     = {
    data_ingestion = 70
    analysis       = 70
    presentation   = 70
    integration    = 70
  }
}

variable "service_min_capacities" {
  description = "Map of minimum task counts for each service"
  type        = map(number)
  default     = {
    data_ingestion = 2
    analysis       = 3
    presentation   = 2
    integration    = 1
  }
}

variable "service_max_capacities" {
  description = "Map of maximum task counts for each service"
  type        = map(number)
  default     = {
    data_ingestion = 10
    analysis       = 20
    presentation   = 10
    integration    = 5
  }
}

variable "app_image" {
  description = "Base Docker image name for the application services"
  type        = string
}

variable "app_port" {
  description = "Port on which the application services listen"
  type        = number
  default     = 8080
}

variable "health_check_path" {
  description = "Path for health check endpoint"
  type        = string
  default     = "/health"
}

variable "deployment_strategy" {
  description = "Deployment strategy to use (rolling or blue-green)"
  type        = string
  default     = "rolling"
}

variable "enable_service_discovery" {
  description = "Whether to enable AWS Cloud Map service discovery"
  type        = bool
  default     = true
}

variable "enable_execute_command" {
  description = "Whether to enable ECS Exec for debugging"
  type        = bool
  default     = true
}

variable "logs_retention_in_days" {
  description = "Number of days to retain CloudWatch logs"
  type        = number
  default     = 30
}

variable "task_execution_role_arn" {
  description = "ARN of the IAM role for ECS task execution"
  type        = string
  default     = null
}

variable "task_role_arn" {
  description = "ARN of the IAM role for ECS tasks"
  type        = string
  default     = null
}

variable "environment_variables" {
  description = "Environment variables to pass to the containers"
  type        = list(map(string))
  default     = []
}

variable "sns_topic_arn" {
  description = "ARN of the SNS topic for CloudWatch alarms"
  type        = string
  default     = null
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default     = {}
}