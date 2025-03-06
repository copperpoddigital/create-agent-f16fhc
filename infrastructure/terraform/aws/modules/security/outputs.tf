output "kms_key_id" {
  description = "ID of the KMS key used for encrypting sensitive freight pricing data"
  value       = aws_kms_key.main.key_id
  sensitive   = false
}

output "kms_key_arn" {
  description = "ARN of the KMS key used for encrypting sensitive freight pricing data"
  value       = aws_kms_key.main.arn
  sensitive   = false
}

output "waf_web_acl_id" {
  description = "ID of the WAF Web ACL used for protecting API endpoints"
  value       = var.enable_waf ? aws_wafv2_web_acl.main[0].id : null
  sensitive   = false
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role used for ECS task execution"
  value       = aws_iam_role.ecs_task_execution.arn
  sensitive   = false
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role used by ECS tasks at runtime"
  value       = aws_iam_role.ecs_task.arn
  sensitive   = false
}

output "bastion_security_group_id" {
  description = "ID of the security group for the bastion host"
  value       = var.enable_bastion ? aws_security_group.bastion[0].id : null
  sensitive   = false
}

output "alb_security_group_id" {
  description = "ID of the security group for the application load balancer"
  value       = aws_security_group.alb.id
  sensitive   = false
}

output "app_security_group_id" {
  description = "ID of the security group for the application tier"
  value       = aws_security_group.app.id
  sensitive   = false
}

output "data_security_group_id" {
  description = "ID of the security group for the data tier"
  value       = aws_security_group.data.id
  sensitive   = false
}