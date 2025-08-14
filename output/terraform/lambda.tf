resource "aws_lambda_function" "data_ingestion" {
  filename         = "lambda_functions/data_ingestion.zip"
  function_name    = "${var.project_name}-data-ingestion-service"
  role            = aws_iam_role.lambda_ingestion.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.vpc_endpoints.id]
  }
}

resource "aws_lambda_function" "data_extract" {
  filename         = "lambda_functions/data_extract.zip"
  function_name    = "${var.project_name}-data-extract-service"
  role            = aws_iam_role.lambda_processing.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.vpc_endpoints.id]
  }
}

resource "aws_lambda_function" "data_chunk" {
  filename         = "lambda_functions/data_chunk.zip"
  function_name    = "${var.project_name}-data-chunk-service"
  role            = aws_iam_role.lambda_processing.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.vpc_endpoints.id]
  }
}

resource "aws_lambda_event_source_mapping" "ingestion_queue" {
  event_source_arn = aws_sqs_queue.new_ingestion.arn
  function_name    = aws_lambda_function.data_extract.arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "chunk_queue" {
  event_source_arn = aws_sqs_queue.new_chunk.arn
  function_name    = aws_lambda_function.data_chunk.arn
  batch_size       = 1
}

resource "aws_cloudwatch_event_target" "ingestion_trigger" {
  rule      = aws_cloudwatch_event_rule.ingestion_trigger.name
  target_id = "LambdaIngestion"
  arn       = aws_lambda_function.data_ingestion.arn
  event_bus_name = aws_cloudwatch_event_bus.main.name
}

resource "aws_cloudwatch_event_rule" "ingestion_trigger" {
  name           = "${var.project_name}-ingestion-trigger"
  event_bus_name = aws_cloudwatch_event_bus.main.name
  
  event_pattern = jsonencode({
    source = ["rag.generation"]
  })
}