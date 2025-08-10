resource "aws_lambda_function" "ingestion" {
  filename      = "lambda_ingestion.zip"
  function_name = "data-ingestion-service"
  role          = aws_iam_role.lambda_ingestion.arn
  handler       = "app.handler"
  runtime       = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      INGESTION_QUEUE_URL = aws_sqs_queue.ingestion.url
    }
  }
}

resource "aws_lambda_function" "extract" {
  filename      = "lambda_extract.zip"
  function_name = "data-extract-service"
  role          = aws_iam_role.lambda_processing.arn
  handler       = "app.handler"
  runtime       = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      CHUNK_QUEUE_URL = aws_sqs_queue.chunk.url
      S3_BUCKET       = aws_s3_bucket.data_store.id
    }
  }
}

resource "aws_lambda_function" "chunk" {
  filename      = "lambda_chunk.zip"
  function_name = "data-chunk-service"
  role          = aws_iam_role.lambda_processing.arn
  handler       = "app.handler"
  runtime       = var.lambda_runtime

  vpc_config {
    subnet_ids         = [aws_subnet.private.id]
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.chunks.id
      S3_BUCKET      = aws_s3_bucket.data_store.id
    }
  }
}

resource "aws_lambda_event_source_mapping" "extract_trigger" {
  event_source_arn = aws_sqs_queue.ingestion.arn
  function_name    = aws_lambda_function.extract.arn
  batch_size       = 1
}

resource "aws_lambda_event_source_mapping" "chunk_trigger" {
  event_source_arn = aws_sqs_queue.chunk.arn
  function_name    = aws_lambda_function.chunk.arn
  batch_size       = 1
}