# Output values for the ElastiCache Redis cluster module
# These outputs provide connection information and resource identifiers
# for use by other Terraform modules or external systems

output "elasticache_replication_group_id" {
  description = "The ID of the ElastiCache replication group"
  value       = aws_elasticache_replication_group.redis.id
}

output "elasticache_primary_endpoint" {
  description = "The primary endpoint address for the ElastiCache Redis cluster"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "elasticache_reader_endpoint" {
  description = "The reader endpoint address for the ElastiCache Redis cluster"
  value       = aws_elasticache_replication_group.redis.reader_endpoint_address
}

output "elasticache_port" {
  description = "The port number on which the ElastiCache Redis cluster accepts connections"
  value       = aws_elasticache_replication_group.redis.port
}

output "elasticache_security_group_id" {
  description = "The ID of the security group created for the ElastiCache Redis cluster"
  value       = aws_security_group.redis.id
}

output "elasticache_subnet_group_name" {
  description = "The name of the subnet group created for the ElastiCache Redis cluster"
  value       = aws_elasticache_subnet_group.redis.name
}