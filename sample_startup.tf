# Kijiji-Guard: Reference Architecture for Nigerian Startups
# This architecture is designed for NDPA 2023 compliance.

provider "aws" {
  region = "af-south-1" # Cape Town (Adequate Protection Zone)
}

# VPC for secure workload isolation
resource "aws_vpc" "unicorn_vpc" {
  cidr_block = "10.0.0.0/16"
  tags = {
    Name = "Unicorn-VPC"
    Region = "af-south-1"
  }
}

resource "aws_subnet" "private_subnet" {
  vpc_id     = aws_vpc.unicorn_vpc.id
  cidr_block = "10.0.1.0/24"
  tags = {
    Name = "Private-Subnet"
    Region = "af-south-1"
  }
}

# S3 Bucket for User KYC Data (Sensitive PII)
# INTENTIONAL FAILURE: Missing lifecycle_rule (CKV_NGR_002)
# INTENTIONAL FAILURE: Missing encryption (CKV_NGR_003)
resource "aws_s3_bucket" "kyc_data" {
  bucket = "unicorn-kyc-data-nigeria"
  
  # Encryption is NOT enabled here (CKV_NGR_003)
  # Lifecycle is NOT enabled here (CKV_NGR_002)

  tags = {
    Name = "KYC-Data"
    Region = "af-south-1" # Passing CKV_NGR_001
  }
}

# RDS Instance for Transaction Data
resource "aws_db_instance" "transaction_db" {
  allocated_storage    = 20
  storage_type         = "gp2"
  engine               = "postgres"
  engine_version       = "13.7"
  instance_class       = "db.t3.micro"
  name                 = "transactions"
  username             = "admin"
  password             = var.db_password
  parameter_group_name = "default.postgres13"
  skip_final_snapshot  = true
  
  # Encryption enabled (CKV_NGR_003)
  storage_encrypted = true

  tags = {
    Name = "Transaction-DB"
    Region = "af-south-1" # Passing CKV_NGR_001
  }
}

variable "db_password" {
  description = "RDS master password — supply via TF_VAR_db_password env var"
  type        = string
  sensitive   = true
}
