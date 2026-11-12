---
name: safe-release
description: Prepare safe Opera Lirico releases with tests, minimal GitHub permissions, evidence, and rollback readiness.
---

# Safe release procedure

## Before changes
- Inspect the current main branch and relevant workflows.
- Create a focused branch; do not write directly to main.
- Keep secrets out of logs, artifacts, source files, and chat.
- Pin third-party GitHub Actions to reviewed full commit SHAs.

## CI permissions
- Default to contents: read.
- Grant contents: write only to jobs that commit repository data.
- Grant pages: write and id-token: write only to the deployment job.
- Keep backup, test, discovery, and draft-generation jobs read-only unless a specific operation requires more.
- Never expose write credentials to untrusted pull-request code.

## Validation
- Run the full unit test suite and relevant focused tests.
- Validate JSON against its schema, Python compilation, JavaScript syntax, and rendered-page behavior where relevant.
- Confirm that discovery queues remain separate from published records.
- Confirm no candidate is auto-published and no email is sent without explicit authorization.
- Review the final diff for unrelated changes, secrets, and accidental data churn.

## Release
- Open a pull request with scope, risks, tests, and rollback notes.
- Merge only after required checks pass and the diff is reviewed.
- Verify the deployed site and health check after merge.
- If deployment or data validation fails, revert the release commit and preserve the last known-good public data.
