# Deployment Sketch: Uptime Monitor MVP Infrastructure (AWS Topology)
# Illustrative Terraform definition mapping ECS Fargate, CloudFront, S3, and EFS.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

# ------------------------------------------------------------------------------
# 1. FRONTEND: S3 + CloudFront Static Web Hosting
# ------------------------------------------------------------------------------
resource "aws_s3_bucket" "frontend_bucket" {
  bucket        = "pulseguard-uptime-frontend-mvp"
  force_destroy = true
}

resource "aws_cloudfront_origin_access_control" "oac" {
  name                              = "pulseguard-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "frontend_cdn" {
  enabled             = true
  default_root_object = "index.html"

  origin {
    domain_name              = aws_s3_bucket.frontend_bucket.bucket_regional_domain_name
    origin_id                = "S3-Frontend"
    origin_access_control_id = aws_cloudfront_origin_access_control.oac.id
  }

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "S3-Frontend"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }
}

# ------------------------------------------------------------------------------
# 2. BACKEND: ECS Fargate Service + Application Load Balancer
# ------------------------------------------------------------------------------
resource "aws_ecs_cluster" "main" {
  name = "pulseguard-cluster"
}

# EFS Mount for SQLite Data Persistence (MVP scale)
resource "aws_efs_file_system" "sqlite_storage" {
  creation_token   = "pulseguard-sqlite-efs"
  performance_mode = "generalPurpose"
  encrypted        = true

  tags = {
    Name = "pulseguard-sqlite-efs"
  }
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "pulseguard-backend-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name      = "uptime-backend"
      image     = "123456789012.dkr.ecr.us-east-1.amazonaws.com/uptime-backend:latest"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "DATABASE_URL", value = "sqlite:////mnt/efs/monitor.db" },
        { name = "CHECK_INTERVAL_SECONDS", value = "60" }
      ]
      mountPoints = [
        {
          sourceVolume  = "sqlite-volume"
          containerPath = "/mnt/efs"
        }
      ]
    }
  ])

  volume {
    name = "sqlite-volume"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.sqlite_storage.id
      root_directory = "/"
    }
  }
}

resource "aws_ecs_service" "backend_service" {
  name            = "pulseguard-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = ["subnet-12345678", "subnet-87654321"]
    assign_public_ip = true
  }
}
