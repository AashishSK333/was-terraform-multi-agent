resource "aws_iam_role" "lambda_ingestion_role" {
  name = "${var.project_name}-lambda-ingestion-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_ingestion_policy" {
  name = "${var.project_name}-lambda-ingestion-policy"
  role = aws_iam_role.lambda_ingestion_role.id

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
          aws_sqs_queue.new_ingestion.arn
        ]
      }
    ]
  })
}

resource "aws_iam_role" "lambda_processing_role" {
  name = "${var.project_name}-lambda-processing-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_processing_policy" {
  name = "${var.project_name}-lambda-processing-policy"
  role = aws_iam_role.lambda_processing_role.id

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
          "s3:DeleteObject",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage"
        ]
        Resource = [
          aws_dynamodb_table.data_chunk_db.arn,
          "${aws_s3_bucket.extract_data_store.arn}/*",
          aws_sqs_queue.new_ingestion.arn,
          aws_sqs_queue.new_chunk.arn
        ]
      }
    ]
  })
}