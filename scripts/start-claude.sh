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

# ── 리뷰 대기 Codex 브랜치 자동 스캔 ──────────────────────────
# handoff-log(main)은 Claude가 반입(merge)한 것만 반영한다 → Codex가 방금 push한
# 신규 브랜치는 아직 안 뜬다. 그래서 origin/codex/* 를 직접 스캔해 "main 에 아직
# 머지 안 된" 브랜치를 리뷰 대기 후보로 잡는다(신규 제출을 놓치지 않기 위함).
echo "▶ 리뷰 대기(미머지) Codex 브랜치 스캔..."
PENDING=""
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/codex 2>/dev/null); do
  if ! git merge-base --is-ancestor "$b" origin/main 2>/dev/null; then
    PENDING="${PENDING}
  - ${b#origin/}  (tip: $(git log -1 --format='%h %s' "$b"))"
  fi
done
if [ -n "$PENDING" ]; then
  echo "⚠ 미머지 Codex 브랜치 (리뷰 또는 보정대기):${PENDING}"
else
  echo "  (미머지 Codex 브랜치 없음)"
fi

FLAGS=""
if [ "${ACGH_YOLO:-0}" = "1" ]; then
  FLAGS="--dangerously-skip-permissions"
  echo "⚠ 무인 모드(ACGH_YOLO=1): 권한확인을 건너뜁니다."
fi

echo "▶ Claude 실행"
exec claude $FLAGS "먼저 'git fetch origin --prune' 후 origin/codex/* 중 main 에 아직 머지 안 된 브랜치를 모두 나열해라(위 런처 스캔 결과 참고). 각 미머지 브랜치를 collab/handoff-log.md·collab/decisions.md 와 대조해 상태 분류: (가) 아직 리뷰 안 됨 = 네 리뷰 차례 / (나) handoff 최신이 '보정요청' = Codex 보정 차례이니 건드리지 마라 / (다) 이미 머지·done = 무시. (가) 브랜치를 main 대비 리뷰해줘. CLAUDE.md/COMMON-RULES 준수(TASKS.md 수용기준 + §1 보수적 개발 평가축). ★심층·적대적 리뷰(CLAUDE.md §2B): '그럴듯함'으로 통과 금지 — 코드를 한 줄씩 뜯어보고, 깨뜨릴 입력을 직접 만들어 돌려보고(픽스처 밖 fresh 입력 + 기대값 변조 음성검증), '내가 짠다면 더 나은가'·'이 출력을 다음 태스크가 어떻게 쓰나(하류 영향)'까지 따져 논리 정합을 검증해라. 무발견≠통과. 거버넌스에 영향 주는 결함은 비차단으로 흘리지 말고 보정요청 또는 차기 AC 가드로 명시. ★★킷 관련 리뷰(kit/ 변경·TASK-026 등 배포 킷)는 특히 상세하게 검토하라 — 킷은 배포·실사용 최전선이라 결함 파급이 크다: (1) run.sh 의 게이트 배선·verdict 조립(max 우선순위)이 각 게이트 실제 exit 의미와 정확히 맞는지, 새 판정층이 누락 없이 조립되는지, (2) 게이트 co-located 내부 의존이 킷에서 실제 해소되는지, (3) HAS_RANGE·정책 부재·--policies 오버라이드·분석실패 fail-closed 전 경로를 fresh 적대입력으로 직접 재현, (4) sync 로 dev 게이트가 빠짐없이 반영됐는지(개수뿐 아니라 실작동), (5) selftest·진입점 적대 전량 재현 + rig-and-revert 로 신규 가드 load-bearing 확인 — 한 줄씩·빠짐없이. 통과/보정은 collab/decisions.md·collab/answers/ 에 기록하고, claude/$(date +%F)-review 브랜치로 상세 커밋 후 push해. 머지(D-007): 리뷰 통과 + 비민감 변경이면 그 브랜치를 main 에 머지하고 push해(구현자≠머지자). 민감 변경(정산·인증/인가·암호화·DB migration·infra 등 CLAUDE.md 🔴🟠)이면 머지하지 말고 collab/needs-human/H-XXXX.md 로 형 승인 요청. 보정 필요하면 collab/answers/ 로 반려하고 머지 보류. 루트에 STOP 파일 있으면 즉시 중단."
