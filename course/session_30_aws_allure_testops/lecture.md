# Session 30 - AWS EC2 & S3 Testing For Allure TestOps With Allure 3

> 📚 **Lecture** · [session_30_aws_allure_testops](.) · [Learning path](../README.md)


<!-- cSpell:words TestOps alluredir Playwright server-side pytest -->

## 🎯 Learning Objectives

By the end of this session you will be able to:

- Design a deployment test plan for Allure TestOps on AWS EC2.
- Validate S3 bucket security for Allure results, reports, and backups.
- Validate EC2 host readiness before running Docker Compose services.
- Keep Allure 3 report generation in the test evidence flow.
- Separate infrastructure smoke tests from release gates.
- Define a backup and restore drill for TestOps reporting data.

---

## Scope And Safety

This session teaches deployment testing without creating real AWS resources.
The Python examples build commands, contracts, and validation errors only.

Production deployments must still be checked against the current vendor and
cloud documentation before use. Allure TestOps deployment options, supported
versions, and storage requirements change over time, so treat this lesson as a
testing model rather than a replacement for the official installation guide.

Keep these rules:

- Do not commit AWS credentials, TestOps tokens, license files, or `.env`
  secrets.
- Prefer IAM roles on EC2 instead of long-lived access keys.
- Block public access on reporting buckets.
- Use server-side encryption and versioning on S3.
- Use HTTPS for the TestOps URL.
- Keep the deployment smoke suite small and deterministic.

---

## Reference Architecture

```text
pytest / Playwright
  -> allure-results/
  -> Allure 3 report generation
  -> S3 artifacts bucket
  -> Allure TestOps running on EC2 with Docker Compose
  -> S3 backup bucket for restore drills
```

The production shape may include external PostgreSQL, Redis, RabbitMQ, object
storage, identity provider integration, and stricter network controls. In this
course we focus on the parts QA automation engineers should know how to test:
host readiness, object storage, report generation, launch ingestion, and
evidence retention.

---

## AWS Deployment Test Matrix

| Area | What to test | Example evidence |
|---|---|---|
| EC2 identity | Instance uses an IAM role, not static AWS keys. | Instance profile exists, no AWS keys in `.env`. |
| EC2 network | HTTPS is reachable, SSH is restricted, health checks pass. | Security group review, `curl` health response. |
| EC2 capacity | Disk and memory are large enough for reports and logs. | `df -h`, Docker volume usage, service logs. |
| S3 access | Buckets block public access and allow only required principals. | Public access block and policy checks. |
| S3 durability | Versioning and lifecycle rules match retention policy. | Versioning status and lifecycle config. |
| S3 security | Server-side encryption is enabled. | Bucket encryption config. |
| Allure 3 | Results generate a clean report before upload or import. | `npx allure generate allure-results --clean -o allure-report`. |
| TestOps | A launch can be created or imported from generated results. | TestOps launch URL and service logs. |
| Backup | Backup object can be written and restored in a drill. | Restore notes and checksum. |

---

## Allure 3 And TestOps Flow

Allure 3 report generation is still useful even when TestOps becomes the
central reporting system. The local or CI-generated report is fast evidence for
debugging failed runs, while TestOps keeps launch history, ownership, manual
test alignment, and broader reporting workflows.

Use this flow:

1. Run pytest or Playwright with `--alluredir=allure-results`.
2. Generate the Allure 3 report.
3. Store report artifacts in S3.
4. Send or import results into TestOps through the supported integration for
   your deployment.
5. Verify the TestOps launch, attachments, logs, and trend data.
6. Run a restore drill for the backup bucket.

---

## Runnable Example

```bash
python course/session_30_aws_allure_testops/lecture.py
pytest course/session_30_aws_allure_testops -q
```

The examples validate a planned deployment and print the command shape for AWS
S3 setup, Allure 3 report generation, and Docker Compose verification on EC2.
They do not contact AWS, Docker, or TestOps.

---

## ✅ Session Completion Checklist

- [ ] I can explain why TestOps deployment testing is different from UI test reporting.
- [ ] I can validate S3 public access, encryption, versioning, and lifecycle requirements.
- [ ] I can explain why EC2 should use an IAM role.
- [ ] I can describe the Allure 3 evidence flow before TestOps ingestion.
- [ ] I can write smoke checks for TestOps reachability, launch creation, and service logs.
- [ ] I can define a backup and restore drill for reporting data.
- [ ] I completed the exercises in `EXERCISES.md`.

## Official References

- [Allure TestOps Docker Compose installation](https://docs.qameta.io/allure-testops/install/docker-compose/)
- [Allure Report 3 configuration](https://allurereport.org/docs/v3/configure/)
- [IAM roles for Amazon EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
- [Amazon EC2 security groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html)
- [Amazon S3 server-side encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingEncryption.html)
