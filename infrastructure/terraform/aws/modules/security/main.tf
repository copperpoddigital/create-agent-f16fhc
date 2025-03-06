# ---------------------------------------------------------------------------------------------------------------------
# AWS SECURITY MODULE
# Provisions security resources for the Freight Price Movement Agent including:
# - KMS keys for data encryption
# - IAM roles and policies for service access
# - Security groups for network traffic control
# - WAF configurations for API protection
# ---------------------------------------------------------------------------------------------------------------------

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# ---------------------------------------------------------------------------------------------------------------------
# KMS KEY FOR DATA ENCRYPTION
# Used to encrypt sensitive freight pricing data at rest
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_kms_key" "main" {
  description             = "KMS key for encrypting freight pricing data"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid    = "Enable IAM User Permissions",
        Effect = "Allow",
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        },
        Action   = "kms:*",
        Resource = "*"
      }
    ]
  })
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-kms-key"
  })
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.name_prefix}"
  target_key_id = aws_kms_key.main.key_id
}

# ---------------------------------------------------------------------------------------------------------------------
# IAM ROLES FOR ECS TASKS
# Provides permissions for ECS task execution and runtime operations
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_iam_role" "ecs_task_execution" {
  name = "${local.name_prefix}-ecs-task-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
  name = "${local.name_prefix}-ecs-task-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
  
  tags = var.tags
}

# ---------------------------------------------------------------------------------------------------------------------
# IAM POLICIES
# Defines permissions for S3 access and KMS encryption
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_iam_policy" "s3_access" {
  name        = "${local.name_prefix}-s3-access-policy"
  description = "Policy for accessing S3 buckets for freight data and analysis results"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ],
        Resource = [
          "arn:aws:s3:::${local.name_prefix}-*",
          "arn:aws:s3:::${local.name_prefix}-*/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_policy" "kms_access" {
  name        = "${local.name_prefix}-kms-access-policy"
  description = "Policy for accessing KMS keys for data encryption"
  
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "kms:Decrypt",
          "kms:GenerateDataKey",
          "kms:DescribeKey"
        ],
        Resource = aws_kms_key.main.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "kms_access_task" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.kms_access.arn
}

resource "aws_iam_role_policy_attachment" "kms_access_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = aws_iam_policy.kms_access.arn
}

# ---------------------------------------------------------------------------------------------------------------------
# SECURITY GROUPS
# Define network access controls for different application tiers
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for the application load balancer"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from internet"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

resource "aws_security_group" "app" {
  name        = "${local.name_prefix}-app-sg"
  description = "Security group for the application tier"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "All traffic from ALB"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-app-sg"
  })
}

resource "aws_security_group" "data" {
  name        = "${local.name_prefix}-data-sg"
  description = "Security group for the data tier"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
    description     = "All traffic from application tier"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-data-sg"
  })
}

resource "aws_security_group" "bastion" {
  count       = var.enable_bastion ? 1 : 0
  name        = "${local.name_prefix}-bastion-sg"
  description = "Security group for the bastion host"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_cidr_blocks
    description = "SSH from allowed CIDR blocks"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-bastion-sg"
  })
}

# ---------------------------------------------------------------------------------------------------------------------
# WAF WEB ACL
# Protects API endpoints from common attacks and rate limits requests
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_wafv2_web_acl" "main" {
  count       = var.enable_waf ? 1 : 0
  name        = "${local.name_prefix}-waf"
  description = "WAF Web ACL for the Freight Price Movement Agent"
  scope       = "REGIONAL"
  
  default_action {
    allow {}
  }
  
  # Rate limiting rule
  rule {
    name     = "RateLimit"
    priority = 1
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = var.waf_rate_limit
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimit"
      sampled_requests_enabled   = true
    }
  }
  
  # AWS Common rule set
  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 2
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  # SQL Injection protection
  rule {
    name     = "AWSManagedRulesSQLiRuleSet"
    priority = 3
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${local.name_prefix}-waf"
    sampled_requests_enabled   = true
  }
  
  tags = var.tags
}

# ---------------------------------------------------------------------------------------------------------------------
# DATA SOURCES
# Reference existing AWS account information
# ---------------------------------------------------------------------------------------------------------------------

data "aws_caller_identity" "current" {}

# ---------------------------------------------------------------------------------------------------------------------
# OUTPUTS
# Export resource identifiers for use in other modules
# ---------------------------------------------------------------------------------------------------------------------

output "kms_key_id" {
  description = "ID of the KMS key used for data encryption"
  value       = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for data encryption"
  value       = aws_kms_key.main.arn
}

output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL used for API protection"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].id : null
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role used for ECS task execution"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role used by ECS tasks at runtime"
  value       = aws_iam_role.ecs_task.arn
}

output "bastion_security_group_id" {
  description = "ID of the security group for the bastion host"
  value       = var.enable_bastion ? aws_security_group.bastion[0].id : null
}

output "alb_security_group_id" {
  description = "ID of the security group for the application load balancer"
  value       = aws_security_group.alb.id
}

output "app_security_group_id" {
  description = "ID of the security group for the application tier"
  value       = aws_security_group.app.id
}

output "data_security_group_id" {
  description = "ID of the security group for the data tier"
  value       = aws_security_group.data.id
}