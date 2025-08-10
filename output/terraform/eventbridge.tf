resource "aws_cloudwatch_event_rule" "rag_generation" {
  name                = "${var.project_name}-generation-rule"
  description         = "Trigger RAG generation pipeline"
  schedule_expression = "rate(1 day)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.rag_generation.name
  target_id = "TriggerLambda"
  arn       = aws_lambda_function.data_ingestion_service.arn
}