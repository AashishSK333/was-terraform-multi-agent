resource "aws_security_group" "vpc_endpoints" {
  name_prefix = "${var.project_name}-vpc-endpoints-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${var.project_name}-vpc-endpoints-sg"
  }
}

resource "aws_iam_role" "lambda_ingestion" {
  name = "${var.project_name}-lambda-ingestion"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role" "lambda_processing" {
  name = "${var.project_name}-lambda-processing"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy" "lambda_ingestion" {
  name = "${var.project_name}-lambda-ingestion-policy"
  role = aws_iam_role.lambda_ingestion.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:DeleteMessage",
          "events:PutEvents"
        ]
        Resource = [
          aws_sqs_queue.new_ingestion.arn,
          aws_cloudwatch_event_bus.main.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_processing" {
  name = "${var.project_name}-lambda-processing-policy"
  role = aws_iam_role.lambda_processing.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "s3:GetObject",
          "s3:PutObject",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:SendMessage"
        ]
        Resource = [
          aws_dynamodb_table.data_chunks.arn,
          "${aws_s3_bucket.data_store.arn}/*",
          aws_sqs_queue.new_ingestion.arn,
          aws_sqs_queue.new_chunk.arn
        ]
      }
    ]
  })
}