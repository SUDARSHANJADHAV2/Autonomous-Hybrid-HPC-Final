from __future__ import annotations

import boto3


class AWSCloud:
    def __init__(self, region: str = "us-east-1", dry_run: bool = True, session=None):
        self.region = region
        self.dry_run = dry_run
        self.session = session or (boto3.Session(region_name=region) if not dry_run else None)
        self.ec2 = None if dry_run else self.session.client("ec2")

    def launch(self, ami_id, instance_type, subnet_id, security_group_id, key_name, tags):
        if self.dry_run:
            return {"dry_run": True, "instance_id": "i-DRYRUN", "tags": tags}
        if not ami_id or ami_id == "ami-CHANGE-ME":
            raise ValueError("A real AMI ID is required when dry_run is false")
        if not subnet_id or subnet_id == "subnet-CHANGE-ME":
            raise ValueError("A real subnet ID is required when dry_run is false")
        if not security_group_id or security_group_id == "sg-CHANGE-ME":
            raise ValueError("A real security group ID is required when dry_run is false")
        if not key_name or key_name == "CHANGE-ME":
            raise ValueError("An EC2 key name is required when dry_run is false")
        response = self.ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            SubnetId=subnet_id,
            SecurityGroupIds=[security_group_id],
            KeyName=key_name,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": str(k), "Value": str(v)} for k, v in tags.items()],
                }
            ],
        )
        return {
            "dry_run": False,
            "instance_id": response["Instances"][0]["InstanceId"],
            "tags": tags,
        }

    def wait_running(self, instance_id: str, timeout: int = 300) -> dict[str, object]:
        if self.dry_run:
            return {"dry_run": True, "instance_id": instance_id, "state": "running"}
        waiter = self.ec2.get_waiter("instance_running")
        waiter.config.max_attempts = max(1, timeout // 15)
        waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 15, "MaxAttempts": waiter.config.max_attempts})
        info = self.describe(instance_id)
        return info

    def describe(self, instance_id: str) -> dict[str, object]:
        if self.dry_run:
            return {"instance_id": instance_id, "state": "running", "private_ip": "127.0.0.1"}
        reservations = self.ec2.describe_instances(InstanceIds=[instance_id])["Reservations"]
        instances = [item for reservation in reservations for item in reservation["Instances"]]
        if not instances:
            raise RuntimeError(f"EC2 instance not found: {instance_id}")
        item = instances[0]
        return {
            "instance_id": item["InstanceId"],
            "state": item.get("State", {}).get("Name"),
            "private_ip": item.get("PrivateIpAddress"),
            "public_ip": item.get("PublicIpAddress"),
        }

    def terminate(self, instance_id):
        if self.dry_run:
            return {"dry_run": True, "instance_id": instance_id, "state": "terminated"}
        self.ec2.terminate_instances(InstanceIds=[instance_id])
        waiter = self.ec2.get_waiter("instance_terminated")
        waiter.wait(InstanceIds=[instance_id], WaiterConfig={"Delay": 5, "MaxAttempts": 60})
        return {"dry_run": False, "instance_id": instance_id, "state": "terminated"}
