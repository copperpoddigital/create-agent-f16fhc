# -------------------------------------------------------------
# AWS Provider Configuration
# -------------------------------------------------------------
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# -------------------------------------------------------------
# Local Variables
# -------------------------------------------------------------
locals {
  # Bucket naming convention: project-environment-purpose
  csv_storage_bucket_name       = "${var.project_name}-${var.environment}-csv-storage"
  analysis_results_bucket_name  = "${var.project_name}-${var.environment}-analysis-results"
  archive_storage_bucket_name   = "${var.project_name}-${var.environment}-archive-storage"
  
  # Common tags for all resources
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# -------------------------------------------------------------
# CSV Storage Bucket
# -------------------------------------------------------------
resource "aws_s3_bucket" "csv_storage" {
  bucket = local.csv_storage_bucket_name
  tags   = merge(var.tags, local.common_tags, { Purpose = "CSV File Storage" })
}

resource "aws_s3_bucket_versioning" "csv_storage" {
  bucket = aws_s3_bucket.csv_storage.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "csv_storage" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.csv_storage.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "csv_storage" {
  bucket = aws_s3_bucket.csv_storage.id
  
  rule {
    id     = "transition-to-standard-ia"
    status = "Enabled"
    
    transition {
      days          = var.csv_storage_standard_ia_transition_days
      storage_class = "STANDARD_IA"
    }
  }
  
  rule {
    id     = "transition-to-glacier"
    status = "Enabled"
    
    transition {
      days          = var.csv_storage_glacier_transition_days
      storage_class = "GLACIER"
    }
  }
  
  rule {
    id     = "expiration"
    status = "Enabled"
    
    expiration {
      days = var.csv_storage_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "csv_storage" {
  bucket                  = aws_s3_bucket.csv_storage.id
  block_public_acls       = var.block_public_access
  block_public_policy     = var.block_public_access
  ignore_public_acls      = var.block_public_access
  restrict_public_buckets = var.block_public_access
}

# -------------------------------------------------------------
# Analysis Results Bucket
# -------------------------------------------------------------
resource "aws_s3_bucket" "analysis_results" {
  bucket = local.analysis_results_bucket_name
  tags   = merge(var.tags, local.common_tags, { Purpose = "Analysis Results Storage" })
}

resource "aws_s3_bucket_versioning" "analysis_results" {
  bucket = aws_s3_bucket.analysis_results.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "analysis_results" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.analysis_results.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "analysis_results" {
  bucket = aws_s3_bucket.analysis_results.id
  
  rule {
    id     = "transition-to-standard-ia"
    status = "Enabled"
    
    transition {
      days          = var.analysis_results_standard_ia_transition_days
      storage_class = "STANDARD_IA"
    }
  }
  
  rule {
    id     = "expiration"
    status = "Enabled"
    
    expiration {
      days = var.analysis_results_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "analysis_results" {
  bucket                  = aws_s3_bucket.analysis_results.id
  block_public_acls       = var.block_public_access
  block_public_policy     = var.block_public_access
  ignore_public_acls      = var.block_public_access
  restrict_public_buckets = var.block_public_access
}

# -------------------------------------------------------------
# Archive Storage Bucket
# -------------------------------------------------------------
resource "aws_s3_bucket" "archive_storage" {
  bucket = local.archive_storage_bucket_name
  tags   = merge(var.tags, local.common_tags, { Purpose = "Long-term Data Archival" })
}

resource "aws_s3_bucket_versioning" "archive_storage" {
  bucket = aws_s3_bucket.archive_storage.id
  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "archive_storage" {
  count  = var.enable_encryption ? 1 : 0
  bucket = aws_s3_bucket.archive_storage.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "archive_storage" {
  bucket = aws_s3_bucket.archive_storage.id
  
  rule {
    id     = "transition-to-deep-archive"
    status = "Enabled"
    
    transition {
      days          = var.archive_storage_deep_archive_transition_days
      storage_class = "DEEP_ARCHIVE"
    }
  }
  
  rule {
    id     = "expiration"
    status = "Enabled"
    
    expiration {
      days = var.archive_storage_expiration_days
    }
  }
}

resource "aws_s3_bucket_public_access_block" "archive_storage" {
  bucket                  = aws_s3_bucket.archive_storage.id
  block_public_acls       = var.block_public_access
  block_public_policy     = var.block_public_access
  ignore_public_acls      = var.block_public_access
  restrict_public_buckets = var.block_public_access
}