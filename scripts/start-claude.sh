#!/usr/bin/env bash
# Claude 리뷰 시작 런처 — 최신 main 받고 → Claude 실행
# 사용: 클론한 repo 폴더 안에서   ./scripts/start-claude.sh
# 참고: git pull/checkout 은 이 스크립트(쉘)가 자동으로 한다. Claude 자체는
#       일반(권한확인) 모드로 띄운다 — Claude 는 게이트키퍼라 무인화하지 않는다.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo 루트로 이동 (스크립트 위치 기준)

echo "▶ main 최신화 (pull/fetch)..."
git checkout main
git pull origin main
git fetch origin --prune

echo "▶ Claude 실행"
exec claude "collab/handoff-log.md 최신 줄에서 Codex가 올린 작업 브랜치를 확인하고, 그 브랜치를 main 대비 리뷰해줘. CLAUDE.md/COMMON-RULES 준수(TASKS.md 수용기준 + §1 보수적 개발 평가축). 통과/보정은 collab/decisions.md·collab/answers/ 에 기록하고, claude/$(date +%F)-review 브랜치로 상세 커밋 후 push해. 루트에 STOP 파일 있으면 즉시 중단."
