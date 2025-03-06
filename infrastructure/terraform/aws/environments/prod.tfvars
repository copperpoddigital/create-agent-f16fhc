# General Project Variables
# ------------------------------------------------------------------------

project_name = "freight-price-agent"
environment  = "prod"

# ------------------------------------------------------------------------
# AWS Configuration Variables
# ------------------------------------------------------------------------

aws_region           = "us-west-2"
secondary_aws_region = "us-east-1"
allowed_account_ids  = ["123456789012"] # Replace with actual production AWS account ID

# ------------------------------------------------------------------------
# Networking Variables
# ------------------------------------------------------------------------

vpc_cidr                  = "10.2.0.0/16"  # Production-specific CIDR range
availability_zones        = ["us-west-2a", "us-west-2b", "us-west-2c"]
public_subnet_cidrs       = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
private_app_subnet_cidrs  = ["10.2.11.0/24", "10.2.12.0/24", "10.2.13.0/24"]
private_data_subnet_cidrs = ["10.2.21.0/24", "10.2.22.0/24", "10.2.23.0/24"]

# ------------------------------------------------------------------------
# Database Variables
# ------------------------------------------------------------------------

db_instance_class        = "db.m5.xlarge"  # More powerful instance for production
db_allocated_storage     = 500             # Larger initial storage for production
db_max_allocated_storage = 1000            # Higher storage limit for growth
db_name                  = "freight_price_agent"
db_username              = "prodadmin"     # Production-specific username
db_multi_az              = true            # Enable Multi-AZ for high availability

# ------------------------------------------------------------------------
# Caching Variables
# ------------------------------------------------------------------------

cache_node_type  = "cache.m5.large"  # Production-grade cache instance
cache_num_nodes  = 3                 # Three nodes for redundancy

# ------------------------------------------------------------------------
# Compute (ECS) Variables
# ------------------------------------------------------------------------

ecs_task_cpu      = 4096             # 4 vCPU for production workloads
ecs_task_memory   = 8192             # 8 GB memory for production workloads
app_min_capacity  = 3                # Higher minimum capacity for production
app_max_capacity  = 10               # Scale up to 10 tasks
app_cpu_threshold = 70               # Scale at 70% CPU utilization

# ------------------------------------------------------------------------
# Application Variables
# ------------------------------------------------------------------------

app_image = "freight-price-agent:prod" # Production-specific image tag
app_port  = 8080

# ------------------------------------------------------------------------
# Security and Compliance Variables
# ------------------------------------------------------------------------

enable_deletion_protection = true     # Prevent accidental deletion in production
backup_retention_period    = 35       # Retain backups for 35 days
enable_cross_region_backup = true     # Enable cross-region backup for DR

# ------------------------------------------------------------------------
# Tagging Variables
# ------------------------------------------------------------------------

tags = {
  Environment           = "Production"
  Project              = "Freight Price Movement Agent"
  ManagedBy            = "Terraform"
  Owner                = "DevOps Team"
  BusinessCriticality  = "High"
  DataClassification   = "Confidential"
  ComplianceRequirement = "SOC2"
}