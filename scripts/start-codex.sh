#!/usr/bin/env bash
# Codex 작업 시작 런처 — 최신 main 받고 → Codex 무인(full-auto 동등) 실행
# 사용: 클론한 repo 폴더 안에서   ./scripts/start-codex.sh
# 무인 조합: -a never(승인 안 물음) + -s workspace-write(작업폴더 쓰기) +
#            network_access=true(git push 되도록 네트워크 허용).
# 이 codex 버전엔 --full-auto 플래그가 없어 위 조합으로 대체.
set -euo pipefail
cd "$(dirname "$0")/.."          # repo 루트로 이동 (스크립트 위치 기준)

echo "▶ 최신 상태 확인..."
git fetch origin --quiet 2>/dev/null || true

# ── 보정요청 감지 ─────────────────────────────────────────────
# handoff-log 맨 위(최신) 줄이 '보정요청'이면 = 새 태스크가 아니라 재수정 차례.
# 이땐 main 으로 강제 전환하지 않는다(작업 브랜치·미커밋 보존). Codex 가 그 브랜치에서 보정.
TOP="$(git show origin/main:collab/handoff-log.md 2>/dev/null | grep -m1 '^- \[' || true)"
if printf '%s' "$TOP" | grep -q '보정요청'; then
  echo "⚠ 최신 인계 = 보정요청. 새 태스크가 아니라 '재수정' 차례입니다."
  echo "   $TOP"
  echo "   → main 으로 전환하지 않습니다(작업 트리 보존)."
  MODE="보정"
else
  echo "▶ main 최신화 (pull)..."
  git checkout main
  git pull origin main
  MODE="새태스크"
fi

echo "▶ Codex 실행 (무인: -a never -s workspace-write +network) · 모드=$MODE"
exec codex --ask-for-approval never --sandbox workspace-write \
  -c sandbox_workspace_write.network_access=true \
  "먼저 collab/handoff-log.md 맨 위(최신) 줄을 확인해라. \
(A) 맨 위 줄이 '보정요청'이면: main 으로 새 브랜치를 만들지 말고, 그 줄이 가리키는 작업 브랜치를 checkout 해서 collab/answers/A-XXXX.md 의 지시대로 보정하고 tests/run-tests.sh 전체 green 확인 후 같은 브랜치에 상세 커밋·push(재인계). 워킹트리에 커밋 안 된 변경이 있으면 먼저 확인해 살릴지 판단. \
(B) 그 외(리뷰통과·done·새 태스크)면: START-HERE.md → COMMON-RULES.md → AGENTS.md → TASKS.md 읽고 오늘 날짜 브랜치(codex/$(date +%F)-<주제>)를 최신 main 기준으로 만들어 다음 할 일을 진행해. \
어느 경우든 끝나면 COMMON-RULES §3 형식의 상세 커밋 후 collab/handoff-log.md 한 줄 + summaries/$(date +%F).md 누적 기록하고 push. 루트에 STOP 파일 있으면 즉시 중단. main 직접 push·자기 머지 금지."
