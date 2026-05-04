# ─────────────────────────────────────────────────────────────────────────────
# variables.tf
# ─────────────────────────────────────────────────────────────────────────────

variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev / staging / prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of: dev, staging, prod"
  }
}

variable "project" {
  description = "Short project identifier used in resource names"
  type        = string
  default     = "gla"   # global-livability-ai
}

variable "app_image_tag" {
  description = "Docker image tag to deploy"
  type        = string
  default     = "latest"
}

variable "ecs_cpu" {
  description = "Fargate task CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 1024
}

variable "ecs_memory" {
  description = "Fargate task memory in MiB"
  type        = number
  default     = 2048
}

variable "app_desired_count" {
  description = "Number of Streamlit app replicas"
  type        = number
  default     = 1
}
