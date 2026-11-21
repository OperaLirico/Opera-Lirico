#!/usr/bin/env bash
# 按固定提交拉取上游 scrapling 技能（MIT, Cedriccmh/claude-code-skill-scrapling）
set -euo pipefail

REPO="Cedriccmh/claude-code-skill-scrapling"
SHA="85dd89f5f85a6326712c516bc82f84c2ceb28c19"
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "fetching ${REPO} @ ${SHA:0:7} ..."
curl -sL "https://codeload.github.com/${REPO}/tar.gz/$SHA" -o "$TMP/src.tar.gz"

rm -rf "$DIR/upstream"
mkdir -p "$DIR/upstream"
tar -xzf "$TMP/src.tar.gz" -C "$DIR/upstream" --strip-components=1

test -f "$DIR/upstream/SKILL.md"
test -f "$DIR/upstream/references/site-patterns.md"

echo "synced: skills/scrapling/upstream"
echo "read:   upstream/SKILL.md"
echo "read:   upstream/references/security.md  (每次抓取前)"
echo "read:   upstream/references/site-patterns.md"
echo "note:   需要 python + pip install \"scrapling[fetchers]\" && scrapling install"
