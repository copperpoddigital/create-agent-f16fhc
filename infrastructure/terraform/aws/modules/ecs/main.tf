# Local variables
locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Get current AWS region
data "aws_region" "current" {}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = local.name_prefix
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = var.tags
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name
  
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]
  
  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = 1
  }
}

# Service Discovery Namespace
resource "aws_service_discovery_private_dns_namespace" "main" {
  count = var.enable_service_discovery ? 1 : 0
  
  name        = "${var.project_name}.local"
  vpc         = var.vpc_id
  description = "Private DNS namespace for ${var.project_name} services"
  
  tags = var.tags
}

# Service Discovery Services
resource "aws_service_discovery_service" "main" {
  count = var.enable_service_discovery ? length(var.service_names) : 0
  
  name = var.service_names[count.index]
  
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main[0].id
    
    dns_records {
      ttl  = 10
      type = "A"
    }
    
    routing_policy = "MULTIVALUE"
  }
  
  health_check_custom_config {
    failure_threshold = 1
  }
  
  tags = var.tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "main" {
  count = length(var.service_names)
  
  name              = "/ecs/${local.name_prefix}/${var.service_names[count.index]}"
  retention_in_days = var.logs_retention_in_days
  
  tags = var.tags
}

# Security Group for ALB
resource "aws_security_group" "alb" {
  name        = "${local.name_prefix}-alb-sg"
  description = "Security group for the application load balancer"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP from internet"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS from internet"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-alb-sg"
  })
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs" {
  name        = "${local.name_prefix}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = var.app_port
    to_port         = var.app_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow traffic from ALB"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-ecs-sg"
  })
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = var.public_subnet_ids
  
  enable_deletion_protection = false
  enable_http2              = true
  idle_timeout              = 60
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-alb"
  })
}

# ALB Target Groups
resource "aws_lb_target_group" "main" {
  count = length(var.service_names)
  
  name        = "${local.name_prefix}-${var.service_names[count.index]}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"
  
  deregistration_delay = 30
  
  health_check {
    enabled             = true
    path                = var.health_check_path
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 30
    matcher             = "200-299"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-${var.service_names[count.index]}-tg"
  })
}

# ALB HTTP Listener
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main[0].arn
  }
}

