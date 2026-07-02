# TASKS.md — MVP-0 작업 목록 + 수용기준

> 정책면(수용기준)은 Claude 소유, 구현은 Codex 소유. Codex는 각 태스크를 자기 브랜치에서 구현하고,
> 완료 시 `collab/handoff-log.md` 에 commit hash 와 함께 남긴다. Claude 가 수용기준 대비 리뷰한다.

상태 범례: ☐ 미착수 / ◐ 진행 / ☑ 리뷰통과

---

## TASK-001 ☑ `check-change-intent` 게이트  (Codex)  — 리뷰통과 D-006 (ff75529)
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

## TASK-002 ☑ `check-sensitive-zones` 게이트  (Codex)  — 리뷰통과 D-008 (704f7a0)
**목적**: diff 가 민감 경로(zones)를 건드렸는지 level별 판정.

**입력**: diff + `policies/sensitive-zones.yaml`
**수용기준**:
1. `frozen` 닿음 → **차단**(종료코드 1), 사유에 path+reason.
2. `protected` 닿음 → **승인요구**(종료코드 2), `required_approval` 포함.
3. `watched` 닿음 → 통과하되 경고 출력(종료코드 0).
4. zones 에 안 걸리는 경로만 변경 → 통과.
5. `defaults.block_levels/approve_levels/warn_levels` 를 코드에 하드코딩하지 말고 policy 에서 읽을 것.
6. 한 변경이 여러 level 에 걸리면 **가장 강한 것**(frozen>protected>watched) 채택.

## TASK-003 ☑ `generate-change-evidence` 게이트  (Codex)  — 리뷰통과 D-009 (f2ecb50)
**목적**: 위 두 게이트 결과 + routing 으로 감사카드 생성.

**입력**: diff + TASK-001/002 결과 + `policies/approval-routing.yaml`
**출력**: `templates/change-evidence.template.yaml` 스키마의 yaml.
**수용기준**:
1. `changed_files[].zone_level`·`in_allowed_paths` 정확히 채움.
2. `verdict` = (frozen 또는 forbidden 있으면 blocked) > (protected/out_of_scope 있으면 approval_required) > pass.
3. `reviewer_required` = 닿은 영역들의 routing 결과 **중복 제거**.
4. `base_commit` 기록(멱등성). `summary` 파일/라인 수 정확.
5. 출력 yaml 이 템플릿 스키마와 키 일치(임의 키 추가 금지).

## TASK-004 ☑ 테스트 fixtures + 러너  (Codex)  — 리뷰통과 D-010 (93e2c40)
**수용기준**:
1. `tests/fixtures/` 에 최소 케이스: good(통과) / out-of-scope(승인요구) / forbidden(차단) / frozen(차단) / protected(승인요구) / watched(경고통과).
2. `tests/cases.yaml` 에 각 케이스의 gate·input·expect(pass/blocked/approval_required) 선언.
3. `tests/run-tests.sh` 로 일괄 실행, 결과 PASS/FAIL 요약. (da-review-kit 의 run-golden.sh 패턴 참고)
4. 6개 케이스 전부 기대대로.

---

# MVP-1 (Python 함수 단위) — 계획

> 목적: 경로 단위(MVP-0) → **Python 함수/클래스 단위**로 정밀화. AST로 "어느 함수가 바뀌었나"를 자동 추출하고, 민감 함수 주석·신규 능력 도입을 감지한다.
> ⚠️ MVP-0과 달리 **언어 의존(Python 우선)** + **AST 사용**. 입력은 name-status 가 아니라 **git refs(base..head)** — before/after 두 버전을 `git show` 로 파싱.
> 전체 9태스크(4단계). **Phase A(005~007)만 먼저 확정**, B/C/D 는 A 완료 후 수용기준 정밀화.

## Phase A — 함수 변경 추출 (핵심)

