"""
Session 30 - AWS EC2 And S3 Testing For Allure TestOps With Allure 3

Runnable examples for planning and validating a cloud deployment test strategy.
The demo prints commands and checks only; it does not create AWS resources.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from course.framework.cloud import (  # noqa: E402
    AllureTestOpsDeploymentPlan,
    EC2InstancePlan,
    S3BucketPlan,
    build_allure3_generate_command,
    build_aws_s3_bucket_commands,
    build_testops_compose_commands,
    create_reference_deployment_plan,
    render_deployment_smoke_checklist,
    validate_deployment_plan,
)


def demo() -> None:
    plan = create_reference_deployment_plan()

    print("Allure TestOps domain:", plan.domain)
    print("EC2 instance:", plan.ec2.name, plan.ec2.instance_type, plan.ec2.region)
    print("Artifacts bucket:", plan.artifacts_bucket.name)
    print("Backups bucket:", plan.backups_bucket.name)
    print()

    print("S3 baseline commands:")
    for command in build_aws_s3_bucket_commands(plan.artifacts_bucket):
        print("-", command)
    print()

    print("Allure 3 report command:")
    print(build_allure3_generate_command())
    print()

    print("EC2 TestOps Compose commands:")
    for command in build_testops_compose_commands(plan):
        print("-", command)
    print()

    print("Smoke checklist:")
    for item in render_deployment_smoke_checklist(plan):
        print("-", item)
    print()

    print("Validation errors:", validate_deployment_plan(plan))


if __name__ == "__main__":
    demo()


__all__ = [
    "AllureTestOpsDeploymentPlan",
    "EC2InstancePlan",
    "S3BucketPlan",
    "build_allure3_generate_command",
    "build_aws_s3_bucket_commands",
    "build_testops_compose_commands",
    "create_reference_deployment_plan",
    "render_deployment_smoke_checklist",
    "validate_deployment_plan",
]
