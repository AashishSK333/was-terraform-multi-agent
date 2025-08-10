resource "aws_sqs_queue" "new_ingestion" {
  name = "${var.project_name}-new-ingestion-sqs"
}

resource "aws_sqs_queue" "new_chunk" {
  name = "${var.project_name}-new-chunk-sqs"
}