resource "aws_sqs_queue" "ingestion" {
  name                       = "new-ingestion-sqs"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.ingestion_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "ingestion_dlq" {
  name = "new-ingestion-sqs-dlq"
}

resource "aws_sqs_queue" "chunk" {
  name                       = "new-chunk-sqs"
  visibility_timeout_seconds = 300
  message_retention_seconds  = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.chunk_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "chunk_dlq" {
  name = "new-chunk-sqs-dlq"
}

resource "aws_cloudwatch_event_bus" "rag" {
  name = "rag-generation"
}