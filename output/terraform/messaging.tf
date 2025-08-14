resource "aws_cloudwatch_event_bus" "main" {
  name = "${var.project_name}-generation"
}

resource "aws_sqs_queue" "new_ingestion" {
  name = "${var.project_name}-new-ingestion"

  visibility_timeout_seconds = 300
  message_retention_seconds = 86400
  
  sqs_managed_sse_enabled = true
}

resource "aws_sqs_queue" "new_chunk" {
  name = "${var.project_name}-new-chunk"

  visibility_timeout_seconds = 300
  message_retention_seconds = 86400
  
  sqs_managed_sse_enabled = true
}