resource "aws_s3_bucket" "extract_data_store" {
  bucket = "${var.project_name}-extract-data-store"
}

resource "aws_s3_bucket_versioning" "extract_data_store" {
  bucket = aws_s3_bucket.extract_data_store.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "data_chunk_db" {
  name           = "${var.project_name}-data-chunk-db"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Name = "data-chunk-db"
  }
}