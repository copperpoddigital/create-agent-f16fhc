# Configures the AWS provider for Terraform with appropriate version constraints, 
# authentication methods, and regional settings for the Freight Price Movement Agent
# infrastructure deployment.

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

# Configure the primary AWS provider with the main region
provider "aws" {
  region              = var.aws_region
  allowed_account_ids = var.allowed_account_ids
  
  default_tags {
    tags = {
      Project     = "Freight Price Movement Agent"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Configure a secondary AWS provider for disaster recovery
provider "aws" {
  alias               = "secondary"
  region              = var.secondary_aws_region
  allowed_account_ids = var.allowed_account_ids
  
  default_tags {
    tags = {
      Project     = "Freight Price Movement Agent"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Configure the random provider for generating unique identifiers
provider "random" {
}