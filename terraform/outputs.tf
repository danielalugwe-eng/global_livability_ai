# ─────────────────────────────────────────────────────────────────────────────
# outputs.tf
# ─────────────────────────────────────────────────────────────────────────────

output "data_bucket_name" {
  description = "S3 bucket for all pipeline data"
  value       = aws_s3_bucket.data_lake.id
}

output "ecr_repository_url" {
  description = "ECR repository URL — use this as the image prefix when pushing"
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "app_service_name" {
  description = "ECS service running the Streamlit dashboard"
  value       = aws_ecs_service.app.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for all ECS tasks"
  value       = aws_cloudwatch_log_group.ecs.name
}
