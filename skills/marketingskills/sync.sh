#!/usr/bin/env bash
# 按固定提交拉取上游 marketingskills（MIT, coreyhaines31/marketingskills）
# 只读 seo-audit / schema / cro / emails 四个子技能
eset -euo pipefail

REPO="coreyhaines31/marketingskills"
SHA="5b2b400eec1e7e1cec76245a715d0b0d4fd2a9c1"
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "fetching ${REPO} @ ${SHA:0:7} ..."
curl -sL "https://codeload.github.com/${REPO}/tar.gz/$SHA" -o "$TMP/src.tar.gz"

rm -rf "$DIR/upstream"
mkdir -p "$DIR/upstream"
tar -xzf "$TMP/src.tar.gz" -C "$DIR/upstream" --strip-components=1

for s in seo-audit schema cro emails; do
  test -f "$DIR/upstream/skills/$s/SKILL.md"
done

echo "synced: skills/marketingskills/upstream (4 of 50+ skills)"
echo "read:   upstream/skills/seo-audit/SKILL.md"
echo "read:   upstream/skills/schema/SKILL.md"
echo "read:   upstream/skills/cro/SKILL.md"
echo "read:   upstream/skills/emails/SKILL.md"
