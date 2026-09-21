output "vpc_id" { value = aws_vpc.hpc.id }
output "public_subnet_id" { value = aws_subnet.public.id }
output "private_subnet_id" { value = aws_subnet.private.id }
output "private_security_group_id" { value = aws_security_group.private.id }
output "bastion_public_ip" { value = var.create_bastion ? aws_instance.bastion[0].public_ip : null }
output "controller_private_ip" { value = var.create_controller ? aws_instance.controller[0].private_ip : null }
