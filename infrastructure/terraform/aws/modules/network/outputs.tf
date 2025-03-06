# Outputs for the AWS Network Module
# These values are exported for use by other modules that depend on this network infrastructure

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "The CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of IDs of public subnets"
  value       = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  description = "List of IDs of private application tier subnets"
  value       = aws_subnet.private_app[*].id
}

output "private_data_subnet_ids" {
  description = "List of IDs of private data tier subnets"
  value       = aws_subnet.private_data[*].id
}

output "internet_gateway_id" {
  description = "The ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of IDs of NAT Gateways"
  value       = aws_nat_gateway.main[*].id
}

output "public_route_table_id" {
  description = "The ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_app_route_table_ids" {
  description = "List of IDs of private application tier route tables"
  value       = aws_route_table.private_app[*].id
}

output "private_data_route_table_ids" {
  description = "List of IDs of private data tier route tables"
  value       = aws_route_table.private_data[*].id
}

output "vpc_endpoint_ids" {
  description = "Map of VPC endpoint IDs by service name"
  value       = {
    s3 = aws_vpc_endpoint.s3.id,
    dynamodb = aws_vpc_endpoint.dynamodb.id,
    ecr_api = aws_vpc_endpoint.ecr_api.id,
    ecr_dkr = aws_vpc_endpoint.ecr_dkr.id
  }
}