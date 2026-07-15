#!/usr/bin/env bash
# run.sh 교차리뷰 회귀: 최종판정 조립, 분석실패, 대상 정책 override.
set -uo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
PASS=0; TOTAL=0

make_repo(){
  local repo="$1"
  mkdir -p "$repo/app" "$repo/custom/crown" "$repo/policies"
  git -C "$repo" init -q
  git -C "$repo" config user.email kit-test@example.invalid
  git -C "$repo" config user.name kit-test
  cp "$KIT/policies/"*.yaml "$repo/policies/"
  cat >"$repo/change-intent.yaml" <<'YAML'
change_intent:
  requirement_id: KIT-TEST
  purpose: run.sh adversarial verification
  author: test
  allowed_paths: ["app/**", "custom/**", "policies/**"]
  forbidden_paths: []
YAML
  printf 'def stable():\n    return True\n' >"$repo/app/service.py"
  git -C "$repo" add . && git -C "$repo" commit -qm base
}

run_case(){
  local name="$1" expected_rc="$2" expected_text="$3" runner="$4" repo="$5"; shift 5
  local output rc
  TOTAL=$((TOTAL + 1))
  output="$(ACGH_GATE_TIMEOUT_SECONDS=1 bash "$runner" HEAD~1..HEAD --repo "$repo" "$@" 2>&1)"; rc=$?
  if [ "$rc" = "$expected_rc" ] && printf '%s\n' "$output" | grep -q -- "$expected_text"; then
    echo "PASS $name"; PASS=$((PASS + 1))
  else
    echo "FAIL $name (exit=$rc expected=$expected_rc, missing=$expected_text)"
    printf '%s\n' "$output" | tail -12 | sed 's/^/  /'
  fi
}

# 실제 차단이 승인요구보다 강하게 조립되는지 + 대상 repo 정책 override.
repo="$WORK/frozen"; make_repo "$repo"
cat >"$repo/policies/sensitive-zones.yaml" <<'YAML'
policy_version: test
defaults:
  block_levels: [frozen]
  approve_levels: [protected]
  warn_levels: [watched]
  unlisted_level: free
zones:
  - path: "custom/crown/**"
    level: frozen
    reason: target repository crown jewel
    required_approval: [human-owner]
YAML
printf 'def settle():\n    return 0\n' >"$repo/custom/crown/ledger.py"
git -C "$repo" add . && git -C "$repo" commit -qm frozen
run_case target-policy-frozen 1 'BLOCKED' "$KIT/run.sh" "$repo" --policies "$repo/policies"

# 신규 능력은 카드가 pass여도 최종 승인요구여야 한다.
repo="$WORK/capability"; make_repo "$repo"
printf 'import subprocess\n\ndef run():\n    return subprocess.run(["true"])\n' >"$repo/app/service.py"
git -C "$repo" add . && git -C "$repo" commit -qm capability
run_case new-capability 2 'APPROVAL_REQUIRED' "$KIT/run.sh" "$repo"

# 정책 규칙 삭제는 메타 게이트가 승인요구로 올린다.
repo="$WORK/policy"; make_repo "$repo"
python3 - "$repo/policies/sensitive-zones.yaml" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
text = p.read_text()
marker = text.find("zones:")
p.write_text(text[:marker] + "zones: []\n")
PY
git -C "$repo" add . && git -C "$repo" commit -qm loosen
run_case policy-loosening 2 'APPROVAL_REQUIRED' "$KIT/run.sh" "$repo"

# 게이트 삭제와 timeout은 정상 판정 exit로 위장되지 않아야 한다.
broken="$WORK/kit-missing"; cp -R "$KIT" "$broken"; rm "$broken/gates/check-new-capabilities.py"
repo="$WORK/missing"; make_repo "$repo"
printf 'def changed():\n    return 1\n' >>"$repo/app/service.py"
git -C "$repo" add . && git -C "$repo" commit -qm changed
run_case missing-gate 2 '분석 실패: check-new-capabilities' "$broken/run.sh" "$repo"

slow="$WORK/kit-timeout"; cp -R "$KIT" "$slow"
cat >"$slow/gates/check-new-capabilities.py" <<'PY'
import time
time.sleep(5)
PY
run_case gate-timeout 2 'timeout' "$slow/run.sh" "$repo"

echo "Entrypoint summary: $PASS/$TOTAL PASS"
[ "$PASS" = "$TOTAL" ]
