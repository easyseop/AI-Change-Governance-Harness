#!/usr/bin/env bash
# Codex 작업 시작 런처 — 최신 main 받고 → Codex 무인(full-auto 동등) 실행
# 사용: 클론한 repo 폴더 안에서   ./scripts/start-codex.sh
# 무인 조합: -a never(승인 안 물음) + -s workspace-write(작업폴더 쓰기) +
#            network_access=true(git push 되도록 네트워크 허용).
# 이 codex 버전엔 --full-auto 플래그가 없어 위 조합으로 대체.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo 루트로 이동 (스크립트 위치 기준)

echo "▶ main 최신화 (pull)..."
git checkout main
git pull origin main

echo "▶ Codex 실행 (무인: -a never -s workspace-write +network)"
exec codex --ask-for-approval never --sandbox workspace-write \
  -c sandbox_workspace_write.network_access=true \
  "START-HERE.md → COMMON-RULES.md → AGENTS.md → TASKS.md 읽고, 네 역할대로 오늘 날짜 브랜치(codex/$(date +%F)-<주제>)를 main 기준으로 만들어 다음 할 일을 진행해. 끝나면 COMMON-RULES §3 형식의 상세 커밋 후, collab/handoff-log.md 한 줄 + summaries/$(date +%F).md 누적 기록하고 네 브랜치로 push해. 루트에 STOP 파일 있으면 즉시 중단. main 직접 push·자기 머지 금지."
