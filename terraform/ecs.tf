# ─────────────────────────────────────────────────────────────────────────────
# ecs.tf  — ECS Fargate cluster, task definitions, service
# ─────────────────────────────────────────────────────────────────────────────

# ── Cluster ──────────────────────────────────────────────────────────────────
resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# ── CloudWatch log group ──────────────────────────────────────────────────────
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${var.project}-${var.environment}"
  retention_in_days = 30
}

# ── Streamlit app task definition ─────────────────────────────────────────────
resource "aws_ecs_task_definition" "app" {
  family                   = "${var.project}-app-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_exec.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "${aws_ecr_repository.app.repository_url}:${var.app_image_tag}"
      essential = true

      portMappings = [{ containerPort = 8501, protocol = "tcp" }]

      environment = [
        { name = "DATA_BUCKET", value = aws_s3_bucket.data_lake.id },
        { name = "AWS_REGION",  value = var.aws_region }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "app"
        }
      }

      # Minimal health check — Streamlit _stcore/health endpoint
      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8501/_stcore/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])
}

# ── Pipeline task definition (one-shot, triggered by Kestra) ─────────────────
resource "aws_ecs_task_definition" "pipeline" {
  family                   = "${var.project}-pipeline-${var.environment}"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ecs_cpu
  memory                   = var.ecs_memory
  execution_role_arn       = aws_iam_role.ecs_exec.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "pipeline"
      image     = "${aws_ecr_repository.app.repository_url}:${var.app_image_tag}"
      essential = true
      command   = ["sh", "-c",
        "python src/collect.py && python src/harmonize.py && python src/impute.py && python src/features.py && python src/target.py && python src/tune.py && python src/train.py && python src/explain.py && python src/forecast.py"
      ]
      environment = [
        { name = "DATA_BUCKET", value = aws_s3_bucket.data_lake.id },
        { name = "AWS_REGION",  value = var.aws_region }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "pipeline"
        }
      }
    }
  ])
}

# ── Streamlit app service (long-running) ─────────────────────────────────────
# NOTE: requires a VPC + subnets — update subnet_ids / security_group_ids
# before applying to a real AWS account.
resource "aws_ecs_service" "app" {
  name            = "${var.project}-app-${var.environment}"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.app_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = []   # TODO: set to your subnet IDs, e.g. ["subnet-abc123"]
    security_groups  = []   # TODO: set to a SG that allows inbound 8501
    assign_public_ip = true
  }

  lifecycle {
    ignore_changes = [task_definition]   # let CI/CD update the image tag
  }
}
