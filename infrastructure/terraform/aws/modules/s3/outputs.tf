# -------------------------------------------------------------
# S3 Bucket Outputs - CSV Storage
# -------------------------------------------------------------
output "csv_storage_bucket_id" {
  description = "The ID of the S3 bucket for CSV file storage"
  value       = aws_s3_bucket.csv_storage.id
}

output "csv_storage_bucket_arn" {
  description = "The ARN of the S3 bucket for CSV file storage"
  value       = aws_s3_bucket.csv_storage.arn
}

output "csv_storage_bucket_name" {
  description = "The name of the S3 bucket for CSV file storage"
  value       = aws_s3_bucket.csv_storage.bucket
}

# -------------------------------------------------------------
# S3 Bucket Outputs - Analysis Results
# -------------------------------------------------------------
output "analysis_results_bucket_id" {
  description = "The ID of the S3 bucket for analysis results storage"
  value       = aws_s3_bucket.analysis_results.id
}

output "analysis_results_bucket_arn" {
  description = "The ARN of the S3 bucket for analysis results storage"
  value       = aws_s3_bucket.analysis_results.arn
}

output "analysis_results_bucket_name" {
  description = "The name of the S3 bucket for analysis results storage"
  value       = aws_s3_bucket.analysis_results.bucket
}

# -------------------------------------------------------------
# S3 Bucket Outputs - Archive Storage
# -------------------------------------------------------------
output "archive_storage_bucket_id" {
  description = "The ID of the S3 bucket for long-term data archival"
  value       = aws_s3_bucket.archive_storage.id
}

output "archive_storage_bucket_arn" {
  description = "The ARN of the S3 bucket for long-term data archival"
  value       = aws_s3_bucket.archive_storage.arn
}

output "archive_storage_bucket_name" {
  description = "The name of the S3 bucket for long-term data archival"
  value       = aws_s3_bucket.archive_storage.bucket
}

# -------------------------------------------------------------
# Consolidated S3 Bucket Outputs
# -------------------------------------------------------------
output "s3_bucket_ids" {
  description = "Map of all S3 bucket IDs created by this module"
  value = {
    "csv_storage"     = aws_s3_bucket.csv_storage.id
    "analysis_results" = aws_s3_bucket.analysis_results.id
    "archive_storage" = aws_s3_bucket.archive_storage.id
  }
}