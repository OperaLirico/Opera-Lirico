# Repository Tools

This directory is reserved for supporting utilities that do not need to run in the browser.

## Planned modules

- `pdf_parser/`: isolated parsing of public competition and conservatory PDFs.
- `monitoring/`: lightweight source-change tracking that can be called from a scheduled job.

## Rules

- Keep experimental dependencies isolated from the production scraper dependencies.
- Do not change the current website data contract without a reviewed migration.
- Do not store credentials or private source documents here.
- Add tests and usage instructions before connecting a tool to the daily production workflow.
