# REA Research Lab

A reusable, evidence-led research and engineering operating system built around the official [REA](https://github.com/morluto/rea) toolchain.

This Lab is deliberately separate from any single product. The same method can be attached to OperaLab or another authorized repository without copying project-specific rules into the core methodology.

## What it does

The Lab connects six stages:

`Research → Evidence → Architecture → Development → Quality → Stewardship`

It is designed to prevent a common failure mode: seeing an impressive product, guessing how it works, and immediately building a superficial imitation. REA is used to establish behavior and technical facts; the project team then decides what is useful, implements a scoped version, and verifies it.

## Core components

- Agent skill: `.agents/skills/rea-research-lab/SKILL.md`
- OperaLab adapter: `.agents/skills/rea-reverse-engineering/SKILL.md`
- Upstream compatibility baseline: `.agents/skills/rea-reverse-engineering/references/upstream-baseline.json`
- Daily upstream drift monitor: `.github/workflows/rea-upstream-watch.yml`
- Templates: `docs/rea-research-lab/templates/`

## Research lanes

The Lab covers websites/browser apps, JavaScript/Electron, desktop software, Android, native binaries, managed assemblies, firmware, network captures/API contracts, runtime behavior, and other supplied artifacts—subject to the current REA release, host, providers, and actual live tool catalog.

It does **not** require every lane to be installed. Start with the smallest route that answers the question. Do not install Ghidra, IDA, Hopper, JADX, Binwalk, or other providers unless a real task requires one and the user approves it.

## Operating rules

1. Start from a decision or user problem, not from a tool demo.
2. Confirm target ownership/authorization and define exclusions.
3. Prefer passive/static inspection; runtime actions need explicit scope.
4. Keep Observed, Inferred, and Unknown separate.
5. Preserve source identity, evidence, coverage, and limitations.
6. Build only when evidence and acceptance criteria are sufficient.
7. Use branches, tests, review, and explicit deployment gates.
8. Never claim MCP connectivity from a committed Skill file.
9. Never claim browser verification from CI alone.
10. No automatic merge, production activation, or paid provider installation.

## First project adapter: OperaLab.

Initial domains:
- Anatomy / vocal physiology: source and anatomical fidelity, provenance, licensing, and clear distinction between teaching models and clinical footage.
- Audizioni: official-source authority, deadlines, eligibility, document integrity, timezone correctness, and duplicate detection.
- Masterclass: teacher/institution authority, dates, location, repertoire, application requirements, and source freshness.
- Conservatorio: official admission notices, academic year, deadlines, requirements, and document provenance.

The adapter is intentionally narrow. Other projects should add their own adapter without changing the universal Lab workflow.

## Daily upstream maintenance

The daily GitHub Action compares:
- Latest official REA GitHub release.
- Latest published `rea-agents` npm package.
- Upstream Skill metadata version.
- The baseline recorded in this repository.

A mismatch opens or refreshes a review issue. It does not blindly copy upstream code, change local MCP configuration, or deploy an update. This is deliberate: release review and compatibility verification are safer than unattended installation.

## Research templates

- [Research brief](templates/research-brief.md)
- [Evidence ledger](templates/evidence-ledger.md)
- [Implementation specification](templates/implementation-spec.md)
- [Verification report](templates/verification-report.md)

## Current limitation

The repository can maintain the Skill and detect upstream drift. Local MCP/plugin/CLI installation and live tool availability still have to be verified in the user's active coding-agent environment. A connected GitHub account does not expose that local runtime.
