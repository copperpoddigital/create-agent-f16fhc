# -----------------------------------------------------------------------------
# RDS PostgreSQL with TimescaleDB module for Freight Price Movement Agent
# -----------------------------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# -----------------------------------------------------------------------------
# Local variables
# -----------------------------------------------------------------------------

locals {
  name_prefix = "${var.project_name}-${var.environment}-db"
}

# -----------------------------------------------------------------------------
# DB Subnet Group
# -----------------------------------------------------------------------------

resource "aws_db_subnet_group" "this" {
  name        = "${local.name_prefix}-subnet-group"
  subnet_ids  = var.private_data_subnet_ids
  description = "Subnet group for Freight Price Movement Agent database"
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-subnet-group"
  })
}

# -----------------------------------------------------------------------------
# Security Group for PostgreSQL access
# -----------------------------------------------------------------------------

resource "aws_security_group" "this" {
  name        = "${local.name_prefix}-sg"
  vpc_id      = var.vpc_id
  description = "Security group for Freight Price Movement Agent database"
  
  # Allow PostgreSQL traffic from application tier
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = var.app_security_group_ids
    description     = "PostgreSQL access from application tier"
  }
  
  # Allow all outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-sg"
  })
}

# -----------------------------------------------------------------------------
# Parameter group for PostgreSQL with TimescaleDB
# -----------------------------------------------------------------------------

resource "aws_db_parameter_group" "this" {
  name        = "${local.name_prefix}-pg"
  family      = "postgres13"
  description = "Parameter group for Freight Price Movement Agent with TimescaleDB"
  
  # TimescaleDB extension configuration
  parameter {
    name  = "shared_preload_libraries"
    value = "timescaledb,pg_stat_statements"
    apply_method = "pending-reboot"
  }
  
  # Optimize for time-series data
  parameter {
    name  = "max_connections"
    value = "200"
    apply_method = "pending-reboot"
  }
  
  parameter {
    name  = "work_mem"
    value = "16384" # 16MB
    apply_method = "pending-reboot"
  }
  
  parameter {
    name  = "maintenance_work_mem"
    value = "2GB"
    apply_method = "pending-reboot"
  }
  
  parameter {
    name  = "random_page_cost"
    value = "1.1"
    apply_method = "pending-reboot"
  }
  
  parameter {
    name  = "effective_cache_size"
    value = "8GB"
    apply_method = "pending-reboot"
  }
  
  # Logging for performance monitoring
  parameter {
    name  = "log_min_duration_statement"
    value = "1000" # ms
    apply_method = "immediate"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-pg"
  })
}

# -----------------------------------------------------------------------------
# KMS Key for RDS encryption (if enabled)
# -----------------------------------------------------------------------------

resource "aws_kms_key" "this" {
  count                   = var.db_storage_encrypted ? 1 : 0
  description             = "KMS key for RDS encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-kms-key"
  })
}

resource "aws_kms_alias" "this" {
  count         = var.db_storage_encrypted ? 1 : 0
  name          = "alias/${local.name_prefix}-key"
  target_key_id = aws_kms_key.this[0].key_id
}

# -----------------------------------------------------------------------------
# RDS PostgreSQL Instance
# -----------------------------------------------------------------------------

resource "aws_db_instance" "this" {
  identifier              = local.name_prefix
  engine                  = "postgres"
  engine_version          = var.db_engine_version
  instance_class          = var.db_instance_class
  allocated_storage       = var.db_allocated_storage
  max_allocated_storage   = var.db_max_allocated_storage
  storage_type            = var.db_storage_type
  storage_encrypted       = var.db_storage_encrypted
  kms_key_id              = var.db_storage_encrypted ? aws_kms_key.this[0].arn : null
  
  # Database configuration
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  port                    = 5432
  
  # High availability and placement
  multi_az                = var.db_multi_az
  db_subnet_group_name    = aws_db_subnet_group.this.name
  vpc_security_group_ids  = [aws_security_group.this.id]
  parameter_group_name    = aws_db_parameter_group.this.name
  
  # Backup and maintenance
  backup_retention_period = var.db_backup_retention_period
  backup_window           = var.db_backup_window
  maintenance_window      = var.db_maintenance_window
  
  # Update behavior
  apply_immediately       = var.db_apply_immediately
  
  # Protection settings
  deletion_protection     = var.db_deletion_protection
  skip_final_snapshot     = var.db_skip_final_snapshot
  final_snapshot_identifier = var.db_skip_final_snapshot ? null : coalesce(var.db_final_snapshot_identifier, "${local.name_prefix}-final-snapshot")
  
  # Monitoring and insights
  monitoring_interval     = var.db_monitoring_interval
  performance_insights_enabled = var.db_performance_insights_enabled
  performance_insights_retention_period = var.db_performance_insights_enabled ? var.db_performance_insights_retention_period : null
  
  # Version management
  auto_minor_version_upgrade = var.db_auto_minor_version_upgrade
  allow_major_version_upgrade = var.db_allow_major_version_upgrade
  
  # Enhanced logging
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  tags = merge(var.tags, {
    Name = local.name_prefix
  })
}

# -----------------------------------------------------------------------------
# Post-deployment setup for TimescaleDB extension
# -----------------------------------------------------------------------------

resource "null_resource" "install_timescaledb" {
  triggers = {
    db_instance_id = aws_db_instance.this.id
  }
  
  provisioner "local-exec" {
    command = "scripts/install-timescaledb.sh ${aws_db_instance.this.address} ${aws_db_instance.this.port} ${var.db_name} ${var.db_username} ${var.db_password}"
  }
}

# -----------------------------------------------------------------------------
# Outputs
# -----------------------------------------------------------------------------

output "db_instance_endpoint" {
  description = "Endpoint of the RDS instance for application connection"
  value       = aws_db_instance.this.endpoint
}

output "db_instance_address" {
  description = "Address of the RDS instance without port information"
  value       = aws_db_instance.this.address
}

output "db_instance_id" {
  description = "Identifier of the RDS instance for reference in other resources"
  value       = aws_db_instance.this.id
}

output "db_instance_port" {
  description = "Port on which the database instance accepts connections"
  value       = aws_db_instance.this.port
}

output "db_instance_name" {
  description = "Name of the created database"
  value       = aws_db_instance.this.db_name
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group for reference in other resources"
  value       = aws_db_subnet_group.this.name
}

output "db_security_group_id" {
  description = "ID of the security group created for database access"
  value       = aws_security_group.this.id
}

output "db_parameter_group_name" {
  description = "Name of the parameter group for PostgreSQL with TimescaleDB configuration"
  value       = aws_db_parameter_group.this.name
}

output "db_kms_key_id" {
  description = "ID of the KMS key used for database encryption"
  value       = var.db_storage_encrypted ? aws_kms_key.this[0].key_id : null
}

output "db_arn" {
  description = "ARN of the RDS instance for IAM policy references"
  value       = aws_db_instance.this.arn
}