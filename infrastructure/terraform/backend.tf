# Purpose: Configure the Terraform backend for state storage, locking, and sharing
#
# This configuration:
# - Stores the Terraform state in an S3 bucket for persistence and sharing
# - Enables state locking using a DynamoDB table to prevent concurrent modifications
# - Enforces encryption of the state file for security
# - Uses a dedicated AWS profile for authentication
#
# Prerequisites:
# - The S3 bucket and DynamoDB table must exist before using this backend
# - The AWS profile must have appropriate permissions to access the bucket and table

terraform {
  backend "s3" {
    bucket         = "freight-price-agent-terraform-state"
    key            = "terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
    dynamodb_table = "freight-price-agent-terraform-locks"
    profile        = "terraform"
  }
}