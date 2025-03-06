# -----------------------------------------------------------------------------
# Network Outputs
# -----------------------------------------------------------------------------
output "vpc_id" {
  description = "ID of the VPC created for the infrastructure"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "List of public subnet IDs created for the infrastructure"
  value       = module.network.public_subnet_ids
}

output "private_app_subnet_ids" {
  description = "List of private application subnet IDs created for the infrastructure"
  value       = module.network.private_app_subnet_ids
}

output "private_data_subnet_ids" {
  description = "List of private data subnet IDs created for the infrastructure"
  value       = module.network.private_data_subnet_ids
}

# -----------------------------------------------------------------------------
# ECS Outputs
# -----------------------------------------------------------------------------
output "ecs_cluster_id" {
  description = "ID of the ECS cluster created for the application services"
  value       = module.ecs.ecs_cluster_id
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster created for the application services"
  value       = module.ecs.ecs_cluster_name
}

output "ecs_service_names" {
  description = "Map of service names for each application component"
  value       = module.ecs.ecs_service_names
}

output "load_balancer_dns_name" {
  description = "DNS name of the application load balancer for accessing the application"
  value       = module.ecs.load_balancer_dns_name
}

# -----------------------------------------------------------------------------
# Database Outputs
# -----------------------------------------------------------------------------
output "db_endpoint" {
  description = "Endpoint of the PostgreSQL database for application connection"
  value       = module.rds.db_instance_endpoint
}

output "db_instance_id" {
  description = "ID of the RDS instance for reference in other resources"
  value       = module.rds.db_instance_id
}

# -----------------------------------------------------------------------------
# ElastiCache Outputs
# -----------------------------------------------------------------------------
output "redis_primary_endpoint" {
  description = "Primary endpoint of the Redis cache for application connection"
  value       = module.elasticache.elasticache_primary_endpoint
}

output "redis_reader_endpoint" {
  description = "Reader endpoint of the Redis cache for read-only operations"
  value       = module.elasticache.elasticache_reader_endpoint
}

# -----------------------------------------------------------------------------
# S3 Bucket Outputs
# -----------------------------------------------------------------------------
output "csv_storage_bucket_name" {
  description = "Name of the S3 bucket for storing CSV files"
  value       = module.s3.csv_storage_bucket_name
}

output "analysis_results_bucket_name" {
  description = "Name of the S3 bucket for storing analysis results"
  value       = module.s3.analysis_results_bucket_name
}

output "archive_storage_bucket_name" {
  description = "Name of the S3 bucket for long-term data archival"
  value       = module.s3.archive_storage_bucket_name
}

# -----------------------------------------------------------------------------
# Security Outputs
# -----------------------------------------------------------------------------
output "kms_key_id" {
  description = "ID of the KMS key used for data encryption"
  value       = module.security.kms_key_id
}

output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL used for API protection"
  value       = module.security.waf_web_acl_id
}

# -----------------------------------------------------------------------------
# Monitoring Outputs
# -----------------------------------------------------------------------------
output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group for application logging"
  value       = aws_cloudwatch_log_group.app.name
}

output "cloudwatch_dashboard_name" {
  description = "Name of the CloudWatch dashboard for monitoring the infrastructure"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

# -----------------------------------------------------------------------------
# Environment Information
# -----------------------------------------------------------------------------
output "environment" {
  description = "The deployment environment (dev, staging, prod)"
  value       = var.environment
}

output "region" {
  description = "The AWS region where the infrastructure is deployed"
  value       = var.aws_region
}