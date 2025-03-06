output "ecs_cluster_id" {
  value       = aws_ecs_cluster.main.id
  description = "ID of the created ECS cluster"
}

output "ecs_cluster_name" {
  value       = aws_ecs_cluster.main.name
  description = "Name of the created ECS cluster"
}

output "ecs_service_names" {
  value       = {for i, name in var.service_names : name => aws_ecs_service.main[i].name}
  description = "Map of service names for each component"
}

output "ecs_service_arns" {
  value       = {for i, name in var.service_names : name => aws_ecs_service.main[i].id}
  description = "Map of service ARNs for each component"
}

output "ecs_task_definition_arns" {
  value       = {for i, name in var.service_names : name => aws_ecs_task_definition.main[i].arn}
  description = "Map of task definition ARNs for each component"
}

output "load_balancer_dns_name" {
  value       = aws_lb.main.dns_name
  description = "DNS name of the application load balancer"
}

output "load_balancer_arn" {
  value       = aws_lb.main.arn
  description = "ARN of the application load balancer"
}

output "target_group_arns" {
  value       = {for i, name in var.service_names : name => aws_lb_target_group.main[i].arn}
  description = "Map of target group ARNs for each component"
}

output "security_group_lb_id" {
  value       = aws_security_group.alb.id
  description = "ID of the security group for the load balancer"
}

output "security_group_ecs_id" {
  value       = aws_security_group.ecs.id
  description = "ID of the security group for ECS tasks"
}

output "ecs_task_execution_role_arn" {
  value       = var.task_execution_role_arn
  description = "ARN of the IAM role used for ECS task execution"
}

output "ecs_task_role_arn" {
  value       = var.task_role_arn
  description = "ARN of the IAM role used by the ECS tasks"
}