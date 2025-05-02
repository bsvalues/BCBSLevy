variable "app_name" {
  description = "The name of the application"
  type        = string
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
}

variable "container_image" {
  description = "The container image to deploy"
  type        = string
}

variable "container_port" {
  description = "The port exposed by the container"
  type        = number
  default     = 5000
}

variable "cpu" {
  description = "The number of CPU units to reserve for the container"
  type        = number
  default     = 1024
}

variable "memory" {
  description = "The amount of memory to reserve for the container in MiB"
  type        = number
  default     = 2048
}

variable "desired_count" {
  description = "The number of instances of the task definition to run"
  type        = number
  default     = 2
}

variable "execution_role_arn" {
  description = "ARN of the task execution role"
  type        = string
}

variable "task_role_arn" {
  description = "ARN of the task role"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "subnet_ids" {
  description = "The IDs of the subnets for the ECS service"
  type        = list(string)
}

variable "security_group_ids" {
  description = "The IDs of the security groups for the ECS service"
  type        = list(string)
}

variable "target_group_arn" {
  description = "The ARN of the target group for the ALB"
  type        = string
}

variable "log_group_name" {
  description = "The name of the CloudWatch log group for the container logs"
  type        = string
}

variable "database_url_secret_arn" {
  description = "The ARN of the Secrets Manager secret for the database URL"
  type        = string
}

variable "session_secret_arn" {
  description = "The ARN of the Secrets Manager secret for the session secret"
  type        = string
}

variable "region" {
  description = "The AWS region to deploy to"
  type        = string
}

variable "tags" {
  description = "A mapping of tags to assign to resources"
  type        = map(string)
  default     = {}
}

variable "autoscaling_min_capacity" {
  description = "The minimum number of tasks for autoscaling"
  type        = number
  default     = 2
}

variable "autoscaling_max_capacity" {
  description = "The maximum number of tasks for autoscaling"
  type        = number
  default     = 10
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-ecs-cluster-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# ECS Task Definition with template file
data "template_file" "container_definition" {
  template = file("${path.module}/task-definition.json")
  
  vars = {
    app_name                = var.app_name
    container_image         = var.container_image
    container_port          = var.container_port
    environment             = var.environment
    log_group               = var.log_group_name
    region                  = var.region
    cpu                     = var.cpu
    memory                  = var.memory
    execution_role_arn      = var.execution_role_arn
    task_role_arn           = var.task_role_arn
    database_url_secret_arn = var.database_url_secret_arn
    session_secret_arn      = var.session_secret_arn
    jsonencode              = jsonencode
    tags                    = jsonencode(merge(
      {
        Name        = "${var.app_name}-task-definition-${var.environment}"
        Environment = var.environment
      },
      var.tags
    ))
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "main" {
  family                   = "${var.app_name}-${var.environment}"
  execution_role_arn       = var.execution_role_arn
  task_role_arn            = var.task_role_arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.cpu
  memory                   = var.memory
  container_definitions    = data.template_file.container_definition.rendered
  
  tags = merge(
    {
      Name        = "${var.app_name}-task-definition-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# ECS Service
resource "aws_ecs_service" "main" {
  name             = "${var.app_name}-service-${var.environment}"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.main.arn
  desired_count    = var.desired_count
  launch_type      = "FARGATE"
  platform_version = "LATEST"
  
  network_configuration {
    subnets          = var.subnet_ids
    security_groups  = var.security_group_ids
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = var.app_name
    container_port   = var.container_port
  }
  
  deployment_controller {
    type = "ECS"
  }
  
  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }
  
  lifecycle {
    ignore_changes = [desired_count, task_definition]
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-ecs-service-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# Application Auto Scaling Target
resource "aws_appautoscaling_target" "main" {
  max_capacity       = var.autoscaling_max_capacity
  min_capacity       = var.autoscaling_min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.main.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

# Application Auto Scaling Policy for CPU
resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.app_name}-cpu-autoscaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main.resource_id
  scalable_dimension = aws_appautoscaling_target.main.scalable_dimension
  service_namespace  = aws_appautoscaling_target.main.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Application Auto Scaling Policy for Memory
resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.app_name}-memory-autoscaling-${var.environment}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.main.resource_id
  scalable_dimension = aws_appautoscaling_target.main.scalable_dimension
  service_namespace  = aws_appautoscaling_target.main.service_namespace
  
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
    
    target_value       = 70
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}

# Amazon ECR Repository
resource "aws_ecr_repository" "main" {
  name                 = "${var.app_name}-${var.environment}"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-ecr-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# ECR Lifecycle Policy
resource "aws_ecr_lifecycle_policy" "main" {
  repository = aws_ecr_repository.main.name
  
  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 30 images"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 30
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# Outputs
output "cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "cluster_name" {
  description = "The name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "service_id" {
  description = "The ID of the ECS service"
  value       = aws_ecs_service.main.id
}

output "service_name" {
  description = "The name of the ECS service"
  value       = aws_ecs_service.main.name
}

output "task_definition_arn" {
  description = "The ARN of the task definition"
  value       = aws_ecs_task_definition.main.arn
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.main.repository_url
}