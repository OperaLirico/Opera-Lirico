#!/usr/bin/env bash
# 按固定提交拉取上游 impeccable（Apache-2.0, pbakaus/impeccable）
set -euo pipefail

REPO="pbakaus/impeccable"
SHA="b49177d32788f2dc585c42831d845dacf1ebed2c"
SUBPATH=".agents/skills/impeccable"
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "fetching ${REPO} @ ${SHA:0:7} ..."
curl -sL "https://codeload.github.com/${REPO}/tar.gz/$SHA" -o "$TMP/src.tar.gz"

rm -rf "$DIR/upstream"
mkdir -p "$DIR/upstream"
tar -xzf "$TMP/src.tar.gz" -C "$DIR/upstream" --strip-components=1

test -f "$DIR/upstream/$SUBPATH/SKILL.md"

echo "synced: skills/impeccable/upstream"
echo "read:   upstream/${SUBPATH}/SKILL.md"
echo "read:   upstream/${SUBPATH}/reference/critique-rubric.md"
echo "note:   scripts/impeccable 首次运行会下载自带二进制，不需要 Node"
