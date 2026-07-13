#!/usr/bin/env bash
# Codex 작업 시작 런처 — 최신 main 받고 → Codex 무인(full-auto 동등) 실행
# 사용: 클론한 repo 폴더 안에서   ./scripts/start-codex.sh
# 무인 조합: -a never(승인 안 물음) + 아래 sandbox 모드.
# 이 codex 버전엔 --full-auto 플래그가 없어 위 조합으로 대체.
#
# ── sandbox 모드 (2026-07-04 수정) ────────────────────────────
# 기본값 danger-full-access. 이유: -s workspace-write 가 .git 을 읽기전용으로
# 열어 Codex 내부의 브랜치 생성·fetch·commit(refs/…lock, FETCH_HEAD 쓰기)을
# 막는 문제가 있었다. 자기 repo 무인 자동화(-a never)라 전체 접근을 허용해
# git 이 항상 되게 한다(full-access 는 네트워크도 포함 → 별도 network 플래그 불요).
# 더 강한 격리를 원하면:  ACGH_SANDBOX=workspace-write ./scripts/start-codex.sh
#
# ── 보정요청 자동 인계 (2026-07-11 보강) ────────────────────────
# 최신 인계가 '보정요청'이면: 헤드 커밋으로 작업 브랜치를 자동 식별·checkout 하고,
# 리뷰기록(A-XXXX)을 origin/main 에서 읽어 출력한다(리뷰기록은 main 에만 있어
# Codex 가 자기 브랜치만 pull 하면 보정요청을 못 보던 문제를 막는다). main 은
# 머지하지 않는다(collab 로그 append 충돌 — 읽기는 origin/main 에서).
set -euo pipefail
cd "$(dirname "$0")/.."          # repo 루트로 이동 (스크립트 위치 기준)

SANDBOX="${ACGH_SANDBOX:-danger-full-access}"
if [ "$SANDBOX" = "workspace-write" ]; then
  SBOX_ARGS=(--sandbox workspace-write -c sandbox_workspace_write.network_access=true)
else
  SBOX_ARGS=(--sandbox danger-full-access)
fi

echo "▶ 최신 상태 확인..."
git fetch origin --quiet 2>/dev/null || true

# ── 보정요청 감지 ─────────────────────────────────────────────
# handoff-log 맨 위(최신) 줄이 '보정요청'이면 = 새 태스크가 아니라 재수정 차례.
# 이땐 main 으로 강제 전환하지 않는다(작업 브랜치·미커밋 보존). Codex 가 그 브랜치에서 보정.
TOP="$(git show origin/main:collab/handoff-log.md 2>/dev/null | grep -m1 '^- \[' || true)"
# ★볼드 태그 '(**보정요청**)' 로만 감지 — 맨 문자열 '보정요청' 매칭 시, 산문에서 그 단어를
#   언급만 해도(예: "재수정 대상 아님" 설명) 오탐한다. HEADC 추출과 동일 태그로 정밀화.
if printf '%s' "$TOP" | grep -qF '(**보정요청**)'; then
  echo "⚠ 최신 인계 = 보정요청. 새 태스크가 아니라 '재수정' 차례입니다."
  echo "   $TOP"
  # 리뷰기록(A-XXXX·decisions·handoff 신호)은 origin/main 에만 있고 작업 브랜치엔 없다.
  # → 작업 브랜치를 '보정요청' 줄의 헤드 커밋으로 자동 식별해 checkout(엉뚱한 브랜치 pull 로 보정요청을 못 보던 문제 방지).
  #   main 은 머지하지 않는다(collab 로그가 append 충돌). 리뷰기록은 origin/main 에서 '읽는다'.
  # 헤드 커밋 = ' (**보정요청**)' 바로 앞의 hex 토큰. 형식이 진화해도 견고하게:
  #   신형 '| <구현> / 헤드 <head> (**보정요청**)' · 구형 '| <head> (**보정요청**)' 둘 다 대응
  #   (앞 구분자를 [^0-9a-f] 로 잡아 '| '·'헤드 ' 무엇이든 허용). ★set -euo pipefail 아래서
  #   추출 실패(빈 값)면 git/grep 이 비영종료 → 스크립트가 조용히 죽던 버그 → '|| true' 로 방어.
  HEADC="$(printf '%s' "$TOP" | sed -n 's/.*[^0-9a-f]\([0-9a-f]\{7,40\}\) (\*\*보정요청\*\*).*/\1/p' || true)"
  CORR_ANS="$(printf '%s' "$TOP" | grep -oE 'A-[0-9]{4}' | head -1 || true)"
  WORKREF=""
  if [ -n "$HEADC" ]; then
    WORKREF="$(git branch -r --contains "$HEADC" 2>/dev/null | grep -oE 'origin/codex/[^ ]+' | head -1 || true)"
  else
    echo "   ⚠ handoff 줄에서 헤드 커밋 추출 실패(형식 변화 가능) — 아래 줄이 가리키는 codex 브랜치를 수동 checkout 하라."
  fi
  if [ -n "$WORKREF" ]; then
    WB="${WORKREF#origin/}"
    echo "   ▸ 작업 브랜치 자동 식별: $WB (헤드 $HEADC) → checkout"
    git checkout -q "$WB" 2>/dev/null || git checkout -q -b "$WB" "$WORKREF"
    git pull -q origin "$WB" 2>/dev/null || true
  else
    echo "   ⚠ 작업 브랜치 자동 식별 실패 — handoff 줄이 가리키는 codex 브랜치를 수동 checkout 하라(main 새 브랜치 금지)."
  fi
  if [ -n "$CORR_ANS" ]; then
    echo "   ── 보정 지시 (origin/main:collab/answers/$CORR_ANS.md) — origin/main 에서 읽음 ──"
    git show "origin/main:collab/answers/$CORR_ANS.md" 2>/dev/null | sed 's/^/   │ /'
  fi
  echo "   → 리뷰기록은 origin/main 에서 읽으면 된다(보정에 머지 불필요). base 동기화로 main 을 머지하면 collab 로그(handoff·summaries)는 append 충돌 → 양쪽 유지(union)로 해소, 코드는 보존."
  MODE="보정"
