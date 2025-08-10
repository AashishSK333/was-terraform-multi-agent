resource "aws_s3_bucket" "data_store" {
  bucket = "extract-data-store"
}

resource "aws_s3_bucket_versioning" "data_store" {
  bucket = aws_s3_bucket.data_store.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "chunks" {
  name             = "data-chunk-db"
  billing_mode     = "PAY_PER_REQUEST"
  hash_key         = "id"
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }
}