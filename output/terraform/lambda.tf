resource "aws_lambda_function" "data_ingestion_service" {
  filename         = "lambda/data_ingestion_service.zip"
  function_name    = "${var.project_name}-data-ingestion-service"
  role            = aws_iam_role.lambda_ingestion_role.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.endpoint.id]
  }
}

resource "aws_lambda_function" "data_extract_service" {
  filename         = "lambda/data_extract_service.zip"
  function_name    = "${var.project_name}-data-extract-service"
  role            = aws_iam_role.lambda_processing_role.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.endpoint.id]
  }
}

resource "aws_lambda_function" "data_chunk_service" {
  filename         = "lambda/data_chunk_service.zip"
  function_name    = "${var.project_name}-data-chunk-service"
  role            = aws_iam_role.lambda_processing_role.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.endpoint.id]
  }
}

resource "aws_lambda_event_source_mapping" "extract_service_trigger" {
  event_source_arn = aws_sqs_queue.new_ingestion.arn
  function_name    = aws_lambda_function.data_extract_service.arn
}

resource "aws_lambda_event_source_mapping" "chunk_service_trigger" {
  event_source_arn = aws_sqs_queue.new_chunk.arn
  function_name    = aws_lambda_function.data_chunk_service.arn
}