# Deployment and Operations

## Current deployment

The public website is hosted with GitHub Pages. Existing data collection and publishing are handled by the repository's current GitHub Actions workflow:

`.github/workflows/daily-scrape-and-publish.yml`

This foundation change intentionally does not edit that workflow or the website entry files.

## Safe development workflow

1. Work on a feature branch, not directly on `main`.
2. Keep changes isolated and review the diff before merging.
3. Test Python scripts locally in a virtual environment or in a separate workflow.
4. Do not merge experimental PDF parsing into the production schedule until it passes representative tests.
5. Merge only after checking the Pages build and a successful collection run.

## Local Python setup

Use a project-specific virtual environment. Do not install project dependencies globally.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install only the dependencies required by the specific tool being tested. Keep experimental dependencies isolated from the current root `requirements.txt` until compatibility has been confirmed.

## GitHub Actions secrets

If future automation needs credentials:

1. Open repository Settings → Secrets and variables → Actions.
2. Add only the required secret.
3. Read it through the workflow's `secrets.NAME` context.
4. Never print secret values in logs.
5. Never place service-role keys in frontend JavaScript or public files.

No secret is required for the foundation files added in this branch.

## GitHub Pages and public data

Anything included in the published site or public repository should be treated as publicly readable. Do not store private notes, personal information, credentials, or unpublished applicant data in the Pages output.

## Future Supabase integration

Start with the hosted free tier if it meets current limits. Apply Row Level Security to exposed tables. Keep privileged keys exclusively in server-side environments or GitHub Actions Secrets. Do not self-host Supabase as part of this initial setup.

## Rollback

Because these changes are isolated on `feature/repo-foundation`, they can be abandoned by closing the associated pull request or deleting the feature branch. Do not force-push or rewrite the production branch.
