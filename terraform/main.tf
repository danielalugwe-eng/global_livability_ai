# ─────────────────────────────────────────────────────────────────────────────
# Terraform — Global Livability AI Infrastructure
# ─────────────────────────────────────────────────────────────────────────────
# Provisions on AWS:
#   • S3 bucket  — versioned data lake (raw / processed / features / models)
#   • ECR repo   — Docker image registry
#   • ECS Fargate cluster + service — runs Streamlit dashboard
#   • ECS task   — one-shot pipeline runner
#   • IAM roles  — least-privilege policies
#   • CloudWatch — log groups
#
# Usage:
#   cd terraform
#   terraform init
#   terraform plan -out=plan.tfplan
#   terraform apply plan.tfplan
# ─────────────────────────────────────────────────────────────────────────────

terraform {
  required_version = ">= 1.7.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
  }

  # Remote state — store in the same S3 bucket after first apply
  # Uncomment after first `terraform apply`
  # backend "s3" {
  #   bucket  = "global-livability-ai-tfstate"
  #   key     = "terraform/state"
  #   region  = var.aws_region
  #   encrypt = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "global-livability-ai"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}
