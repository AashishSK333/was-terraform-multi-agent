resource "aws_lambda_function" "ingestion" {
  filename         = "lambda/ingestion.zip"
  function_name    = "data-ingestion-service"
  role            = aws_iam_role.ingestion_lambda.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_lambda_function" "extract" {
  filename         = "lambda/extract.zip"
  function_name    = "data-extract-service"
  role            = aws_iam_role.processing_lambda.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_lambda_function" "chunk" {
  filename         = "lambda/chunk.zip"
  function_name    = "data-chunk-service"
  role            = aws_iam_role.processing_lambda.arn
  handler         = "app.handler"
  runtime         = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }
}

resource "aws_cloudwatch_event_rule" "rag_generation" {
  name        = "rag-generation"
  description = "EventBridge rule for RAG generation"
}