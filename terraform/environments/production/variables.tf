variable "region" {
  description = "The AWS region to deploy to"
  type        = string
  default     = "us-west-2"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "List of availability zones to use"
  type        = list(string)
  default     = ["us-west-2a", "us-west-2b", "us-west-2c"]
}

# Database Variables
variable "db_instance_class" {
  description = "The instance type of the RDS instance"
  type        = string
  default     = "db.r5.large"
}

variable "db_allocated_storage" {
  description = "The amount of allocated storage in gibibytes"
  type        = number
  default     = 100
}

variable "db_max_allocated_storage" {
  description = "The upper limit to which Amazon RDS can automatically scale the storage"
  type        = number
  default     = 500
}

variable "db_name" {
  description = "The name of the database to create when the DB instance is created"
  type        = string
  default     = "terrafusion"
}

variable "db_username" {
  description = "Username for the master DB user"
  type        = string
  default     = "postgres"
}

variable "db_port" {
  description = "The port on which the DB accepts connections"
  type        = number
  default     = 5432
}

# Container Variables
variable "container_image" {
  description = "The container image to deploy"
  type        = string
  default     = "123456789012.dkr.ecr.us-west-2.amazonaws.com/terrafusion:latest"
}

variable "container_port" {
  description = "The port exposed by the container"
  type        = number
  default     = 5000
}

variable "container_cpu" {
  description = "The number of CPU units to reserve for the container"
  type        = number
  default     = 1024
}

variable "container_memory" {
  description = "The amount of memory to reserve for the container in MiB"
  type        = number
  default     = 2048
}

variable "container_desired_count" {
  description = "The number of instances of the task definition to run"
  type        = number
  default     = 2
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

# Load Balancer Variables
variable "health_check_path" {
  description = "The path for the health check"
  type        = string
  default     = "/health"
}

variable "certificate_arn" {
  description = "The ARN of the SSL certificate"
  type        = string
  default     = null
}

# Route 53 Variables
variable "domain_name" {
  description = "The domain name to use for the application"
  type        = string
  default     = null
}

variable "route53_zone_id" {
  description = "The ID of the Route 53 hosted zone"
  type        = string
  default     = null
}

# Monitoring Variables
variable "alarm_email" {
  description = "Email address to send CloudWatch alarms"
  type        = string
  default     = null
}