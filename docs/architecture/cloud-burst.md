# Cloud burst lifecycle

Cloud workers progress through:

`REQUESTED -> PROVISIONING -> BOOTING -> NETWORK_READY -> CONFIGURING -> SLURM_REGISTERING -> AVAILABLE -> BUSY/IDLE -> DRAINING -> TERMINATING -> TERMINATED`

Terraform owns the VPC, subnets, routes, NAT, bastion and any intentionally persistent hosts. The runtime manager uses Boto3 to launch and terminate ephemeral workers so Terraform state does not fight autoscaling. A worker is not considered available until connectivity, configuration, Slurm registration and verification succeed.

Scale-down must first stop new placement, drain the worker, wait for running work to finish or apply a documented force policy, verify Slurm state, then terminate the EC2 instance and record the final cloud state.
