#!/usr/bin/env bash
# Claude 리뷰 시작 런처 — 최신 main 받고 → Claude 실행
# 사용:
#   ./scripts/start-claude.sh              # 기본: 안전(권한확인) 모드
#   ACGH_YOLO=1 ./scripts/start-claude.sh  # 무인 모드(권한확인 건너뜀, --dangerously-skip-permissions)
#
# ⚠ Claude 는 게이트키퍼(리뷰어)다. 무인 모드는 "틀 잡는 부트스트랩 단계"용 임시 편의이고,
#   틀이 안정되면 기본(안전) 모드로 되돌리는 걸 권장한다. git pull/checkout 은 이 쉘이 한다.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo 루트로 이동 (스크립트 위치 기준)

echo "▶ main 최신화 (pull/fetch)..."
git checkout main
git pull origin main
git fetch origin --prune

FLAGS=""
if [ "${ACGH_YOLO:-0}" = "1" ]; then
  FLAGS="--dangerously-skip-permissions"
  echo "⚠ 무인 모드(ACGH_YOLO=1): 권한확인을 건너뜁니다."
fi

echo "▶ Claude 실행"
exec claude $FLAGS "collab/handoff-log.md 최신 줄에서 Codex가 올린 작업 브랜치를 확인하고, 그 브랜치를 main 대비 리뷰해줘. CLAUDE.md/COMMON-RULES 준수(TASKS.md 수용기준 + §1 보수적 개발 평가축). 통과/보정은 collab/decisions.md·collab/answers/ 에 기록하고, claude/$(date +%F)-review 브랜치로 상세 커밋 후 push해. 머지(D-007): 리뷰 통과 + 비민감 변경이면 그 브랜치를 main 에 머지하고 push해(구현자≠머지자). 민감 변경(정산·인증/인가·암호화·DB migration·infra 등 CLAUDE.md 🔴🟠)이면 머지하지 말고 collab/needs-human/H-XXXX.md 로 형 승인 요청. 보정 필요하면 collab/answers/ 로 반려하고 머지 보류. 루트에 STOP 파일 있으면 즉시 중단."
