# AWS Network Module for Freight Price Movement Agent
# This module sets up a VPC with public and private subnets across multiple
# availability zones, NAT gateways, and VPC endpoints for secure communication.

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Get current AWS region
data "aws_region" "current" {}

# Local variables for resource naming and configuration
locals {
  module_name = "freight-price-agent"
}

# Main VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = var.enable_dns_hostnames
  enable_dns_support   = var.enable_dns_support
  
  tags = merge(var.tags, {
    Name = "freight-price-agent-vpc"
  })
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(var.tags, {
    Name = "public-subnet-${count.index}"
  })
}

# Private Application Subnets
resource "aws_subnet" "private_app" {
  count                   = length(var.private_app_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_app_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false
  
  tags = merge(var.tags, {
    Name = "private-app-subnet-${count.index}"
  })
}

# Private Data Subnets
resource "aws_subnet" "private_data" {
  count                   = length(var.private_data_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.private_data_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = false
  
  tags = merge(var.tags, {
    Name = "private-data-subnet-${count.index}"
  })
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(var.tags, {
    Name = "freight-price-agent-igw"
  })
}

# Elastic IPs for NAT Gateways
resource "aws_eip" "nat" {
  count = length(var.public_subnet_cidrs)
  vpc   = true
  
  tags = merge(var.tags, {
    Name = "nat-gateway-eip-${count.index}"
  })
}

# NAT Gateways
resource "aws_nat_gateway" "main" {
  count         = length(var.public_subnet_cidrs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(var.tags, {
    Name = "nat-gateway-${count.index}"
  })
  
  depends_on = [aws_internet_gateway.main]
}

# Public Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(var.tags, {
    Name = "public-route-table"
  })
}

# Private App Route Tables
resource "aws_route_table" "private_app" {
  count  = length(var.private_app_subnet_cidrs)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(var.tags, {
    Name = "private-app-route-table-${count.index}"
  })
}

# Private Data Route Tables
resource "aws_route_table" "private_data" {
  count  = length(var.private_data_subnet_cidrs)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(var.tags, {
    Name = "private-data-route-table-${count.index}"
  })
}

# Public Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private App Route Table Associations
resource "aws_route_table_association" "private_app" {
  count          = length(var.private_app_subnet_cidrs)
  subnet_id      = aws_subnet.private_app[count.index].id
  route_table_id = aws_route_table.private_app[count.index].id
}

# Private Data Route Table Associations
resource "aws_route_table_association" "private_data" {
  count          = length(var.private_data_subnet_cidrs)
  subnet_id      = aws_subnet.private_data[count.index].id
  route_table_id = aws_route_table.private_data[count.index].id
}

# Security Group for VPC Endpoints
resource "aws_security_group" "vpc_endpoints" {
  name        = "vpc-endpoints-sg"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
    description = "HTTPS from VPC"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "vpc-endpoints-sg"
  })
}

# S3 VPC Endpoint
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(
    [aws_route_table.public.id],
    aws_route_table.private_app[*].id,
    aws_route_table.private_data[*].id
  )
  
  tags = merge(var.tags, {
    Name = "s3-vpc-endpoint"
  })
}

# DynamoDB VPC Endpoint
resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${data.aws_region.current.name}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = concat(
    [aws_route_table.public.id],
    aws_route_table.private_app[*].id,
    aws_route_table.private_data[*].id
  )
  
  tags = merge(var.tags, {
    Name = "dynamodb-vpc-endpoint"
  })
}

# ECR API VPC Endpoint
resource "aws_vpc_endpoint" "ecr_api" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.api"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
  
  tags = merge(var.tags, {
    Name = "ecr-api-vpc-endpoint"
  })
}

# ECR Docker VPC Endpoint
resource "aws_vpc_endpoint" "ecr_dkr" {
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${data.aws_region.current.name}.ecr.dkr"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = aws_subnet.private_app[*].id
  security_group_ids  = [aws_security_group.vpc_endpoints.id]
  private_dns_enabled = true
  
  tags = merge(var.tags, {
    Name = "ecr-dkr-vpc-endpoint"
  })
}

# VPC Flow Logs
resource "aws_flow_log" "vpc_flow_logs" {
  count                = var.enable_vpc_flow_logs ? 1 : 0
  log_destination_type = "cloud-watch-logs"
  log_destination      = aws_cloudwatch_log_group.vpc_flow_logs[0].arn
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.main.id
  iam_role_arn         = aws_iam_role.vpc_flow_logs[0].arn
  
  tags = merge(var.tags, {
    Name = "vpc-flow-logs"
  })
}

# CloudWatch Log Group for VPC Flow Logs
resource "aws_cloudwatch_log_group" "vpc_flow_logs" {
  count             = var.enable_vpc_flow_logs ? 1 : 0
  name              = "/aws/vpc-flow-logs/freight-price-agent"
  retention_in_days = 30
  
  tags = var.tags
}

# IAM Role for VPC Flow Logs
resource "aws_iam_role" "vpc_flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0
  name  = "vpc-flow-logs-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "vpc-flow-logs.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

# IAM Policy for VPC Flow Logs Role
resource "aws_iam_role_policy" "vpc_flow_logs" {
  count = var.enable_vpc_flow_logs ? 1 : 0
  name  = "vpc-flow-logs-policy"
  role  = aws_iam_role.vpc_flow_logs[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Outputs
output "vpc_id" {
  description = "ID of the created VPC for reference by other modules"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC for reference by security groups and other resources"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs for resources that need public internet access"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "List of private application tier subnet IDs for application services"
  value       = aws_subnet.private_app[*].id
}

output "private_data_subnet_ids" {
  description = "List of private data tier subnet IDs for database and cache services"
  value       = aws_subnet.private_data[*].id
}

output "nat_gateway_ids" {
  description = "List of NAT gateway IDs for reference by other modules"
  value       = aws_nat_gateway.main[*].id
}

output "internet_gateway_id" {
  description = "ID of the internet gateway for reference by other modules"
  value       = aws_internet_gateway.main.id
}

output "vpc_endpoint_ids" {
  description = "IDs of VPC endpoints for AWS services"
  value = {
    s3        = aws_vpc_endpoint.s3.id
    dynamodb  = aws_vpc_endpoint.dynamodb.id
    ecr_api   = aws_vpc_endpoint.ecr_api.id
    ecr_dkr   = aws_vpc_endpoint.ecr_dkr.id
  }
}

output "route_table_ids" {
  description = "IDs of route tables for reference by other modules"
  value = {
    public       = aws_route_table.public.id
    private_app  = aws_route_table.private_app[*].id
    private_data = aws_route_table.private_data[*].id
  }
}