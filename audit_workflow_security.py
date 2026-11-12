#!/usr/bin/env python3
"""Static security checks for GitHub Actions workflow configuration."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORKFLOW_DIR = ROOT / ".github" / "workflows"
PINNED_ACTION = re.compile(r"^[^\s]+@[0-9a-f]{40}$")


def top_level_block(lines: list[str], key: str) -> list[str]:
    start = next((i for i, line in enumerate(lines) if line == f"{key}:"), None)
    if start is None:
        return []
    result = []
    for line in lines[start + 1:]:
        if line and not line[0].isspace():
            break
        result.append(line)
    return result


def audit_workflows() -> list[str]:
    errors: list[str] = []
    workflows = sorted(WORKFLOW_DIR.glob("*.yml"))
    if not workflows:
        return ["No GitHub Actions workflows found"]

    for path in workflows:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for number, line in enumerate(lines, 1):
            match = re.match(r"^\s*uses:\s*([^\s#]+)", line)
            if not match:
                continue
            action = match.group(1)
            if action.startswith("./"):
                continue
            if not PINNED_ACTION.fullmatch(action):
                errors.append(
                    f"{path.relative_to(ROOT)}:{number}: action is not pinned to a full 40-character SHA: {action}"
                )

        permissions = top_level_block(lines, "permissions")
        has_top_level_write = any(re.search(r":\s*write\s*$", line) for line in permissions)
        jobs_index = next((i for i, line in enumerate(lines) if line == "jobs:"), None)
        job_lines = lines[jobs_index + 1:] if jobs_index is not None else []
        job_count = sum(1 for line in job_lines if re.match(r"^  [a-zA-Z0-9_-]+:\s*$", line))
        if has_top_level_write and job_count > 1:
            errors.append(
                f"{path.relative_to(ROOT)}: workflow-level write permission spans {job_count} jobs; scope it to the required job"
            )

    daily = WORKFLOW_DIR / "daily-scrape-and-publish.yml"
    if daily.exists():
        text = daily.read_text(encoding="utf-8")
        if re.search(r"(?m)^permissions:\n(?:  [^\n]*\n)*  (?:contents|pages|id-token): write", text):
            errors.append("daily-scrape-and-publish.yml: broad workflow-level write permission remains")
        if not re.search(r"(?ms)^  build:\n(?:(?!^  [a-zA-Z0-9_-]+:).)*?^    permissions:\n      contents: write", text):
            errors.append("daily-scrape-and-publish.yml: build job must explicitly own contents: write")
        if not re.search(r"(?ms)^  deploy:\n(?:(?!^  [a-zA-Z0-9_-]+:).)*?^    permissions:\n      contents: read\n      pages: write\n      id-token: write", text):
            errors.append("daily-scrape-and-publish.yml: deployment permissions must be isolated to the deploy job")

    return errors


def main() -> int:
    errors = audit_workflows()
    if errors:
        print("WORKFLOW SECURITY AUDIT FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    count = len(list(WORKFLOW_DIR.glob("*.yml")))
    print(f"PASS: {count} workflows checked; all external actions use full commit SHAs.")
    print("PASS: daily source refresh write permissions are separated from Pages deployment permissions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
