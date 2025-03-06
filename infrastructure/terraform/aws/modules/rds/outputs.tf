# -----------------------------------------------------------------------------
# Outputs for RDS PostgreSQL with TimescaleDB module
# -----------------------------------------------------------------------------

# Connection details for application integration
output "db_instance_endpoint" {
  description = "Endpoint of the RDS instance for application connection"
  value       = aws_db_instance.this.endpoint
}

output "db_instance_address" {
  description = "Address of the RDS instance without port information"
  value       = aws_db_instance.this.address
}

output "db_instance_port" {
  description = "Port on which the database instance accepts connections"
  value       = aws_db_instance.this.port
}

output "db_instance_name" {
  description = "Name of the created database"
  value       = aws_db_instance.this.db_name
}

# Resource identifiers for reference in other modules
output "db_instance_id" {
  description = "Identifier of the RDS instance for reference in other resources"
  value       = aws_db_instance.this.id
}

output "db_subnet_group_name" {
  description = "Name of the DB subnet group for reference in other resources"
  value       = aws_db_subnet_group.this.name
}

output "db_parameter_group_name" {
  description = "Name of the parameter group for PostgreSQL with TimescaleDB configuration"
  value       = aws_db_parameter_group.this.name
}

output "db_arn" {
  description = "ARN of the RDS instance for IAM policy references"
  value       = aws_db_instance.this.arn
}

# Security-related outputs
output "db_security_group_id" {
  description = "ID of the security group created for database access"
  value       = aws_security_group.this.id
}

output "db_kms_key_id" {
  description = "ID of the KMS key used for database encryption"
  value       = var.db_storage_encrypted ? aws_kms_key.this[0].key_id : null
}