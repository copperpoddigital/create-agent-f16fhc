# General Project Variables
# ------------------------------------------------------------------------

project_name = "freight-price-agent"
environment  = "staging"

# ------------------------------------------------------------------------
# AWS Configuration Variables
# ------------------------------------------------------------------------

aws_region           = "us-west-2"
secondary_aws_region = "us-east-1"

# ------------------------------------------------------------------------
# Networking Variables
# ------------------------------------------------------------------------

vpc_cidr = "10.1.0.0/16"

availability_zones = [
  "us-west-2a",
  "us-west-2b",
  "us-west-2c"
]

public_subnet_cidrs = [
  "10.1.1.0/24",
  "10.1.2.0/24",
  "10.1.3.0/24"
]

private_app_subnet_cidrs = [
  "10.1.11.0/24",
  "10.1.12.0/24",
  "10.1.13.0/24"
]

private_data_subnet_cidrs = [
  "10.1.21.0/24",
  "10.1.22.0/24",
  "10.1.23.0/24"
]

# ------------------------------------------------------------------------
# Database Variables
# ------------------------------------------------------------------------

db_instance_class         = "db.m5.large"
db_allocated_storage      = 200
db_max_allocated_storage  = 500
db_name                   = "freight_price_agent"
db_username               = "stagingadmin"
db_multi_az               = true
enable_deletion_protection = true
backup_retention_period   = 14
enable_cross_region_backup = true

# ------------------------------------------------------------------------
# Caching Variables
# ------------------------------------------------------------------------

cache_node_type = "cache.m5.large"
cache_num_nodes = 2

# ------------------------------------------------------------------------
# Compute (ECS) Variables
# ------------------------------------------------------------------------

ecs_task_cpu       = 2048
ecs_task_memory    = 4096
app_min_capacity   = 2
app_max_capacity   = 6
app_cpu_threshold  = 70

# ------------------------------------------------------------------------
# Application Variables
# ------------------------------------------------------------------------

app_image = "freight-price-agent:staging"
app_port  = 8080

# ------------------------------------------------------------------------
# Tagging Variables
# ------------------------------------------------------------------------

tags = {
  Environment         = "Staging"
  Project            = "Freight Price Movement Agent"
  ManagedBy          = "Terraform"
  Owner              = "DevOps Team"
  BusinessCriticality = "Medium"
  DataClassification  = "Confidential"
}