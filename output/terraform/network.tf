resource "aws_vpc" "rag_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "rag-vpc"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.rag_vpc.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "rag-private-subnet"
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.rag_vpc.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [aws_route_table.private.id]

  tags = {
    Name = "vpc-s3-gw-endpoint"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.rag_vpc.id
  service_name      = "com.amazonaws.${var.aws_region}.dynamodb"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [aws_route_table.private.id]

  tags = {
    Name = "vpc-dynamodb-gw-endpoint"
  }
}

resource "aws_vpc_endpoint" "sqs" {
  vpc_id             = aws_vpc.rag_vpc.id
  service_name       = "com.amazonaws.${var.aws_region}.sqs"
  vpc_endpoint_type  = "Interface"
  subnet_ids         = [aws_subnet.private.id]
  security_group_ids = [aws_security_group.endpoint.id]

  private_dns_enabled = true

  tags = {
    Name = "vpc-sqs-endpoint"
  }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.rag_vpc.id

  tags = {
    Name = "rag-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}