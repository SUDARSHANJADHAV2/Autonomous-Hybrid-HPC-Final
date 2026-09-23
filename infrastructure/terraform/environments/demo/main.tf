terraform {
  required_version = ">= 1.6, < 2.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.62" }
  }
}

provider "aws" { region = var.aws_region }

resource "aws_vpc" "hpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "hpc-vpc", ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.hpc.id
  tags = { Name = "hpc-igw", ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.hpc.id
  cidr_block              = var.public_cidr
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"
  tags = { Name = "hpc-public", ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_subnet" "private" {
  vpc_id            = aws_vpc.hpc.id
  cidr_block        = var.private_cidr
  availability_zone = "${var.aws_region}a"
  tags = { Name = "hpc-private", ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.hpc.id
  route { cidr_block = "0.0.0.0/0" gateway_id = aws_internet_gateway.igw.id }
  tags = { Name = "hpc-public-rt" }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

resource "aws_eip" "nat" {
  domain = "vpc"
  tags = { Name = "hpc-nat-eip" }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public.id
  depends_on    = [aws_internet_gateway.igw]
  tags = { Name = "hpc-nat" }
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.hpc.id
  route { cidr_block = "0.0.0.0/0" nat_gateway_id = aws_nat_gateway.nat.id }
  tags = { Name = "hpc-private-rt" }
}

resource "aws_route_table_association" "private" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}

resource "aws_security_group" "bastion" {
  name   = "hpc-bastion"
  vpc_id = aws_vpc.hpc.id
  dynamic "ingress" {
    for_each = var.admin_cidrs
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "hpc-bastion-sg" }
}

resource "aws_security_group" "private" {
  name   = "hpc-private"
  vpc_id = aws_vpc.hpc.id
  ingress {
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.bastion.id]
  }
  ingress {
    from_port = 6817
    to_port   = 6818
    protocol  = "tcp"
    self      = true
  }
  ingress {
    from_port = 6819
    to_port   = 6819
    protocol  = "tcp"
    self      = true
  }
  ingress {
    from_port       = 9090
    to_port         = 9090
    protocol        = "tcp"
    cidr_blocks     = var.monitoring_cidrs
  }
  egress { from_port = 0 to_port = 0 protocol = "-1" cidr_blocks = ["0.0.0.0/0"] }
  tags = { Name = "hpc-private-sg" }
}

resource "aws_key_pair" "admin" {
  count      = var.create_bastion || var.create_controller ? 1 : 0
  key_name   = var.ssh_key_name
  public_key = var.ssh_public_key
  tags = { ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_instance" "bastion" {
  count                  = var.create_bastion ? 1 : 0
  ami                    = var.bastion_ami_id
  instance_type          = var.bastion_instance_type
  subnet_id              = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.bastion.id]
  key_name               = aws_key_pair.admin[0].key_name
  tags = { Name = "hpc-bastion", Role = "bastion", ManagedBy = "autonomous-hybrid-hpc" }
}

resource "aws_instance" "controller" {
  count                  = var.create_controller ? 1 : 0
  ami                    = var.controller_ami_id
  instance_type          = var.controller_instance_type
  subnet_id              = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.private.id]
  key_name               = aws_key_pair.admin[0].key_name
  tags = { Name = "hpc-controller", Role = "controller", ManagedBy = "autonomous-hybrid-hpc" }
}
