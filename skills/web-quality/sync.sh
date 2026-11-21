#!/usr/bin/env bash
# 按固定提交拉取上游 agent-skills（MIT, addyosmani/agent-skills）
# 只读 accessibility / performance / browser-testing 三个子技能
set -euo pipefail

REPO="addyosmani/agent-skills"
SHA="8c99fa36d90068c82d547f7c12a9d67a3e95f4ee"
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "fetching ${REPO} @ ${SHA:0:7} ..."
curl -sL "https://codeload.github.com/${REPO}/tar.gz/$SHA" -o "$TMP/src.tar.gz"

rm -rf "$DIR/upstream"
mkdir -p "$DIR/upstream"
tar -xzf "$TMP/src.tar.gz" -C "$DIR/upstream" --strip-components=1

for s in accessibility-engineering performance-optimization browser-testing-with-devtools; do
  test -f "$DIR/upstream/skills/$s/SKILL.md"
done

echo "synced: skills/web-quality/upstream (3 of 26 skills)"
echo "read:   upstream/skills/accessibility-engineering/SKILL.md"
echo "read:   upstream/skills/performance-optimization/SKILL.md"
