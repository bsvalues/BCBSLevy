provider "aws" {
  region = var.region
}

terraform {
  required_version = ">= 1.0.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
  
  backend "s3" {
    # These values should be configured during initialization using -backend-config
    # bucket         = "terrafusion-terraform-state-prod"
    # key            = "terraform/state/terrafusion-prod.tfstate"
    # region         = "us-west-2"
    # dynamodb_table = "terrafusion-terraform-locks-prod"
    # encrypt        = true
  }
}

locals {
  app_name    = "terrafusion"
  environment = "prod"
  tags = {
    Application = "TerraFusion"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

module "network" {
  source = "../../modules/network"
  
  app_name           = local.app_name
  environment        = local.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  
  tags = local.tags
}

module "security" {
  source = "../../modules/security"
  
  app_name        = local.app_name
  environment     = local.environment
  vpc_id          = module.network.vpc_id
  alb_subnet_ids  = module.network.public_subnet_ids
  
  tags = local.tags
}

module "monitoring" {
  source = "../../modules/monitoring"
  
  app_name         = local.app_name
  environment      = local.environment
  retention_in_days = 90
  alarm_email      = var.alarm_email
  
  tags = local.tags
}

module "database" {
  source = "../../modules/database"
  
  identifier           = "${local.app_name}-db-${local.environment}"
  instance_class       = var.db_instance_class
  allocated_storage    = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  
  db_name              = var.db_name
  username             = var.db_username
  port                 = var.db_port
  
  vpc_security_group_ids = [module.security.db_security_group_id]
  subnet_ids             = module.network.database_subnet_ids
  
  multi_az               = true
  publicly_accessible    = false
  deletion_protection    = true
  
  backup_retention_period = 30
  backup_window           = "03:00-06:00"
  maintenance_window      = "Mon:00:00-Mon:03:00"
  
  monitoring_interval     = 60
  monitoring_role_arn     = module.monitoring.rds_monitoring_role_arn
  
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  tags = local.tags
}

module "loadbalancer" {
  source = "../../modules/loadbalancer"
  
  app_name          = local.app_name
  environment       = local.environment
  vpc_id            = module.network.vpc_id
  subnet_ids        = module.network.public_subnet_ids
  security_group_ids = [module.security.alb_security_group_id]
  
  health_check_path = var.health_check_path
  certificate_arn   = var.certificate_arn
  waf_web_acl_arn   = module.security.waf_web_acl_arn
  
  tags = local.tags
}

module "container" {
  source = "../../modules/container"
  
  app_name             = local.app_name
  environment          = local.environment
  container_image      = var.container_image
  container_port       = var.container_port
  
  cpu                  = var.container_cpu
  memory               = var.container_memory
  desired_count        = var.container_desired_count
  
  execution_role_arn   = module.security.task_execution_role_arn
  task_role_arn        = module.security.task_role_arn
  
  vpc_id               = module.network.vpc_id
  subnet_ids           = module.network.private_subnet_ids
  security_group_ids   = [module.security.ecs_security_group_id]
  
  target_group_arn     = module.loadbalancer.target_group_arn
  log_group_name       = module.monitoring.log_group_name
  
  database_url_secret_arn = module.database.secret_arn
  session_secret_arn      = aws_secretsmanager_secret.session_secret.arn
  
  region                = var.region
  
  autoscaling_min_capacity = var.autoscaling_min_capacity
  autoscaling_max_capacity = var.autoscaling_max_capacity
  
  tags = local.tags
}

# Session Secret in Secrets Manager
resource "random_password" "session_secret" {
  length           = 32
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}

resource "aws_secretsmanager_secret" "session_secret" {
  name = "${local.app_name}-session-secret-${local.environment}"
  
  tags = merge(
    {
      Name = "${local.app_name}-session-secret-${local.environment}"
    },
    local.tags
  )
}

resource "aws_secretsmanager_secret_version" "session_secret" {
  secret_id     = aws_secretsmanager_secret.session_secret.id
  secret_string = random_password.session_secret.result
}

# Route 53 DNS Record (if domain is provided)
resource "aws_route53_record" "app" {
  count   = var.domain_name != null ? 1 : 0
  zone_id = var.route53_zone_id
  name    = var.domain_name
  type    = "A"
  
  alias {
    name                   = module.loadbalancer.alb_dns_name
    zone_id                = module.loadbalancer.alb_zone_id
    evaluate_target_health = true
  }
}

# CloudWatch Dashboard for Application Metrics
resource "aws_cloudwatch_dashboard" "app_metrics" {
  dashboard_name = "${local.app_name}-${local.environment}-metrics"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", module.container.service_name, "ClusterName", module.container.cluster_name, { "stat": "Average" }]
          ]
          view    = "timeSeries"
          region  = var.region
          title   = "ECS CPU Utilization"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", module.container.service_name, "ClusterName", module.container.cluster_name, { "stat": "Average" }]
          ]
          view    = "timeSeries"
          region  = var.region
          title   = "ECS Memory Utilization"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", module.loadbalancer.alb_arn, { "stat": "Sum", "period": 60 }]
          ]
          view    = "timeSeries"
          region  = var.region
          title   = "ALB Request Count"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", module.loadbalancer.alb_arn, { "stat": "Average", "period": 60 }]
          ]
          view    = "timeSeries"
          region  = var.region
          title   = "ALB Response Time"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 12
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", module.database.instance_address, { "stat": "Average" }],
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", module.database.instance_address, { "stat": "Average", "yAxis": "right" }]
          ]
          view    = "timeSeries"
          region  = var.region
          title   = "RDS Utilization"
        }
      }
    ]
  })
}

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.network.vpc_id
}

output "alb_dns_name" {
  description = "The DNS name of the ALB"
  value       = module.loadbalancer.alb_dns_name
}

output "app_url" {
  description = "The URL of the application"
  value       = var.domain_name != null ? "https://${var.domain_name}" : "http://${module.loadbalancer.alb_dns_name}"
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = module.container.ecr_repository_url
}

output "db_endpoint" {
  description = "The endpoint of the database"
  value       = module.database.instance_endpoint
  sensitive   = true
}

output "cloudwatch_dashboard_url" {
  description = "The URL of the CloudWatch dashboard"
  value       = "https://console.aws.amazon.com/cloudwatch/home?region=${var.region}#dashboards:name=${aws_cloudwatch_dashboard.app_metrics.dashboard_name}"
}