# ALB Listener Rules
resource "aws_lb_listener_rule" "main" {
  count = length(var.service_names) - 1
  
  listener_arn = aws_lb_listener.http.arn
  priority     = 100 + count.index
  
  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main[count.index + 1].arn
  }
  
  condition {
    path_pattern {
      values = ["/${var.service_names[count.index + 1]}/*"]
    }
  }
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "main" {
  count = length(var.service_names)
  
  family                   = "${local.name_prefix}-${var.service_names[count.index]}"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = var.task_execution_role_arn
  task_role_arn            = var.task_role_arn
  
  container_definitions = jsonencode([
    {
      name         = var.service_names[count.index]
      image        = "${var.app_image}-${var.service_names[count.index]}:latest"
      essential    = true
      portMappings = [
        {
          containerPort = var.app_port
          hostPort      = var.app_port
          protocol      = "tcp"
        }
      ]
      environment = var.environment_variables
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.main[count.index].name
          "awslogs-region"        = data.aws_region.current.name
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-${var.service_names[count.index]}-task"
  })
}

# ECS Services
resource "aws_ecs_service" "main" {
  count = length(var.service_names)
  
  name                               = "${local.name_prefix}-${var.service_names[count.index]}"
  cluster                           = aws_ecs_cluster.main.id
  task_definition                   = aws_ecs_task_definition.main[count.index].arn
  desired_count                     = var.service_min_capacities[var.service_names[count.index]]
  launch_type                       = "FARGATE"
  platform_version                  = "LATEST"
  scheduling_strategy               = "REPLICA"
  deployment_maximum_percent        = 200
  deployment_minimum_healthy_percent = 100
  health_check_grace_period_seconds = 60
  enable_execute_command            = var.enable_execute_command
  
  network_configuration {
    subnets          = var.private_app_subnet_ids
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.main[count.index].arn
    container_name   = var.service_names[count.index]
    container_port   = var.app_port
  }
  
  service_registries {
    registry_arn = var.enable_service_discovery ? aws_service_discovery_service.main[count.index].arn : null
  }
  
  deployment_controller {
    type = var.deployment_strategy == "blue-green" ? "CODE_DEPLOY" : "ECS"
  }
  
  tags = merge(var.tags, {
    Name = "${local.name_prefix}-${var.service_names[count.index]}-service"
  })
}

# Auto-scaling targets
resource "aws_appautoscaling_target" "main" {
  count = length(var.service_names)
  
  max_capacity       = var.service_max_capacities[var.service_names[count.index]]
  min_capacity       = var.service_min_capacities[var.service_names[count.index]]
  resource_id        = format("service/%s/%s", aws_ecs_cluster.main.name, aws_ecs_service.main[count.index].name)
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# CPU-based auto-scaling policies
resource "aws_appautoscaling_policy" "cpu" {
  count = length(var.service_names)
  
  name               = "${local.name_prefix}-${var.service_names[count.index]}-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.main[count.index].scalable_dimension
  service_namespace  = aws_appautoscaling_target.main[count.index].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = var.service_cpu_thresholds[var.service_names[count.index]]
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Memory-based auto-scaling policies
resource "aws_appautoscaling_policy" "memory" {
  count = length(var.service_names)
  
  name               = "${local.name_prefix}-${var.service_names[count.index]}-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main[count.index].resource_id
  scalable_dimension = aws_appautoscaling_target.main[count.index].scalable_dimension
  service_namespace  = aws_appautoscaling_target.main[count.index].service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    target_value       = 80
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# CloudWatch Alarms for service health
resource "aws_cloudwatch_metric_alarm" "service_health" {
  count = length(var.service_names)
  
  alarm_name          = "${local.name_prefix}-${var.service_names[count.index]}-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Average"
  threshold           = 1
  alarm_description   = "This alarm monitors the health of the ${var.service_names[count.index]} service"
  
  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
    TargetGroup  = aws_lb_target_group.main[count.index].arn_suffix
  }
  
  alarm_actions             = var.sns_topic_arn != null ? [var.sns_topic_arn] : []
  ok_actions                = var.sns_topic_arn != null ? [var.sns_topic_arn] : []
  insufficient_data_actions = var.sns_topic_arn != null ? [var.sns_topic_arn] : []
  
  tags = var.tags
}

# Outputs
output "ecs_cluster_id" {
  description = "ID of the created ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_cluster_name" {
  description = "Name of the created ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_names" {
  description = "Map of service names for each component"
  value       = { for i, name in var.service_names : name => aws_ecs_service.main[i].name }
}

output "ecs_service_arns" {
  description = "Map of service ARNs for each component"
  value       = { for i, name in var.service_names : name => aws_ecs_service.main[i].id }
}

output "ecs_task_definition_arns" {
  description = "Map of task definition ARNs for each component"
  value       = { for i, name in var.service_names : name => aws_ecs_task_definition.main[i].arn }
}

output "load_balancer_dns_name" {
  description = "DNS name of the application load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_arn" {
  description = "ARN of the application load balancer"
  value       = aws_lb.main.arn
}

output "target_group_arns" {
  description = "Map of target group ARNs for each component"
  value       = { for i, name in var.service_names : name => aws_lb_target_group.main[i].arn }
}

output "security_group_lb_id" {
  description = "ID of the security group for the load balancer"
  value       = aws_security_group.alb.id
}

output "security_group_ecs_id" {
  description = "ID of the security group for ECS tasks"
  value       = aws_security_group.ecs.id
}

output "ecs_task_execution_role_arn" {
  description = "ARN of the IAM role used for ECS task execution"
  value       = var.task_execution_role_arn
}

output "ecs_task_role_arn" {
  description = "ARN of the IAM role used by the ECS tasks"
  value       = var.task_role_arn
}