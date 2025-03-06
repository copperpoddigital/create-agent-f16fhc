# General Project Variables
# ------------------------------------------------------------------------
project_name = "freight-price-agent"
environment  = "dev"

# ------------------------------------------------------------------------
# AWS Configuration Variables
# ------------------------------------------------------------------------
aws_region           = "us-west-2"
secondary_aws_region = "us-east-1"

# ------------------------------------------------------------------------
# Networking Variables
# ------------------------------------------------------------------------
vpc_cidr                 = "10.0.0.0/16"
availability_zones       = ["us-west-2a", "us-west-2b"]  # Reduced to 2 AZs for dev environment
public_subnet_cidrs      = ["10.0.1.0/24", "10.0.2.0/24"]
private_app_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]
private_data_subnet_cidrs = ["10.0.21.0/24", "10.0.22.0/24"]

# ------------------------------------------------------------------------
# Database Variables
# ------------------------------------------------------------------------
db_instance_class         = "db.t3.medium"  # Smaller instance for dev
db_allocated_storage      = 50              # Reduced storage for dev
db_max_allocated_storage  = 100             # Lower storage ceiling for dev
db_name                   = "freight_price_agent"
db_username               = "devadmin"
db_multi_az               = false           # Disabled Multi-AZ for dev environment

# ------------------------------------------------------------------------
# Caching Variables
# ------------------------------------------------------------------------
cache_node_type  = "cache.t3.small"  # Smaller cache instance for dev
cache_num_nodes  = 1                 # Single node for dev environment

# ------------------------------------------------------------------------
# Compute (ECS) Variables
# ------------------------------------------------------------------------
ecs_task_cpu       = 1024  # 1 vCPU
ecs_task_memory    = 2048  # 2GB RAM
app_min_capacity   = 1     # Minimum of 1 task for dev
app_max_capacity   = 3     # Maximum of 3 tasks for dev
app_cpu_threshold  = 70    # Scale on 70% CPU utilization

# ------------------------------------------------------------------------
# Application Variables
# ------------------------------------------------------------------------
app_image = "freight-price-agent:dev"
app_port  = 8080

# ------------------------------------------------------------------------
# Security & Backup Variables
# ------------------------------------------------------------------------
enable_deletion_protection = false  # Allow deletion for easy cleanup in dev
backup_retention_period    = 7      # Retain backups for 1 week in dev
enable_cross_region_backup = false  # Disable cross-region backups for dev

# ------------------------------------------------------------------------
# Tagging Variables
# ------------------------------------------------------------------------
tags = {
  Environment = "Development"
  Project     = "Freight Price Movement Agent"
  ManagedBy   = "Terraform"
  Owner       = "DevOps Team"
}