else
  echo "▶ main 최신화 (pull)..."
  git checkout main
  git pull origin main
  MODE="새태스크"
fi

echo "▶ Codex 실행 (무인: -a never -s $SANDBOX) · 모드=$MODE"
# 🔴 모드는 런처가 origin/main 기준으로 이미 판단했다. Codex 가 로컬 handoff-log 로 재판단하면
#    보정요청 브랜치의 로컬 handoff 맨 위는 'TASK-XXX done'(자기 제출)이라 '새 태스크'로 오판한다.
#    → 프롬프트를 MODE 로 분기해 못박는다(로컬 handoff 로 모드 판단 금지).
COMMON_TAIL="끝나면 COMMON-RULES §3 상세 커밋 후 collab/handoff-log.md 한 줄 + summaries/$(date +%F).md 누적 기록하고 push. 루트에 STOP 파일 있으면 즉시 중단. main 직접 push·자기 머지 금지."
if [ "$MODE" = "보정" ]; then
  PROMPT="⚠️ 지금은 '보정 재제출' 차례다(런처가 origin/main 기준으로 확정). 런처가 작업 브랜치 ${WB:-(handoff 줄의 codex 브랜치)} 를 이미 checkout 했다. \
★로컬 collab/handoff-log.md 로 모드 판단하지 마라 — 이 브랜치 로컬 handoff 맨 위는 네가 낸 'done' 이라 '새 태스크'처럼 보인다. 그건 무시하고, 보정 지시는 origin/main 에서 읽어라: 'git show origin/main:collab/answers/${CORR_ANS:-A-XXXX}.md' 와 'git show origin/main:collab/handoff-log.md' 맨 위 줄. (origin/main 머지 불필요.) \
그 R-x 지시(멱등성: 지정 커밋 재처리 금지·델타만)대로 **코드만 보정**하고 tests/run-tests.sh 전체 green 확인 후 **같은 브랜치**에 상세 커밋·push(재인계). ★새 태스크(TASK-014 등)로 넘어가지 마라. $COMMON_TAIL"
else
  PROMPT="새 태스크 차례다. START-HERE.md → COMMON-RULES.md → AGENTS.md → TASKS.md 읽고, TASKS.md 실행 순서상 다음 할 일을 확인해 오늘 날짜 브랜치(codex/$(date +%F)-<주제>)를 최신 main 기준으로 만들어 진행해. $COMMON_TAIL"
fi
exec codex --ask-for-approval never "${SBOX_ARGS[@]}" "$PROMPT"
