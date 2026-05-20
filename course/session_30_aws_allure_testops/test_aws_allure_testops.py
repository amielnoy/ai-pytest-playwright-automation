from __future__ import annotations

from course.framework.cloud import (
    AllureTestOpsDeploymentPlan,
    EC2InstancePlan,
    S3BucketPlan,
    build_allure3_generate_command,
    build_aws_s3_bucket_commands,
    build_testops_compose_commands,
    create_reference_deployment_plan,
    render_deployment_smoke_checklist,
    validate_deployment_plan,
    validate_ec2_instance,
    validate_s3_bucket,
)


def test_reference_deployment_plan_is_valid() -> None:
    plan = create_reference_deployment_plan()

    assert validate_deployment_plan(plan) == []


def test_s3_bucket_validation_rejects_public_unencrypted_short_retention_bucket() -> None:
    bucket = S3BucketPlan(
        name="bad-bucket",
        region="eu-west-1",
        versioning_enabled=False,
        encryption="NONE",
        public_access_blocked=False,
        lifecycle_days=7,
    )

    errors = validate_s3_bucket(bucket)

    assert "S3 bucket bad-bucket must block public access" in errors
    assert "S3 bucket bad-bucket must use SSE-S3 or SSE-KMS encryption" in errors
    assert "S3 bucket bad-bucket must enable versioning for report and backup recovery" in errors
    assert "S3 bucket bad-bucket lifecycle must retain artifacts for at least 30 days" in errors


def test_ec2_validation_requires_iam_role_disk_and_https() -> None:
    instance = EC2InstancePlan(
        name="small-testops-host",
        region="eu-west-1",
        volume_gb=40,
        security_group_ports=(22,),
        uses_iam_role=False,
    )

    errors = validate_ec2_instance(instance)

    assert "EC2 instance small-testops-host should allocate at least 80 GB for TestOps data and logs" in errors
    assert "EC2 instance small-testops-host must use an IAM role instead of stored AWS keys" in errors
    assert "EC2 instance small-testops-host must expose HTTPS on port 443" in errors


def test_deployment_validation_requires_https_allure3_and_matching_regions() -> None:
    plan = AllureTestOpsDeploymentPlan(
        domain="http://testops.example.com",
        ec2=EC2InstancePlan(name="qa-testops-ec2", region="eu-west-1"),
        artifacts_bucket=S3BucketPlan(name="artifacts", region="us-east-1"),
        backups_bucket=S3BucketPlan(name="backups", region="eu-west-1"),
        uses_allure3=False,
    )

    errors = validate_deployment_plan(plan)

    assert "Allure TestOps domain must use HTTPS" in errors
    assert "Deployment plan must keep Allure 3 report generation in the test evidence flow" in errors
    assert "EC2 instance and artifacts bucket should be in the same region" in errors


def test_deployment_validation_requires_reporting_prefixes() -> None:
    plan = AllureTestOpsDeploymentPlan(
        domain="https://testops.example.com",
        ec2=EC2InstancePlan(name="qa-testops-ec2", region="eu-west-1"),
        artifacts_bucket=S3BucketPlan(name="artifacts", region="eu-west-1"),
        backups_bucket=S3BucketPlan(name="backups", region="eu-west-1"),
        result_prefix="raw-results/",
    )

    errors = validate_deployment_plan(plan)

    assert "Missing required S3 prefix: allure-results/" in errors


def test_s3_bucket_commands_include_security_baseline() -> None:
    bucket = S3BucketPlan(name="qa-testops-artifacts-example", region="eu-west-1")

    commands = build_aws_s3_bucket_commands(bucket)

    assert any("put-public-access-block" in command for command in commands)
    assert any("put-bucket-encryption" in command for command in commands)
    assert any("put-bucket-versioning" in command for command in commands)


def test_allure3_generate_command_writes_clean_report() -> None:
    command = build_allure3_generate_command("docker-artifacts/allure-results", "docker-artifacts/allure-report")

    assert command == (
        "npx allure generate docker-artifacts/allure-results --clean -o docker-artifacts/allure-report"
    )


def test_testops_compose_commands_cover_deploy_and_logs() -> None:
    commands = build_testops_compose_commands(create_reference_deployment_plan())

    assert commands == (
        "cd ~/testops",
        "docker compose pull",
        "docker compose up -d",
        "docker compose ps",
        "docker compose logs testops --tail=200",
    )


def test_smoke_checklist_covers_https_s3_allure3_testops_and_backup() -> None:
    checklist = render_deployment_smoke_checklist(create_reference_deployment_plan())
    joined = "\n".join(checklist)

    assert "HTTPS" in joined
    assert "allure-results/" in joined
    assert "Allure 3" in joined
    assert "TestOps launch" in joined
    assert "testops-backups/" in joined
