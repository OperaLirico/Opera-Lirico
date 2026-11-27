# Security Policy

## Reporting a vulnerability

Please do not report suspected vulnerabilities in public issues or pull requests.

Use GitHub's **Report a vulnerability** option in the repository's **Security** tab to submit a private vulnerability report. Include the affected file or workflow, the steps needed to reproduce the issue, and any relevant impact. Do not include live credentials in the report.

If private vulnerability reporting is unavailable, contact the repository maintainers privately through the OperaLirico GitHub organization before disclosing the issue publicly.

## Supported versions

Security fixes are applied to the default branch. The repository is an actively developed project; deployments should use the latest reviewed default-branch release or commit.

## Secret handling

Never commit API keys, access tokens, passwords, private keys, service-account files, or production environment files. If a credential is exposed, revoke or rotate it immediately; deleting it from the latest commit is not sufficient because Git history may retain it.
