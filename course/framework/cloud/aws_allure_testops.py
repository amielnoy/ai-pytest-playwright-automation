"""AWS EC2 and S3 testing contracts for Allure TestOps deployments.

The helpers in this module intentionally do not call AWS, Docker, or Allure.
They model the checks students should automate around a real deployment plan
before they run infrastructure smoke tests against paid cloud resources.
"""

from __future__ import annotations

from dataclasses import dataclass
from shlex import quote


ALLOWED_S3_ENCRYPTION = {"SSE-S3", "SSE-KMS"}
REQUIRED_S3_PREFIXES = ("allure-results/", "allure-reports/", "testops-backups/")


@dataclass(frozen=True)
class S3BucketPlan:
    """Security and lifecycle contract for a bucket used by test reporting."""

    name: str
    region: str
    versioning_enabled: bool = True
    encryption: str = "SSE-S3"
    public_access_blocked: bool = True
    lifecycle_days: int = 90


@dataclass(frozen=True)
class EC2InstancePlan:
    """Deployment host contract for an Allure TestOps Docker Compose server."""

    name: str
    region: str
    instance_type: str = "t3.large"
    volume_gb: int = 100
    security_group_ports: tuple[int, ...] = (22, 80, 443)
    uses_iam_role: bool = True
    requires_https: bool = True


@dataclass(frozen=True)
class AllureTestOpsDeploymentPlan:
    """End-to-end contract for TestOps on EC2 with S3-backed artifacts."""

    domain: str
    ec2: EC2InstancePlan
    artifacts_bucket: S3BucketPlan
    backups_bucket: S3BucketPlan
    testops_version: str = "latest-supported"
    uses_allure3: bool = True
    compose_directory: str = "~/testops"
    result_prefix: str = "allure-results/"
    report_prefix: str = "allure-reports/"
    backup_prefix: str = "testops-backups/"


def build_aws_s3_bucket_commands(bucket: S3BucketPlan) -> tuple[str, ...]:
    """Return AWS CLI commands that create the bucket security baseline."""

    commands = [
        (
            "aws s3api create-bucket "
            f"--bucket {quote(bucket.name)} "
            f"--region {quote(bucket.region)} "
            "--create-bucket-configuration "
            f"LocationConstraint={quote(bucket.region)}"
        ),
        (
            "aws s3api put-public-access-block "
            f"--bucket {quote(bucket.name)} "
            "--public-access-block-configuration "
            "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
        ),
        (
            "aws s3api put-bucket-encryption "
            f"--bucket {quote(bucket.name)} "
            "--server-side-encryption-configuration "
            f"Rules=[{{ApplyServerSideEncryptionByDefault={{SSEAlgorithm={_s3_encryption_algorithm(bucket)}}}}}]"
        ),
        (
            "aws s3api put-bucket-versioning "
            f"--bucket {quote(bucket.name)} "
            "--versioning-configuration Status=Enabled"
        ),
    ]
    return tuple(commands)


def build_allure3_generate_command(
    results_dir: str = "allure-results",
    report_dir: str = "allure-report",
) -> str:
    """Return the local Allure 3 report generation command for CI artifacts."""

    return " ".join(("npx", "allure", "generate", quote(results_dir), "--clean", "-o", quote(report_dir)))


def build_testops_compose_commands(plan: AllureTestOpsDeploymentPlan) -> tuple[str, ...]:
    """Return the high-level deployment and verification commands for EC2."""

    compose_dir = plan.compose_directory
    return (
        f"cd {compose_dir}",
        "docker compose pull",
        "docker compose up -d",
        "docker compose ps",
        "docker compose logs testops --tail=200",
    )


def create_reference_deployment_plan() -> AllureTestOpsDeploymentPlan:
    """Create a safe reference plan for the course examples."""

    region = "eu-west-1"
    return AllureTestOpsDeploymentPlan(
        domain="https://testops.example.com",
        ec2=EC2InstancePlan(name="qa-testops-ec2", region=region),
        artifacts_bucket=S3BucketPlan(name="qa-testops-artifacts-example", region=region),
        backups_bucket=S3BucketPlan(
            name="qa-testops-backups-example",
            region=region,
            encryption="SSE-KMS",
            lifecycle_days=180,
        ),
    )