### TASK-005 ☑ 함수/클래스 인벤토리 추출  (Codex) — 리뷰통과·머지 (D-011)
**목적**: 단일 Python 파일을 AST 파싱해 함수/클래스 목록을 만든다.
**입력**: `.py` 파일(또는 소스 문자열)
**수용기준**:
1. 모든 함수/클래스의 **정규화 이름**(`Class.method`, 중첩 `outer.inner`)·**시작/끝 라인범위**·데코레이터 목록 추출.
2. `async def`·메서드·중첩 함수·데코레이터 함수 모두 포함.
3. 파싱 실패(문법오류) 시 **예외 없이** 빈 인벤토리 + 오류표시 반환(fail-safe).
4. 결정적 + `--json` 출력.

### TASK-006 ☑ diff 헝크 ↔ 함수 매핑  (Codex) — 리뷰통과·머지 (D-012, e5b4c2d)
**목적**: 변경된 라인범위가 **어느 함수에 속하는지** 매핑.
**입력**: `base..head` (git refs) + TASK-005 인벤토리
**수용기준**:
1. `git diff` 변경 라인범위(헝크) ↔ 함수 라인범위 **교집합**으로 "닿은 함수" 판정.
2. 한 헝크가 여러 함수에 걸치면 전부, 함수 밖(모듈 레벨) 변경은 `<module>` 로 표기.
3. after 기준 라인범위 사용(추가/삭제 오프셋 정확).
4. 결정적 + `--json`.
5. **🔴 데코레이터 줄 포함**(TASK-005 리뷰 #4): 함수 매핑 시작범위에 데코레이터 줄(`decorator_list[0].lineno ~ def`)을 포함하거나 별도 매핑. 이유: `@requires_auth`·`@app.route`·`@gov` **데코레이터만 변경**해도 해당 함수에 매핑돼야 함(미포함 시 인증·라우팅·권한 변경을 `<module>` 로 흘려 놓침). TASK-005 인벤토리의 `start_line` 은 def 줄이므로 매핑측에서 데코레이터 범위를 보정한다.

### TASK-007 ☑ before/after 함수 변경 분류  (Codex) — 재리뷰통과·머지 (D-014, impl 2243173; 1차 보정요청 D-013)
**목적**: 함수 단위로 **added/modified/deleted** 분류.
**입력**: `base..head` (양 버전 `git show`)
**수용기준**:
1. before/after 인벤토리 비교 → 함수별 `added`/`deleted`/`modified` 판정.
2. **시그니처 변경 vs 본문만 변경** 구분 표시.
3. 비-`.py`·파싱실패·신규/삭제 파일은 **파일 단위 fallback**(안전 스킵, 표시).
4. 결정적(2회 동일) + `--json`. 종료코드는 보고용(0) — 판정은 후속 게이트(Phase B).
5. **🔴 동명 함수 매칭 가드**(TASK-005 리뷰 #5): 정규화 이름은 중복 가능(`@property`/`@x.setter` 동일 `Class.x`, `@overload`, 조건부 재정의). before/after 매칭 키를 **이름 단독으로 쓰지 말고** `(정규화이름, 데코레이터셋 또는 같은 이름 내 라인순서)` 로. 이름만으로 매칭 시 setter/오버로드의 added/deleted/modified 오판.

## Phase B — 민감 함수 주석  *(A 완료 후 수용기준 확정)*
- **TASK-008** `@gov` 주석 규약+파서+검증 (Claude 설계 → Codex)
- **TASK-009** 변경함수 ↔ 주석 → level 게이트(0/1/2, policy 재사용)

## Phase C — 신규 능력 감지  *(A 완료 후)*
- **TASK-010** `sensitive-capabilities` catalog 설계 + 능력 추출 (Claude 설계 → Codex)
- **TASK-011** before/after 능력 diff → 신규 도입만 승인요구

## Phase D — 통합·테스트  *(A 완료 후)*
- **TASK-012** 감사카드 통합 (`changed_functions[]` + verdict 반영)
  - **🔴 AC 가드(TASK-006 리뷰 D-012 #1)**: 매핑/추출 게이트 출력의 `error`(top-level git 실패) 또는 파일별 `parse_error`(문법오류) 가 존재하면 **fail-closed** 로 처리(verdict = 최소 `approval_required`, 파괴적이면 `blocked`). **`files`/`changed_functions` 가 비었다고 "변경 없음(pass)" 으로 간주 금지.** 이유: TASK-006 은 보고용으로 하드 에러 시 exit 0 + `error` + `files:[]` 를 반환하므로(Phase A 설계), 통합측이 `error` 를 무시하면 git 실패가 *clean diff* 로 읽혀 민감 변경을 통째로 놓침(fail-open).
  - **🔴 AC 가드(TASK-007 리뷰 D-013 #1)**: **TASK-007 함수 분류 출력 단독으로 판정 금지.** 모듈레벨 변경(상수·import·톱레벨 문장 — 예: `ADMIN_ROLE = "user"→"admin"`)은 TASK-007 에 **아무 표식 없이 비가시**(`function_changes: []`)이므로, 반드시 TASK-006 헝크 매핑의 `<module>` touched 와 **병합**해 판정한다. 또한 `fallback: true` 파일(비-py·신규/삭제·parse_error·리네임)은 함수 단위가 안 보이므로 **파일 단위 보수 취급**(zone/intent 게이트 결과로 판정, "함수변경 0 = clean" 간주 금지).
- **TASK-013** Python before/after fixtures + 러너 확장
  - **🔴 AC 가드(TASK-007 재리뷰 D-014 #1) — 리네임 회귀 픽스처 실효화**: 현행 리네임 픽스처(`renamed_source→renamed_target`, 초소형+내용 수정)는 git 유사도 감지에 안 걸려 renames 환경에서도 D+A → **`--no-renames` 를 제거해도 스위트가 통과해 회귀를 못 잡음(실증)**. **순수 리네임(내용 동일) 쌍**을 추가하라 — 내용 동일 리네임은 크기 무관 exact-match 로 항상 R100 감지되므로(실증) 플래그 제거 회귀 시 스위트가 확실히 FAIL. 검수 시 "`--no-renames` 제거 → FAIL" 음성검증 포함.
  - **🔴 AC 가드(TASK-007 재리뷰 D-014 #2) — 파일 단위 오류 격리**: 비-UTF8 소스(`# -*- coding: latin-1 -*-` 등) `.py` M 파일 1건이 현행 classify 게이트에서 `UnicodeDecodeError` → top-level `error`+`files:[]` **전역 붕괴**(R-1 동류, 실증 — 형제 M 파일 분류 소실). 게이트(classify·map 공통)는 **파일별 예외를 해당 파일 fallback**(예: `fallback_reason: "unreadable"`)으로 격리하고 형제 파일 분류를 보존하도록 강건화 + **픽스처(비-UTF8 파일 + 동반 M 파일 → 형제 보존 기대값)** 로 고정하라. (현행은 TASK-012 fail-closed 가드로 fail-open 은 아님 — 희귀 입력이라 비차단 처리하되 여기서 명시적으로 막는다.)

## MVP-1 공통 (MVP-0 공통 규칙에 더해)
- **Python AST 허용** (MVP-0의 "AST 금지"는 MVP-0 한정). 단 LLM·추정은 여전히 금지(결정적).
- 입력은 **git refs**(before/after 필요). fixtures 도 before/after 두 버전으로.
- 2층(능력) 판정은 **자동 차단 금지 → 승인요구만** (D-004).

---

## 공통 규칙 (Codex)
- 언어: Python3 + pyyaml (기존 킷과 통일). 외부 의존 최소.
- diff 파싱: `git diff --name-status` + `--numstat` 수준이면 MVP-0 충분 (AST·내용분석 금지 = MVP-1).
- 게이트는 **결정적**: 같은 입력=같은 출력. 추정·LLM 호출 금지.
- 막히는 정책 판단은 `collab/questions/Q-XXXX.md` 로 Claude 에게.

## Claude 측 후속 (리뷰)
- 각 TASK 완료 commit 을 수용기준 대비 검수 → `collab/decisions.md` 에 "TASK-00X 리뷰통과/보정요청".
