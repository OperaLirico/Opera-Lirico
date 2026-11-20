# OperaLab. — Engineering and Product Improvement Audit

- Review date: 2026-11-19
- Reviewed ref: `main` at `ff7e42d3465708b78e3d551809326a315a716711`
- Scope: repository structure, product entry points, data pipeline, GitHub Actions, agent Skills, recent runs, open PRs/issues
- Method: read-only repository and workflow inspection; this is not a full line-by-line security audit or a live browser usability test.

## Executive summary

OperaLab is already a substantial automated information platform, not a starter website. The current repository contains 300 tracked text/binary blobs across 332 tree entries, 55 Python files (including tests), 25 test modules, 28 data files, and 63 GitHub Actions workflow files.

The project already has a mature source/evidence pipeline and an L4-style automation design. The next phase should therefore prioritize reliability, user-facing data quality, workflow consolidation, and maintenance discipline—not another general-purpose agent or another parallel scraper.

## What is already working in the architecture

- Static website/PWA with a single main application entry point and separate pages for masterclasses and vocal anatomy.
- Opportunity records are separated from discovered candidates; the public "open" state is intended to require review and official-source evidence.
- Conservatory admission collection is separate from theatre/competition source collection.
- Repertoire collection uses a candidate queue; candidates are not automatically published as curated arias.
- Daily collection and weekly discovery/coverage are deliberately separated.
- Last-good snapshots are retained when a source fails.
- Automated checks cover source quality, opportunity data, time zones, repertoire candidates, section search, SEO metadata, workflow separation, and workflow trigger safety.
- The project has monitoring, a failure digest, limited self-healing, a private operations dashboard, and deployment rollback.
- The daily REA upstream watch compares official upstream metadata and opens a review issue when drift is detected.

## Findings and priorities

### P0 — Fix KV backup artifact lifecycle

**Finding:** The 2026-11-19 KV backup run failed at "Upload encrypted backup". In `.github/workflows/kv-backup.yml`, the encryption step sets an EXIT trap that deletes the encrypted file (`ENC`) when that shell step exits. GitHub Actions runs the upload step only after the shell exits, so the file can be removed before `upload-artifact` reads it.

**Proposed fix:** Keep the encrypted artifact through upload, retry the upload once on failure, download the resulting artifact in the same run, decrypt it and validate the KV backup schema/key count, then remove temporary encrypted and plaintext files.

**Status:** Implemented on branch `fix/kv-backup-artifact-lifecycle`; CI and a successful workflow-dispatch backup run are still required. Do not report the backup as repaired until upload and restore verification both succeed.

### P1 — Triage the failing workflow-security audit

The project-agent queue reported a failed "Source quality tests" run at the "Audit GitHub Actions security" step on 2026-11-19. The static audit checks SHA-pinned external Actions and permission scoping.

The complete 2026-11-19 job log identifies six findings: `.github/workflows/cycle2-log.yml` through `cycle7-log.yml` each used floating `actions/checkout@v4` rather than a full commit SHA. The source-quality unit tests all passed (155 tests); the security audit alone failed.

**Correction:** Pin those six cycle-log workflows to the verified upstream `actions/checkout v4.2.2` commit `11bd71901bbe5b1630ceea73d27597364c9af683`. This keeps the audit strict and preserves the workflows' existing triggers and write permissions. Re-run the audit before merging.

### P1 — Review the pending REA Skill update