def render_deployment_smoke_checklist(plan: AllureTestOpsDeploymentPlan) -> tuple[str, ...]:
    """Return deployment checks students can convert into manual or automated tests."""

    return (
        f"Resolve {plan.domain} over HTTPS",
        "Confirm EC2 has an IAM role and no long-lived AWS keys in .env",
        f"Upload a small object to s3://{plan.artifacts_bucket.name}/{plan.result_prefix}",
        "Run pytest with --alluredir and generate an Allure 3 report",
        "Create or import one TestOps launch from the generated results",
        f"Write and restore one backup object under s3://{plan.backups_bucket.name}/{plan.backup_prefix}",
        "Capture docker compose ps and TestOps service logs after deployment",
    )


def validate_s3_bucket(bucket: S3BucketPlan) -> list[str]:
    """Return validation errors for an S3 bucket reporting contract."""

    errors: list[str] = []
    if not bucket.name:
        errors.append("S3 bucket name is required")
    if not bucket.region:
        errors.append(f"S3 bucket {bucket.name or '<unknown>'} region is required")
    if not bucket.public_access_blocked:
        errors.append(f"S3 bucket {bucket.name} must block public access")
    if bucket.encryption not in ALLOWED_S3_ENCRYPTION:
        errors.append(f"S3 bucket {bucket.name} must use SSE-S3 or SSE-KMS encryption")
    if not bucket.versioning_enabled:
        errors.append(f"S3 bucket {bucket.name} must enable versioning for report and backup recovery")
    if bucket.lifecycle_days < 30:
        errors.append(f"S3 bucket {bucket.name} lifecycle must retain artifacts for at least 30 days")
    return errors


def validate_ec2_instance(instance: EC2InstancePlan) -> list[str]:
    """Return validation errors for an EC2 TestOps host contract."""

    errors: list[str] = []
    if not instance.name:
        errors.append("EC2 instance name is required")
    if not instance.region:
        errors.append(f"EC2 instance {instance.name or '<unknown>'} region is required")
    if instance.volume_gb < 80:
        errors.append(f"EC2 instance {instance.name} should allocate at least 80 GB for TestOps data and logs")
    if not instance.uses_iam_role:
        errors.append(f"EC2 instance {instance.name} must use an IAM role instead of stored AWS keys")
    if instance.requires_https and 443 not in instance.security_group_ports:
        errors.append(f"EC2 instance {instance.name} must expose HTTPS on port 443")
    if 22 in instance.security_group_ports and 443 not in instance.security_group_ports:
        errors.append(f"EC2 instance {instance.name} exposes SSH but not HTTPS")
    return errors


def validate_deployment_plan(plan: AllureTestOpsDeploymentPlan) -> list[str]:
    """Return validation errors for the full EC2, S3, TestOps, and Allure 3 plan."""

    errors: list[str] = []
    errors.extend(validate_ec2_instance(plan.ec2))
    errors.extend(validate_s3_bucket(plan.artifacts_bucket))
    errors.extend(validate_s3_bucket(plan.backups_bucket))

    if not plan.domain.startswith("https://"):
        errors.append("Allure TestOps domain must use HTTPS")
    if not plan.uses_allure3:
        errors.append("Deployment plan must keep Allure 3 report generation in the test evidence flow")
    if plan.ec2.region != plan.artifacts_bucket.region:
        errors.append("EC2 instance and artifacts bucket should be in the same region")
    if plan.ec2.region != plan.backups_bucket.region:
        errors.append("EC2 instance and backups bucket should be in the same region")

    prefixes = (plan.result_prefix, plan.report_prefix, plan.backup_prefix)
    for prefix in REQUIRED_S3_PREFIXES:
        if prefix not in prefixes:
            errors.append(f"Missing required S3 prefix: {prefix}")
    return errors


def _s3_encryption_algorithm(bucket: S3BucketPlan) -> str:
    if bucket.encryption == "SSE-KMS":
        return "aws:kms"
    return "AES256"
