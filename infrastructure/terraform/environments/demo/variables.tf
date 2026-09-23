variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.40.0.0/16"
}

variable "public_cidr" {
  type    = string
  default = "10.40.1.0/24"
}

variable "private_cidr" {
  type    = string
  default = "10.40.10.0/24"
}

variable "admin_cidrs" {
  type    = list(string)
  default = []
}

variable "monitoring_cidrs" {
  type    = list(string)
  default = []
}

variable "ssh_key_name" {
  type    = string
  default = "hpc-admin"
}

variable "ssh_public_key" {
  type    = string
  default = ""
  validation {
    condition     = (!var.create_bastion && !var.create_controller) || length(trimspace(var.ssh_public_key)) > 20
    error_message = "ssh_public_key must be supplied when a bastion or controller instance is created."
  }
}

variable "create_bastion" {
  type    = bool
  default = false
}

variable "create_controller" {
  type    = bool
  default = false
}

variable "bastion_ami_id" {
  type    = string
  default = ""
  validation {
    condition     = !var.create_bastion || length(trimspace(var.bastion_ami_id)) > 0
    error_message = "bastion_ami_id is required when create_bastion=true."
  }
}

variable "controller_ami_id" {
  type    = string
  default = ""
  validation {
    condition     = !var.create_controller || length(trimspace(var.controller_ami_id)) > 0
    error_message = "controller_ami_id is required when create_controller=true."
  }
}

variable "bastion_instance_type" {
  type    = string
  default = "t3.micro"
}

variable "controller_instance_type" {
  type    = string
  default = "t3.large"
}