- Open PR: [#127 — sync OperaLab baseline to upstream Skill v63](https://github.com/OperaLirico/Opera-Lirico/pull/127)
- Scope is documentation metadata and upstream compatibility baseline only.
- It does not install or update the local REA MCP runtime.
- Review the official upstream commit and PR checks before merging.

The daily REA watch is useful and should remain detection-first: detect upstream drift, create a review task/PR, and never silently update local runtime or production workflows.

### P1 — Establish one Skill inventory and update policy

Current project Skills include:
- `.agents/skills/rea-research-lab`: generic cross-project method; now also copied into ERA, but the source-of-truth/reference relationship still needs to be formalized.
- `.agents/skills/rea-reverse-engineering`: OperaLab-specific adapter with a dated upstream baseline.
- `.agents/skills/anatomy`: pinned Git submodule; update should be reviewed and pinned deliberately.

Recommended inventory fields:
- Skill name and purpose
- Upstream repository and canonical path
- License
- Pinned commit/release/version
- Last reviewed date
- Local modifications / project adapter boundary
- Update method (watch-only, PR, or manual)
- Last test/validation result

Recommended policy:
1. Check upstream drift on a schedule (weekly is sufficient for most Skills; daily only for fast-moving critical tooling).
2. Create an issue or PR with the upstream diff and release/license notes.
3. Run the Skill quality gate and project-specific regression tests.
4. Require human review before changing the pinned version.
5. Never auto-install or silently replace a Skill in the user's local Codex environment.

The REA daily watcher is an existing implementation to reuse. Do not create a second REA watcher.

### P1 — Reduce workflow sprawl safely

The repository currently has 63 workflow files. A large group of similarly named `larynx-map-v*`, `larynx-overlay*`, and `larynx-frames-*` workflows appears to record iterative visual experiments; `cycle2-log` through `cycle7-log` are also individually represented.

This is a maintenance and discoverability cost, but file names alone do not prove that a workflow is obsolete. Before removing or consolidating:
- Inspect every workflow's trigger, outputs, artifact retention, and latest run.
- Identify which outputs are still used by the site or future anatomy integration.
- Preserve reproducible source/assets and provenance.
- Consolidate only after a single parameterized experiment workflow can reproduce the needed outputs.
- Archive old workflows rather than deleting useful research history.

Do not touch these workflows as part of an unrelated production fix.

### P2 — Product information architecture and discovery

The homepage currently exposes six major areas:
1. Theatre auditions and competitions
2. Conservatory admissions
3. Theatre Accademia
4. Combined aria and art-song repertoire
5. Masterclasses
6. Vocal anatomy lab

The repertoire panel already advertises search by work, composer, lyrics, and voice type. Preserve this combined catalogue model; do not split art songs into a disconnected standalone section.

Next usability review should test the complete user journeys:
- A singer finds an open audition and verifies the official application page/PDF.
- A Chinese-speaking applicant finds a conservatory and understands the application window, exam date, requirements, and source limitations.
- A singer finds a masterclass and can distinguish official confirmed details from discovered candidates.
- A user searches a repertoire title, composer, lyric fragment, or voice type and can open the correct source/score.
- A learner opens the anatomy lab and can understand what is modeled, what is simplified, and what is evidence-backed.

For each journey, inspect mobile layout, empty/loading/error states, stale data, and the path back to the main sections. Do not add features until these flows are tested.

### P2 — Improve user-visible data freshness and confidence

Keep separate labels for:
- Last checked time
- Last successful fetch time
- Source status
- Data freshness
- Human verification state
- Official source link

A successful scheduled run is not proof that every source returned fresh content. A failed source should not silently look current merely because a last-good snapshot is shown. Preserve the current last-good behavior but make stale/fallback status prominent and understandable.

### P3 — Visual design and motion

Taste and GSAP are not assumed to be installed in OperaLab. If tested:
- Select one real page and record a baseline screenshot.
- Use Taste only to define a design direction and hierarchy.
- Use GSAP only for purposeful motion, with reduced-motion and mobile performance checks.
- Keep the trial on a feature branch and compare before/after; do not redesign the entire site for tool adoption.

## Current operational signals checked

- Recent runs on 2026-11-19 showed the daily source refresh, system health check, analytics watchdog, REA upstream watch, masterclass discovery, social draft generation, and self-heal jobs completing successfully.
- KV backup failed at artifact upload.
- The project-agent daily review reported a Source quality tests failure at the workflow security audit step; root cause not confirmed from the available job metadata.
- Open PRs include #127 (REA v63 baseline), #109 (weekly source discovery), #107 (changedetection.io/Modern Web Guidance), #101/#105/#124 (anatomy work), and additional draft quality/privacy work. Review and close/merge deliberately; avoid creating parallel implementations for already-open work.

## Recommended execution order

1. Complete and verify the KV backup artifact fix.
2. Retrieve and resolve the exact workflow-security audit failure.
3. Review PR #127 and keep REA upstream updates on the existing review-first process.
4. Add the Skills inventory and a common update/evaluation policy; include the pinned Anatomy submodule and the ERA generic core.
5. Audit the 63 workflows and propose a safe consolidation map; do not delete before mapping dependencies.
6. Run five mobile-first product journey tests across the six main areas.
7. Prioritize data freshness/confidence and search accuracy improvements based on observed failures.
8. Trial Taste/GSAP on one page only if the baseline review finds a meaningful visual issue.

## Explicit non-goals for this pass

- No new server, database, Docker service, or paid API.
- No replacement of Scrapling or current source collection pipeline.
- No automatic publication of auditions, masterclasses, repertoire, social content, or newsletters.
- No local Codex/MCP installation or automatic Skill replacement.
- No merge to main or production deployment without review and successful checks.
- No deletion of historical workflows or source records based only on names.

## Verification status

This document records a repository/workflow audit. The KV workflow change is proposed on a branch; no successful backup rerun has yet been observed. No live visual/browser journey test was performed in this audit.
