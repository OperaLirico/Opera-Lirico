#!/usr/bin/env bash
# 按固定提交拉取上游 tasteskill（MIT, Leonxlnx/taste-skill）
set -euo pipefail

SHA=f6b76575f949707b4e3c37cd86cb44b0b98643e8
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "fetching tasteskill @ ${SHA:0:7} ..."
curl -sL "https://codeload.github.com/Leonxlnx/taste-skill/tar.gz/$SHA" -o "$TMP/src.tar.gz"

rm -rf "$DIR/upstream"
mkdir -p "$DIR/upstream"
tar -xzf "$TMP/src.tar.gz" -C "$DIR/upstream" --strip-components=1

test -f "$DIR/upstream/skills/taste-skill/SKILL.md"
test -f "$DIR/upstream/LICENSE"

COUNT=$(find "$DIR/upstream/skills/taste-skill" -type f | wc -l | tr -d ' ')
echo "synced: skills/taste-skill/upstream  (${COUNT} files)"
echo "read:   upstream/skills/taste-skill/SKILL.md"
echo "note:   Node 22+ and Chrome needed for its scripts"
