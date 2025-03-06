# AWS ElastiCache Module for Freight Price Movement Agent
# This module creates a Redis cluster for caching application data and analysis results

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

locals {
  # Local variables for resource naming and configuration
  name_prefix = "freight-price-agent"
}

# Create a subnet group for the ElastiCache Redis cluster
resource "aws_elasticache_subnet_group" "redis" {
  name        = "${local.name_prefix}-redis-subnet-group"
  description = "Subnet group for Freight Price Movement Agent Redis cluster"
  subnet_ids  = var.private_app_subnet_ids
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-redis-subnet-group"
  })
}

# Create a security group for the ElastiCache Redis cluster
resource "aws_security_group" "redis" {
  name        = "${local.name_prefix}-redis-sg"
  description = "Security group for Freight Price Movement Agent Redis cluster"
  vpc_id      = var.vpc_id
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-redis-sg"
  })
}

# Create ingress rules for the Redis security group
# Allow access from application security groups on Redis port
resource "aws_security_group_rule" "redis_ingress" {
  for_each = toset(var.app_security_group_ids)
  
  type                     = "ingress"
  from_port                = var.redis_port
  to_port                  = var.redis_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.redis.id
  source_security_group_id = each.value
  description              = "Allow Redis access from application security group"
}

# Create egress rules for the Redis security group
# Allow all outbound traffic
resource "aws_security_group_rule" "redis_egress" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = aws_security_group.redis.id
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow all outbound traffic"
}

# Create a parameter group for the ElastiCache Redis cluster
resource "aws_elasticache_parameter_group" "redis" {
  name        = "${local.name_prefix}-redis-params"
  family      = "redis6.x"
  description = "Parameter group for Freight Price Movement Agent Redis cluster"
  
  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"  # Evict keys with TTL when memory is full
  }
  
  parameter {
    name  = "notify-keyspace-events"
    value = "Ex"  # Notify when keys expire
  }
  
  tags = var.tags
}

# Create the ElastiCache Redis cluster
resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "${local.name_prefix}-redis"
  description                = "Redis cluster for Freight Price Movement Agent"
  node_type                  = var.redis_node_type
  port                       = var.redis_port
  parameter_group_name       = aws_elasticache_parameter_group.redis.name
  subnet_group_name          = aws_elasticache_subnet_group.redis.name
  security_group_ids         = [aws_security_group.redis.id]
  
  automatic_failover_enabled = var.redis_automatic_failover_enabled
  multi_az_enabled           = var.redis_multi_az_enabled
  num_cache_clusters         = var.redis_num_cache_nodes
  
  engine                     = "redis"
  engine_version             = var.redis_engine_version
  
  at_rest_encryption_enabled = var.redis_at_rest_encryption_enabled
  transit_encryption_enabled = var.redis_transit_encryption_enabled
  auth_token                 = var.redis_transit_encryption_enabled ? var.redis_auth_token : null
  
  snapshot_retention_limit   = var.redis_snapshot_retention_limit
  snapshot_window            = var.redis_snapshot_window
  maintenance_window         = var.redis_maintenance_window
  
  auto_minor_version_upgrade = var.redis_auto_minor_version_upgrade
  apply_immediately          = var.redis_apply_immediately
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-redis"
  })
}

# Output Variables
output "elasticache_replication_group_id" {
  description = "The ID of the ElastiCache replication group"
  value       = aws_elasticache_replication_group.redis.id
}

output "elasticache_primary_endpoint" {
  description = "The primary endpoint address for the ElastiCache Redis cluster"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "elasticache_reader_endpoint" {
  description = "The reader endpoint address for the ElastiCache Redis cluster"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "elasticache_port" {
  description = "The port number on which the ElastiCache Redis cluster accepts connections"
  value       = aws_elasticache_replication_group.redis.port
}

output "elasticache_security_group_id" {
  description = "The ID of the security group created for the ElastiCache Redis cluster"
  value       = aws_security_group.redis.id
}

output "elasticache_subnet_group_name" {
  description = "The name of the subnet group created for the ElastiCache Redis cluster"
  value       = aws_elasticache_subnet_group.redis.name
}