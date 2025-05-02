variable "app_name" {
  description = "The name of the application"
  type        = string
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
}

variable "retention_in_days" {
  description = "Log retention period in days"
  type        = number
  default     = 90
}

variable "alarm_email" {
  description = "Email address to send CloudWatch alarms"
  type        = string
  default     = null
}

variable "tags" {
  description = "A mapping of tags to assign to resources"
  type        = map(string)
  default     = {}
}

# Create CloudWatch Log Group for application logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/ecs/${var.app_name}-${var.environment}"
  retention_in_days = var.retention_in_days
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-logs"
      Environment = var.environment
    },
    var.tags
  )
}

# Create CloudWatch Dashboard for the application
resource "aws_cloudwatch_dashboard" "app_dashboard" {
  dashboard_name = "${var.app_name}-${var.environment}"
  
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
            ["AWS/ECS", "CPUUtilization", "ServiceName", "${var.app_name}-service-${var.environment}", "ClusterName", "${var.app_name}-${var.environment}", { "stat": "Average" }]
          ]
          view    = "timeSeries"
          region  = data.aws_region.current.name
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
            ["AWS/ECS", "MemoryUtilization", "ServiceName", "${var.app_name}-service-${var.environment}", "ClusterName", "${var.app_name}-${var.environment}", { "stat": "Average" }]
          ]
          view    = "timeSeries"
          region  = data.aws_region.current.name
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
            ["AWS/ApplicationELB", "RequestCount", "LoadBalancer", "app/${var.app_name}-alb-${var.environment}/", { "stat": "Sum", "period": 60 }]
          ]
          view    = "timeSeries"
          region  = data.aws_region.current.name
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
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "app/${var.app_name}-alb-${var.environment}/", { "stat": "Average", "period": 60 }]
          ]
          view    = "timeSeries"
          region  = data.aws_region.current.name
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
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", "${var.app_name}-db-${var.environment}", { "stat": "Average" }],
            ["AWS/RDS", "DatabaseConnections", "DBInstanceIdentifier", "${var.app_name}-db-${var.environment}", { "stat": "Average", "yAxis": "right" }]
          ]
          view    = "timeSeries"
          region  = data.aws_region.current.name
          title   = "RDS Utilization"
        }
      },
      {
        type   = "log"
        x      = 0
        y      = 18
        width  = 24
        height = 6
        properties = {
          query   = "fields @timestamp, @message\n| filter @message like /ERROR/\n| sort @timestamp desc\n| limit 20"
          region  = data.aws_region.current.name
          title   = "Recent Application Errors"
          view    = "table"
          logGroupName = aws_cloudwatch_log_group.app_logs.name
        }
      }
    ]
  })
}

# Create SNS Topic for alarms
resource "aws_sns_topic" "alarms" {
  count = var.alarm_email != null ? 1 : 0
  name  = "${var.app_name}-${var.environment}-alarms"
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-alarms"
      Environment = var.environment
    },
    var.tags
  )
}

# Create SNS Topic Subscription for email alerts
resource "aws_sns_topic_subscription" "alarm_email" {
  count     = var.alarm_email != null ? 1 : 0
  topic_arn = aws_sns_topic.alarms[0].arn
  protocol  = "email"
  endpoint  = var.alarm_email
}

# High CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  count               = var.alarm_email != null ? 1 : 0
  alarm_name          = "${var.app_name}-${var.environment}-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ECS CPU utilization"
  
  dimensions = {
    ClusterName = "${var.app_name}-${var.environment}"
    ServiceName = "${var.app_name}-service-${var.environment}"
  }
  
  alarm_actions = [aws_sns_topic.alarms[0].arn]
  ok_actions    = [aws_sns_topic.alarms[0].arn]
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-cpu-high"
      Environment = var.environment
    },
    var.tags
  )
}

# High Memory Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "memory_high" {
  count               = var.alarm_email != null ? 1 : 0
  alarm_name          = "${var.app_name}-${var.environment}-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors ECS memory utilization"
  
  dimensions = {
    ClusterName = "${var.app_name}-${var.environment}"
    ServiceName = "${var.app_name}-service-${var.environment}"
  }
  
  alarm_actions = [aws_sns_topic.alarms[0].arn]
  ok_actions    = [aws_sns_topic.alarms[0].arn]
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-memory-high"
      Environment = var.environment
    },
    var.tags
  )
}

# Database High CPU Utilization Alarm
resource "aws_cloudwatch_metric_alarm" "db_cpu_high" {
  count               = var.alarm_email != null ? 1 : 0
  alarm_name          = "${var.app_name}-${var.environment}-db-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors RDS CPU utilization"
  
  dimensions = {
    DBInstanceIdentifier = "${var.app_name}-db-${var.environment}"
  }
  
  alarm_actions = [aws_sns_topic.alarms[0].arn]
  ok_actions    = [aws_sns_topic.alarms[0].arn]
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-db-cpu-high"
      Environment = var.environment
    },
    var.tags
  )
}

# 5XX Error Rate Alarm
resource "aws_cloudwatch_metric_alarm" "http_5xx" {
  count               = var.alarm_email != null ? 1 : 0
  alarm_name          = "${var.app_name}-${var.environment}-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors the HTTP 5XX error rate"
  
  dimensions = {
    LoadBalancer = "app/${var.app_name}-alb-${var.environment}/"
  }
  
  alarm_actions = [aws_sns_topic.alarms[0].arn]
  ok_actions    = [aws_sns_topic.alarms[0].arn]
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-5xx-errors"
      Environment = var.environment
    },
    var.tags
  )
}

# Create IAM role for RDS monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.app_name}-${var.environment}-rds-monitoring-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    {
      Name        = "${var.app_name}-${var.environment}-rds-monitoring-role"
      Environment = var.environment
    },
    var.tags
  )
}

# Attach policy to RDS monitoring role
resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

data "aws_region" "current" {}

output "log_group_name" {
  description = "Name of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "log_group_arn" {
  description = "ARN of the CloudWatch Log Group"
  value       = aws_cloudwatch_log_group.app_logs.arn
}

output "dashboard_name" {
  description = "Name of the CloudWatch Dashboard"
  value       = aws_cloudwatch_dashboard.app_dashboard.dashboard_name
}

output "rds_monitoring_role_arn" {
  description = "ARN of the IAM role for RDS monitoring"
  value       = aws_iam_role.rds_monitoring.arn
}

output "alarm_topic_arn" {
  description = "ARN of the SNS topic for alarms"
  value       = var.alarm_email != null ? aws_sns_topic.alarms[0].arn : null
}