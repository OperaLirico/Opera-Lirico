# Italia Audizioni — Architecture

## Current baseline

The repository is a GitHub Pages site with a Python-based collection pipeline. The existing site and scheduled workflow remain the source of truth during this foundation phase.

Current components observed in the repository include:

- Static frontend: `index.html`, `app.js`, and `styles.css`
- Public data files under `data/`
- Existing collection scripts such as `scrape_sources.py` and conservatory-related scripts
- Existing GitHub Actions workflow: `.github/workflows/daily-scrape-and-publish.yml`

This document does not replace or modify those components.

## Target direction

1. Official public pages and documents are discovered by the existing collection scripts.
2. Scrapling continues to collect permitted public web content.
3. A separate PDF parsing module may use Docling after compatibility and runtime testing.
4. Extracted records are reviewed before being treated as verified opportunities.
5. The current JSON data format remains compatible with the static website.
6. Supabase may be introduced later as an additional structured store, without requiring an immediate frontend rewrite.

## Proposed tool boundaries

- `tools/pdf_parser/`: isolated PDF parsing experiments and scripts.
- `tools/monitoring/`: source-change fingerprints and monitoring utilities that can run within existing scheduled jobs.
- `docs/`: architecture, deployment, and operational guidance.

## Design constraints

- Do not couple the static website to Python-only runtime services.
- Do not add heavyweight dependencies to the existing daily workflow until tested independently.
- Preserve current JSON contracts until a deliberate migration is reviewed.
- Keep credentials out of the repository and browser bundle.
- Track official source URLs and last-verified timestamps.
