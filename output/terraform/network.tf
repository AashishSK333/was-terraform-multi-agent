resource "aws_vpc" "rag_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.rag_vpc.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-private-subnet"
  }
}

resource "aws_vpc_endpoint" "s3" {
  vpc_id       = aws_vpc.rag_vpc.id
  service_name = "com.amazonaws.${var.aws_region}.s3"
  
  tags = {
    Name = "vpc-s3-gw-endpoint"
  }
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id       = aws_vpc.rag_vpc.id
  service_name = "com.amazonaws.${var.aws_region}.dynamodb"
  
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

resource "aws_security_group" "endpoint" {
  name        = "sg-endpoint"
  description = "Security group for VPC endpoints"
  vpc_id      = aws_vpc.rag_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
}