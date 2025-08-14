resource "aws_s3_bucket" "data_store" {
  bucket = "${var.project_name}-extract-data-store"
}

resource "aws_s3_bucket_versioning" "data_store" {
  bucket = aws_s3_bucket.data_store.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_store" {
  bucket = aws_s3_bucket.data_store.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_dynamodb_table" "data_chunks" {
  name           = "${var.project_name}-data-chunk-db"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"
  
  attribute {
    name = "id"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  point_in_time_recovery {
    enabled = true
  }
}