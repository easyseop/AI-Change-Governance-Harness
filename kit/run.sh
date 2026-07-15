#!/usr/bin/env bash
# =====================================================================
# run.sh — 변경 거버넌스 러너 (키트 진입점 · spine verify hook)
# =====================================================================
# 전 런타임 게이트를 결정적으로 순서 실행 → 감사카드 1장 + 최종 판정.
# 판정에 LLM 없음. 같은 입력이면 항상 같은 결과(결정론).
#
# ★조립 대상(누락 없이):
#   [1층] 의도이탈 + 민감경로 + @gov 함수      → generate-change-evidence 가 3축 조립 + 카드
#   [2층] 신규 위험능력                          → check-new-capabilities (카드 밖 — 여기서 명시 추가)
#   [메타] 정책 자기무력화                        → check-policy-change    (카드 밖 — 여기서 명시 추가)
#   최종 = 세 결과의 가장 센 판정(차단 > 승인 > 통과).
#
# 사용:  ./run.sh <base>..<head> [--repo <대상repo>] [--output <카드경로>]
# 종료코드: 0 통과 / 1 차단 / 2 승인필요
# =====================================================================
set -uo pipefail
KIT="$(cd "$(dirname "$0")" && pwd)"
G="$KIT/gates"
POL="$KIT/policies"
ZONES="$POL/sensitive-zones.yaml"
CAPS="$POL/sensitive-capabilities.yaml"
ROUTING="$POL/approval-routing.yaml"

RANGE="${1:?사용: ./run.sh <base>..<head> [--repo <repo>] [--output <카드>]}"; shift
REPO="."; OUT="change-evidence.yaml"
while [ $# -gt 0 ]; do case "$1" in
  --repo)   REPO="$2"; shift 2;;
  --output) OUT="$2"; shift 2;;
  *) echo "알 수 없는 인자: $1"; exit 64;;
esac; done

# base..head 범위여야 함수·능력·정책 게이트가 돈다(git 두 ref 필요).
HAS_RANGE=0; case "$RANGE" in *..*) HAS_RANGE=1;; esac

cd "$REPO" || { echo "✗ 대상 repo 없음: $REPO"; exit 66; }
INTENT=""; [ -f change-intent.yaml ] && INTENT="change-intent.yaml"

hr(){ printf '─%.0s' $(seq 1 66); echo; }
echo "════════════════════════════════════════════════════════════════"
echo "  변경 감사카드 · AI Change Governance Kit"
echo "════════════════════════════════════════════════════════════════"
echo "  대상 repo : $(basename "$(pwd)")"
echo "  변경 범위 : $RANGE"
[ -n "$INTENT" ] || echo "  (change-intent.yaml 없음 — 의도이탈 층은 생략)"
hr

# ── 감사카드 + 3축(의도·민감경로·@gov 함수) 판정 ────────────────────
INTENT_ARGS=(); [ -n "$INTENT" ] && INTENT_ARGS=(--change-intent "$INTENT")
CARD="$(python3 "$G/generate-change-evidence.py" "$RANGE" \
          --sensitive-zones "$ZONES" --approval-routing "$ROUTING" \
          "${INTENT_ARGS[@]}" --repo . 2>&1)"; ge_exit=$?
printf '%s\n' "$CARD" > "$OUT"
echo "▸ [1층] 의도이탈·민감경로·@gov 함수 (감사카드 3축)"
printf '%s\n' "$CARD" | grep -E 'verdict:|status:|frozen_touched|protected_touched|out_of_scope|forbidden_touched|reviewer_required' | sed 's/^/    /' | head -20

# ── [2층] 신규 위험 능력 (감사카드에 미포함 → 여기서 명시 조립) ─────
cap_exit=0
echo "▸ [2층] 신규 위험 능력 (외부호출·암복호·실행 등 신규 도입?)"
if [ "$HAS_RANGE" = 1 ]; then
  CAP_OUT="$(python3 "$G/check-new-capabilities.py" "$RANGE" "$CAPS" --repo . 2>&1)"; cap_exit=$?
  printf '%s\n' "$CAP_OUT" | head -6 | sed 's/^/    /'
else
  echo "    (base..head 범위 아님 — 능력 층 생략·coverage 갭)"
fi

# ── [메타] 정책 자기무력화 (감사카드에 미포함 → 여기서 명시 조립) ───
pol_exit=0
echo "▸ [메타] 정책 자기무력화 (게이트/정책 완화·집행우회?)"
if [ "$HAS_RANGE" = 1 ]; then
  POL_OUT="$(python3 "$G/check-policy-change.py" "$RANGE" --repo . 2>&1)"; pol_exit=$?
  printf '%s\n' "$POL_OUT" | head -6 | sed 's/^/    /'
else
  echo "    (base..head 범위 아님 — 정책변경 층 생략·coverage 갭)"
fi

# ── 최종 판정 = 가장 센 것 (차단 1 > 승인 2 > 통과 0) ────────────────
final=0; label="🟢 PASS (통과)"
if [ "$ge_exit" = 1 ] || [ "$cap_exit" = 1 ] || [ "$pol_exit" = 1 ]; then
  final=1; label="🔴 BLOCKED (차단)"
elif [ "$ge_exit" = 2 ] || [ "$cap_exit" = 2 ] || [ "$pol_exit" = 2 ]; then
  final=2; label="🟠 APPROVAL_REQUIRED (승인필요)"
fi

hr
echo "  게이트 판정 : 카드3축=$ge_exit · 능력=$cap_exit · 정책=$pol_exit  (0통과/1차단/2승인)"
echo "  최종 판정   : $label   (exit $final)"
echo "  감사카드    : $OUT"
echo "════════════════════════════════════════════════════════════════"
exit $final
