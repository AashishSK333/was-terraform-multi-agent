output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.rag_vpc.id
}

output "private_subnet_id" {
  description = "The ID of the private subnet"
  value       = aws_subnet.private.id
}

output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.extract_data_store.id
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.data_chunk_db.id
}

output "sqs_new_ingestion_url" {
  description = "The URL of the new ingestion SQS queue"
  value       = aws_sqs_queue.new_ingestion.url
}

output "sqs_new_chunk_url" {
  description = "The URL of the new chunk SQS queue"
  value       = aws_sqs_queue.new_chunk.url
}