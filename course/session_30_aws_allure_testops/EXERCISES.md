# Session 30 Exercises - AWS EC2, S3, Allure TestOps, And Allure 3

> ✏️ **Exercises** · [session_30_aws_allure_testops](.) · [Lecture notes](lecture.md)


<!-- cSpell:words TestOps alluredir pytest server-side -->

## Exercise 1 - Deployment Plan Review

Run:

```bash
python course/session_30_aws_allure_testops/lecture.py
```

Identify:

- the EC2 instance name and region
- the artifacts bucket
- the backups bucket
- the generated S3 security commands
- the Allure 3 report generation command
- the TestOps Docker Compose verification commands

## Exercise 2 - S3 Bucket Security Checklist

Write a checklist for the artifacts bucket that covers:

- public access block
- server-side encryption
- versioning
- lifecycle retention
- allowed writers and readers

Explain which missing setting would block a production deployment.

## Exercise 3 - EC2 Readiness Review

Review the `EC2InstancePlan` fields in
`course/framework/cloud/aws_allure_testops.py`.

Write the evidence you would collect for:

- IAM role attached to the instance
- HTTPS reachable on port 443
- SSH restricted to approved administrators
- enough disk for reports, logs, and Docker volumes
- Docker Compose services healthy after deployment

## Exercise 4 - Allure 3 Evidence Flow

Write the commands for a CI job that:

1. runs tests with `--alluredir=allure-results`
2. generates an Allure 3 report
3. uploads the generated report folder to S3
4. records the S3 URL in CI artifacts or release notes

Keep secrets out of the command text. Use environment variable names instead.

## Exercise 5 - TestOps Smoke Suite

Design a smoke suite with five checks:

- DNS and HTTPS reachability
- login or first-admin invite readiness
- TestOps launch creation or import
- attachment visibility
- service log review after the launch

For each check, state whether it is manual, API-based, or UI-based.

## Exercise 6 - Backup And Restore Drill

Write a restore drill for the backup bucket.

Include:

- how often the drill runs
- which object prefix is used
- who approves restore access
- what evidence proves the restore worked
- how the team reports a failed restore

## Exercise 7 - Cost And Cleanup Guardrails

Write three cleanup rules for this cloud training environment.

Examples:

- stop EC2 outside workshop hours
- expire old report artifacts after the retention window
- delete temporary launches created by smoke tests
