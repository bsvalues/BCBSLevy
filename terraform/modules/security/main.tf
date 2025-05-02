variable "app_name" {
  description = "The name of the application"
  type        = string
}

variable "environment" {
  description = "The deployment environment (dev, staging, prod)"
  type        = string
}

variable "vpc_id" {
  description = "The ID of the VPC"
  type        = string
}

variable "alb_subnet_ids" {
  description = "List of subnet IDs for the ALB"
  type        = list(string)
}

variable "tags" {
  description = "A mapping of tags to assign to resources"
  type        = map(string)
  default     = {}
}

# Security Group for Application Load Balancer
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-alb-sg-${var.environment}"
  description = "Security group for the application load balancer"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP traffic from internet"
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS traffic from internet"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-alb-sg-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# Security Group for ECS Tasks
resource "aws_security_group" "ecs_tasks" {
  name        = "${var.app_name}-ecs-sg-${var.environment}"
  description = "Security group for the ECS tasks"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 5000
    to_port         = 5000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow traffic from ALB to Flask application"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-ecs-sg-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# Security Group for RDS
resource "aws_security_group" "db" {
  name        = "${var.app_name}-db-sg-${var.environment}"
  description = "Security group for the database"
  vpc_id      = var.vpc_id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
    description     = "Allow PostgreSQL traffic from ECS tasks"
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-db-sg-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# WAF Web ACL
resource "aws_wafv2_web_acl" "main" {
  name        = "${var.app_name}-waf-${var.environment}"
  description = "WAF ACL for ${var.app_name} ${var.environment}"
  scope       = "REGIONAL"
  
  default_action {
    allow {}
  }
  
  # Amazon managed rule groups
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
    priority = 1
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  # SQL Injection protection
  rule {
    name     = "AWS-AWSManagedRulesSQLiRuleSet"
    priority = 2
    
    override_action {
      none {}
    }
    
    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesSQLiRuleSet"
        vendor_name = "AWS"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesSQLiRuleSet"
      sampled_requests_enabled   = true
    }
  }
  
  # Rate limiting rule
  rule {
    name     = "RateLimitRule"
    priority = 3
    
    action {
      block {}
    }
    
    statement {
      rate_based_statement {
        limit              = 3000
        aggregate_key_type = "IP"
      }
    }
    
    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateLimitRule"
      sampled_requests_enabled   = true
    }
  }
  
  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.app_name}-web-acl-${var.environment}"
    sampled_requests_enabled   = true
  }
  
  tags = merge(
    {
      Name        = "${var.app_name}-waf-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# IAM role for ECS Task Execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.app_name}-task-execution-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    {
      Name        = "${var.app_name}-task-execution-role-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# Attach policies to ECS Task Execution role
resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# IAM role for ECS Tasks
resource "aws_iam_role" "ecs_task" {
  name = "${var.app_name}-task-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    {
      Name        = "${var.app_name}-task-role-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

# Policy for ECS Tasks to access Secrets Manager
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.app_name}-secrets-access-policy-${var.environment}"
  description = "Policy for accessing secrets in Secrets Manager"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:secretsmanager:*:*:secret:${var.app_name}-*"
      }
    ]
  })
}

# Attach secrets access policy to ECS Task role
resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# Create KMS key for encryption
resource "aws_kms_key" "app_encryption" {
  description             = "KMS key for encrypting ${var.app_name} data"
  deletion_window_in_days = 30
  enable_key_rotation     = true
  
  tags = merge(
    {
      Name        = "${var.app_name}-kms-key-${var.environment}"
      Environment = var.environment
    },
    var.tags
  )
}

resource "aws_kms_alias" "app_encryption" {
  name          = "alias/${var.app_name}-${var.environment}"
  target_key_id = aws_kms_key.app_encryption.key_id
}

# Outputs
output "alb_security_group_id" {
  description = "Security Group ID for the ALB"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "Security Group ID for the ECS tasks"
  value       = aws_security_group.ecs_tasks.id
}

output "db_security_group_id" {
  description = "Security Group ID for the database"
  value       = aws_security_group.db.id
}

output "waf_web_acl_arn" {
  description = "ARN of the WAF Web ACL"
  value       = aws_wafv2_web_acl.main.arn
}

output "task_execution_role_arn" {
  description = "ARN of the Task Execution IAM Role"
  value       = aws_iam_role.ecs_task_execution.arn
}

output "task_role_arn" {
  description = "ARN of the Task IAM Role"
  value       = aws_iam_role.ecs_task.arn
}

output "kms_key_arn" {
  description = "ARN of the KMS Key"
  value       = aws_kms_key.app_encryption.arn
}