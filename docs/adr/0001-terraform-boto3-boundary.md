# ADR 0001: Terraform and Boto3 boundary

Decision: Terraform owns persistent infrastructure; Boto3 owns ephemeral burst workers. This prevents two independent state machines from trying to own the same runtime instance set.
