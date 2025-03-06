# -----------------------------------------------------------------------------
# Main Terraform configuration for the Freight Price Movement Agent
# 
# This file orchestrates the AWS infrastructure deployment by calling
# various submodules for networking, security, database, caching, storage, and
# compute resources to create a complete, production-ready environment.
# -----------------------------------------------------------------------------

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Common tags to be applied to all resources (merged with the input tags)
  common_tags = merge(var.tags, {
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  })
}

# -----------------------------------------------------------------------------
# Network Module - Creates VPC, subnets, route tables, and other networking components
# -----------------------------------------------------------------------------
module "network" {
  source = "./modules/network"
  
  vpc_cidr                = var.vpc_cidr
  availability_zones      = var.availability_zones
  public_subnet_cidrs     = var.public_subnet_cidrs
  private_app_subnet_cidrs = var.private_app_subnet_cidrs
  private_data_subnet_cidrs = var.private_data_subnet_cidrs
  enable_vpc_flow_logs    = true
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# Security Module - Creates IAM roles, security groups, KMS keys, and WAF
# -----------------------------------------------------------------------------
module "security" {
  source = "./modules/security"
  
  project_name         = var.project_name
  environment          = var.environment
  vpc_id               = module.network.vpc_id
  public_subnet_ids    = module.network.public_subnet_ids
  private_app_subnet_ids = module.network.private_app_subnet_ids
  private_data_subnet_ids = module.network.private_data_subnet_ids
  enable_waf           = true
  waf_rate_limit       = var.app_cpu_threshold
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# RDS Module - Creates PostgreSQL database with TimescaleDB extension
# -----------------------------------------------------------------------------
module "rds" {
  source = "./modules/rds"
  
  vpc_id                  = module.network.vpc_id
  private_data_subnet_ids = module.network.private_data_subnet_ids
  db_instance_class       = var.db_instance_class
  db_allocated_storage    = var.db_allocated_storage
  db_max_allocated_storage = var.db_max_allocated_storage
  db_name                 = var.db_name
  db_username             = var.db_username
  db_password             = var.db_password
  db_multi_az             = var.db_multi_az
  db_backup_retention_period = var.backup_retention_period
  db_deletion_protection  = var.enable_deletion_protection
  db_storage_encrypted    = true
  app_security_group_ids  = [module.security.app_security_group_id]
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# ElastiCache Module - Creates Redis cache for application caching
# -----------------------------------------------------------------------------
module "elasticache" {
  source = "./modules/elasticache"
  
  vpc_id                  = module.network.vpc_id
  private_app_subnet_ids  = module.network.private_app_subnet_ids
  redis_node_type         = var.cache_node_type
  redis_num_cache_nodes   = var.cache_num_nodes
  redis_engine_version    = "6.x"
  redis_automatic_failover_enabled = true
  redis_multi_az_enabled  = true
  redis_at_rest_encryption_enabled = true
  redis_transit_encryption_enabled = true
  app_security_group_ids  = [module.security.app_security_group_id]
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# S3 Module - Creates S3 buckets for file storage, analysis results, and archival
# -----------------------------------------------------------------------------
module "s3" {
  source = "./modules/s3"
  
  project_name        = var.project_name
  environment         = var.environment
  aws_region          = var.aws_region
  enable_versioning   = true
  enable_encryption   = true
  lifecycle_rules_enabled = true
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# ECS Module - Creates ECS cluster, services, and related resources
# -----------------------------------------------------------------------------
module "ecs" {
  source = "./modules/ecs"
  
  project_name           = var.project_name
  environment            = var.environment
  vpc_id                 = module.network.vpc_id
  public_subnet_ids      = module.network.public_subnet_ids
  private_app_subnet_ids = module.network.private_app_subnet_ids
  ecs_task_cpu           = var.ecs_task_cpu
  ecs_task_memory        = var.ecs_task_memory
  app_min_capacity       = var.app_min_capacity
  app_max_capacity       = var.app_max_capacity
  app_cpu_threshold      = var.app_cpu_threshold
  app_image              = var.app_image
  app_port               = var.app_port
  health_check_path      = "/health"
  deployment_strategy    = "rolling"
  task_execution_role_arn = module.security.ecs_task_execution_role_arn
  task_role_arn          = module.security.ecs_task_role_arn
  alb_security_group_id  = module.security.alb_security_group_id
  app_security_group_id  = module.security.app_security_group_id
  waf_web_acl_id         = module.security.waf_web_acl_id
  
  environment_variables = [
    {
      name  = "DB_HOST"
      value = module.rds.db_instance_endpoint
    },
    {
      name  = "DB_NAME"
      value = var.db_name
    },
    {
      name  = "REDIS_HOST"
      value = module.elasticache.elasticache_primary_endpoint
    },
    {
      name  = "S3_BUCKET_CSV"
      value = module.s3.csv_storage_bucket_name
    },
    {
      name  = "S3_BUCKET_RESULTS"
      value = module.s3.analysis_results_bucket_name
    }
  ]
  
  tags = local.common_tags
}

# -----------------------------------------------------------------------------
# CloudWatch Resources - Creates log groups and dashboards for monitoring
# -----------------------------------------------------------------------------

# Create CloudWatch log group for application logging
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/freight-price-agent/${var.environment}"
  retention_in_days = 30
  tags              = local.common_tags
}

# Create CloudWatch dashboard for monitoring key metrics
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "freight-price-agent-${var.environment}"
  
  dashboard_body = <<EOF
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/ECS", "CPUUtilization", "ServiceName", "${module.ecs.ecs_service_names[0]}", "ClusterName", "${module.ecs.ecs_cluster_name}"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "${var.aws_region}",
        "title": "ECS CPU Utilization"
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/ECS", "MemoryUtilization", "ServiceName", "${module.ecs.ecs_service_names[0]}", "ClusterName", "${module.ecs.ecs_cluster_name}"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "${var.aws_region}",
        "title": "ECS Memory Utilization"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${module.rds.db_instance_id}"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "${var.aws_region}",
        "title": "RDS CPU Utilization"
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 6,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${module.rds.db_instance_id}"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "${var.aws_region}",
        "title": "RDS Database Connections"
      }
    },
    {
      "type": "metric",
      "x": 0,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/ElastiCache", "CPUUtilization", "CacheClusterId", "${split(".", module.elasticache.elasticache_primary_endpoint)[0]}"]
        ],
        "period": 300,
        "stat": "Average",
        "region": "${var.aws_region}",
        "title": "ElastiCache CPU Utilization"
      }
    },
    {
      "type": "metric",
      "x": 12,
      "y": 12,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "${split("/", module.ecs.load_balancer_dns_name)[1]}"]
        ],
        "period": 300,
        "stat": "Sum",
        "region": "${var.aws_region}",
        "title": "ALB Request Count"
      }
    }
  ]
}
EOF
}