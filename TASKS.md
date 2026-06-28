# TASKS.md — MVP-0 작업 목록 + 수용기준

> 정책면(수용기준)은 Claude 소유, 구현은 Codex 소유. Codex는 각 태스크를 자기 브랜치에서 구현하고,
> 완료 시 `collab/handoff-log.md` 에 commit hash 와 함께 남긴다. Claude 가 수용기준 대비 리뷰한다.

상태 범례: ☐ 미착수 / ◐ 진행 / ☑ 리뷰통과

---

## TASK-001 ☐ `check-change-intent` 게이트  (Codex)
**목적**: diff 가 change-intent 의 의도 범위를 벗어났는지 결정적 감지.

**입력**: `<diff 경로 또는 git ref>` + `change-intent.yaml`
**출력**: 텍스트 결과 + 종료코드. 선택 `--json` 으로 구조화.

**수용기준 (Claude 검수 체크리스트)**:
1. change-intent.yaml 없으면 **실패(비통과)** 하고 "의도 선언 누락" 안내.
2. diff 의 변경 파일이 `allowed_paths` glob 안에만 있으면 통과.
3. `allowed_paths` 밖 파일 변경 → `out_of_scope` 로 보고 (종료코드 2, 승인필요).
4. `forbidden_paths` 안 파일 변경 → **차단**(종료코드 1).
5. glob 매칭은 `**`(다단계)·`*`(단일단계) 지원. 경로 구분자 OS 무관.
6. 변경 0건이면 통과(빈 diff 안전).

## TASK-002 ☐ `check-sensitive-zones` 게이트  (Codex)
**목적**: diff 가 민감 경로(zones)를 건드렸는지 level별 판정.

**입력**: diff + `policies/sensitive-zones.yaml`
**수용기준**:
1. `frozen` 닿음 → **차단**(종료코드 1), 사유에 path+reason.
2. `protected` 닿음 → **승인요구**(종료코드 2), `required_approval` 포함.
3. `watched` 닿음 → 통과하되 경고 출력(종료코드 0).
4. zones 에 안 걸리는 경로만 변경 → 통과.
5. `defaults.block_levels/approve_levels/warn_levels` 를 코드에 하드코딩하지 말고 policy 에서 읽을 것.
6. 한 변경이 여러 level 에 걸리면 **가장 강한 것**(frozen>protected>watched) 채택.

## TASK-003 ☐ `generate-change-evidence` 게이트  (Codex)
**목적**: 위 두 게이트 결과 + routing 으로 감사카드 생성.

**입력**: diff + TASK-001/002 결과 + `policies/approval-routing.yaml`
**출력**: `templates/change-evidence.template.yaml` 스키마의 yaml.
**수용기준**:
1. `changed_files[].zone_level`·`in_allowed_paths` 정확히 채움.
2. `verdict` = (frozen 또는 forbidden 있으면 blocked) > (protected/out_of_scope 있으면 approval_required) > pass.
3. `reviewer_required` = 닿은 영역들의 routing 결과 **중복 제거**.
4. `base_commit` 기록(멱등성). `summary` 파일/라인 수 정확.
5. 출력 yaml 이 템플릿 스키마와 키 일치(임의 키 추가 금지).

## TASK-004 ☐ 테스트 fixtures + 러너  (Codex)
**수용기준**:
1. `tests/fixtures/` 에 최소 케이스: good(통과) / out-of-scope(승인요구) / forbidden(차단) / frozen(차단) / protected(승인요구) / watched(경고통과).
2. `tests/cases.yaml` 에 각 케이스의 gate·input·expect(pass/blocked/approval_required) 선언.
3. `tests/run-tests.sh` 로 일괄 실행, 결과 PASS/FAIL 요약. (da-review-kit 의 run-golden.sh 패턴 참고)
4. 6개 케이스 전부 기대대로.

---

## 공통 규칙 (Codex)
- 언어: Python3 + pyyaml (기존 킷과 통일). 외부 의존 최소.
- diff 파싱: `git diff --name-status` + `--numstat` 수준이면 MVP-0 충분 (AST·내용분석 금지 = MVP-1).
- 게이트는 **결정적**: 같은 입력=같은 출력. 추정·LLM 호출 금지.
- 막히는 정책 판단은 `collab/questions/Q-XXXX.md` 로 Claude 에게.

## Claude 측 후속 (리뷰)
- 각 TASK 완료 commit 을 수용기준 대비 검수 → `collab/decisions.md` 에 "TASK-00X 리뷰통과/보정요청".
