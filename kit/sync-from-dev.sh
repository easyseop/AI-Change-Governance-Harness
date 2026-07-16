#!/usr/bin/env bash
# =====================================================================
# sync-from-dev.sh — 개발 저장소 → 키트 재생성 (★MVP 완료마다 실행)
# =====================================================================
# 키트(kit/)는 개발 저장소의 "배포 가능한 스냅샷"이다. 게이트·정책·템플릿·
# 테스트를 dev 원본에서 복사해 키트를 완료 MVP 상태와 동기화한다.
#
# ★게이트는 서로를 같은 디렉토리에서 import 한다(각 게이트의
#   GATE_DIR = Path(__file__).resolve().parent · load_gate_module()).
#   따라서 전 게이트를 kit/gates/ 에 **co-located** 로 복사해야 하며,
#   하나라도 빠지면 함수-거버넌스·능력 게이트의 내부 import 가 깨진다.
#   → 이 스크립트는 끝에서 dev 게이트 수 == kit 게이트 수를 검증한다(누락 방지).
#
# 사용:  ./kit/sync-from-dev.sh      (kit 폴더 위치 기준으로 dev 루트 자동 유도)
# =====================================================================
set -euo pipefail
KIT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEV_ROOT="$(cd "$KIT_DIR/.." && pwd)"

echo "▶ 동기화: dev=$DEV_ROOT → kit=$KIT_DIR"

# 1) 게이트 전체 (16종 + gates/README) — co-located 필수
rm -rf "$KIT_DIR/gates"; mkdir -p "$KIT_DIR/gates"
cp "$DEV_ROOT"/.harness/gates/*.py "$KIT_DIR/gates/"
[ -f "$DEV_ROOT/.harness/gates/README.md" ] && cp "$DEV_ROOT/.harness/gates/README.md" "$KIT_DIR/gates/"

# 2) 정책 (sensitive-zones·sensitive-capabilities·approval-routing·change-intent 템플릿류)
SINK_REGISTRY_SNAPSHOT="$(mktemp)"
[ -f "$KIT_DIR/policies/sink-registry.yaml" ] && cp "$KIT_DIR/policies/sink-registry.yaml" "$SINK_REGISTRY_SNAPSHOT"
rm -rf "$KIT_DIR/policies"; mkdir -p "$KIT_DIR/policies"
cp "$DEV_ROOT"/policies/*.yaml "$KIT_DIR/policies/"
# TASK-022 확정 정책의 dev 원본이 아직 없으면 현재 킷 기본본을 보존한다(Q-0004).
if [ ! -f "$KIT_DIR/policies/sink-registry.yaml" ] && [ -s "$SINK_REGISTRY_SNAPSHOT" ]; then
  cp "$SINK_REGISTRY_SNAPSHOT" "$KIT_DIR/policies/sink-registry.yaml"
fi
rm -f "$SINK_REGISTRY_SNAPSHOT"

# 3) 감사카드 템플릿
rm -rf "$KIT_DIR/templates"; mkdir -p "$KIT_DIR/templates"
cp "$DEV_ROOT"/templates/*.yaml "$KIT_DIR/templates/"

# 4) 테스트(자체검증 selftest.sh 용) — 러너·뮤테이션·케이스·픽스처
ENTRYPOINT_TEST_SNAPSHOT="$(mktemp)"
[ -f "$KIT_DIR/tests/run-entrypoint-tests.sh" ] && cp "$KIT_DIR/tests/run-entrypoint-tests.sh" "$ENTRYPOINT_TEST_SNAPSHOT"
rm -rf "$KIT_DIR/tests"; mkdir -p "$KIT_DIR/tests"
cp -r "$DEV_ROOT"/tests/. "$KIT_DIR/tests/"
# 킷 진입점 전용 적대검증은 dev 테스트에 없으므로 동기화에서도 보존한다.
if [ -s "$ENTRYPOINT_TEST_SNAPSHOT" ]; then
  cp "$ENTRYPOINT_TEST_SNAPSHOT" "$KIT_DIR/tests/run-entrypoint-tests.sh"
  chmod +x "$KIT_DIR/tests/run-entrypoint-tests.sh"
fi
rm -f "$ENTRYPOINT_TEST_SNAPSHOT"

# 5) ★누락 검증 — dev 게이트 수와 kit 게이트 수 일치 확인
DEV_N=$(ls "$DEV_ROOT"/.harness/gates/*.py 2>/dev/null | wc -l | tr -d ' ')
KIT_N=$(ls "$KIT_DIR"/gates/*.py 2>/dev/null | wc -l | tr -d ' ')
echo "  게이트 수: dev=$DEV_N  kit=$KIT_N"
if [ "$DEV_N" != "$KIT_N" ]; then
  echo "✗ 게이트 수 불일치 — 누락 발생! 동기화 실패."; exit 1
fi
echo "✓ 동기화 완료 — 게이트 $KIT_N 종 전부 반영 (누락 0)"
echo "  다음: ./kit/run.sh <base>..<head> --repo <대상>  또는  ./kit/selftest.sh"
