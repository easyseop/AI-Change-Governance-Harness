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

## Phase B — 민감 함수 주석  *(수용기준 확정 — D-017)*

### TASK-008 ☑ `@gov` 주석 규약+파서+검증  — 보정 재리뷰통과·머지 (D-019, 보정 2272a47; 1차 보정요청 D-018 `collab/answers/A-0004.md`)
**설계 계약(전문): `collab/answers/A-0003.md` (Q-0001 답변, D-017)** — 문법·필드·검증·스키마는 계약이 정본.
**목적**: 코드에 사람이 선언한 `@gov(...)` / `__gov__` 민감도 주석을 AST 로 결정적 추출·검증.
**산출**: `.harness/gates/extract-gov-annotations.py` — **별도 게이트**(TASK-005 인벤토리 스키마 확장 금지), 보고 전용 exit 0.
**수용기준**(A-0003 §Q7 = 리뷰 체크리스트):
1. 데코레이터 `@gov(level=, reason=, [owner=])`(keyword·문자열 리터럴만) + 모듈 `__gov__` 리터럴 dict — 일반/async/메서드/중첩 전부 파싱.
2. **🔴 엄격 승계(stricter-wins)**: effective_level = max(자기, 둘러싼 class/def, 모듈) — 내부 주석으로 레벨 **하향 불가**(frozen 클래스 안 watched 메서드 → effective frozen) 픽스처 실증.
3. **🔴 고정 적대 세트**(상설 회귀 픽스처): setter 에만 `@gov`(getter/setter 동명 — `order_key` 부착 정확) · `@overload` · 조건부/중첩 def.
4. 검증오류 각 1+ 케이스: `invalid_level`·`unresolved`(비-리터럴)·`duplicate`(가장 엄한 level 채택)·`missing_reason`·`unknown_field`·positional — **전부 기록·보수 취급**(silent pass 금지, invalid → protected 보수 기본).
5. fail-safe: 문법오류 → `parse_error`·비-UTF8 → `unreadable` **파일 단위 격리**(형제 보존, exit 0 — TASK-013 계보).
6. 결정성(md5 2회 동일) + `--json` + 음성검증 가능(기대 변조→FAIL).
7. **🔴 AC 가드(D-018 R-1) — 동일 주석 내 중복 필드 strongest-wins**: `@gov(level="frozen", level="watched")`(`ast.parse` 는 중복 keyword 를 안 거름 — compile 단계만 SyntaxError, 실증)·`__gov__ = {"level":"frozen","level":"watched"}`(dict 중복 키는 합법 실행 코드) 모두 **last-wins 금지** — 오류 기록(`duplicate`/`invalid_module_gov`) + level 은 유효값 중 가장 엄한 것 채택. 픽스처 2건 + "strongest-wins 제거→FAIL" 음성검증.
8. **🔴 AC 가드(D-018 R-2) — `__gov__` 비정식 형태 silent drop 금지**(A-0004 로 A-0003 개정): ① 값 있는 톱레벨 `AnnAssign`(`__gov__: dict = {...}`) 은 **정식 인정**(Assign 동일 처리) ② 그 외 위치/형태의 `__gov__` 바인딩(if 안·클래스 본문·AugAssign·다중 타겟)은 발견 시 `invalid_module_gov` 기록 + protected 보수 취급(무기록 무시 금지). 각 픽스처 + 음성검증.

### TASK-009 ☑ 변경함수 ↔ 주석 → level 게이트 (0/1/2, policy 재사용) — 보정 재리뷰통과·머지 (D-021, 보정 aacdfe9; 1차 보정요청 D-020 `collab/answers/A-0005.md`)
**판정**: 변경 함수(TASK-006 매핑 ∪ TASK-007 분류, `<module>` 포함)의 effective level → `frozen=blocked(1)` / `protected=approval_required(2)` / `watched=경고 pass(0)`. 어휘·의미는 `sensitive-zones.yaml` 재사용. (층 분류: `@gov` = 선언적 1층 — D-017, frozen 차단은 D-004 와 모순 없음.)
- **🔴 AC 가드(D-017 #1) — 주석 제거 우회 방지**: 판정은 **base ∪ head 양측 주석의 max**. 같은 PR 에서 `@gov(frozen)` 삭제+본문 수정 시 head 만 보면 무주석 → base 측이 지배해야 우회 차단. 주석 *제거 자체*도 해당 레벨 변경으로 취급. 리뷰 시 "주석 삭제 PR" fresh 시나리오로 실증.
- **🔴 AC 가드(D-017 #2) — fail-closed 연동**: base 에 frozen/protected 주석 있던 파일이 head 에서 `parse_error`/`unreadable` → 최소 `approval_required` (TASK-012 "빈 결과 ≠ clean" 가드와 정합).
- 변경 함수에 invalid/`unresolved` 주석 → 최소 `approval_required` (조용히 pass 금지). errors 비어있지 않은 주석(`duplicate` 포함)도 동일 취급.
- **join 키 주의(D-018 관찰 #5)**: TASK-008 `order_key`(같은 이름 내 전 def 등장순서)와 TASK-007 `_match_key` occurrence(`(이름, 데코셋)` 내 순서)는 **동일하지 않다**(setter 실측: 전자 1, 후자 0). order_key 끼리 join 금지 — **`(path, name, TASK-008 def_line ↔ TASK-007 after start_line)`** 으로 join 한다.
- **🔴 AC 가드(D-020/A-0005) — 분석-불능 파일 per-path fail-closed (동반 레코드에 꺼지면 안 됨)**: ① head 에 **존재하는** 변경 `.py` 가 `parse_error`/`unreadable` → **다른 레코드 유무와 무관하게** 그 파일에 fail-closed 레코드(base 민감 시 base 최강 레벨, 아니면 `protected`) — 전역 "errors 있고 records 없을 때만" 조건 금지(watched 1건 동반으로 pass 세탁 실증). ② base 에 **존재했던** 변경 `.py` 의 base 측 불능(head 가독 여부 무관) → 최소 `protected` fail-closed(base 주석 은닉 → head 재인코딩·주석 제거 세탁 실증). ③ head **부재**(삭제/리네임 소스)는 구분: base 가독·비민감 → 통과 허용(과차단 방지), base 가독·민감 → base 최강 레벨(D-017 #2), base 불능 → `protected`. 존재/부재 판별은 결정적으로(에러 메시지 문자열 파싱 금지). ④ map/classify top-level `error` → records 유무 무관 최소 `approval_required`. 회귀 픽스처: unreadable-head/base-laundering(watched 동반 → approval)·plain-delete-pass + "fail-closed 무력화 → FAIL" 음성검증.

## Phase C — 신규 능력 감지  *(A 완료 후)*  *(설계 확정: `docs/capability-catalog-design.md`, D-022)*
> **2층 불변식(D-004·설계 §3)**: 능력 감지는 **추론** → **절대 blocked 금지, `approval_required` 가 상한**. catalog `level ∈ {protected, watched}`, `frozen` 오면 검증오류+protected clamp.

### TASK-010 ☑ `sensitive-capabilities` catalog + 능력 추출기 `extract-python-capabilities.py`  *(Claude 설계 완료 → Codex)* — 리뷰통과 D-024 (1ed4222)
**판정**: 단일 `.py` → 카탈로그(`policies/sensitive-capabilities.yaml`) 신호로 파일의 민감 **능력 집합** 추출. **보고 전용·exit 0**(판정 없음 — TASK-008 대응). 계약 전문: `docs/capability-catalog-design.md`.
- **신호 3종**: `imports`(모듈 import 자체가 신호) / `calls`(별칭·from-import 해소한 점표기 전체이름 일치) / `builtins`(무-import 내장 `eval`/`exec` 등).
- **🔴 AC 가드 — import-레벨 backstop**: 호출 해석은 별칭·`getattr`·재대입으로 우회 가능 → **import 신호가 최종 방어선**. `os` 등 흔한 모듈은 import 무신호(특정 호출만), `subprocess`·`pickle`·`requests` 등은 import 자체가 신호.
- **🔴 AC 가드 — 고정 적대(우회) 세트 상설 픽스처**(§2B, 계약 Q4): ① `import subprocess as sp` 별칭 ② `from subprocess import run as r` from-별칭 ③ `from subprocess import *` star-import ④ `getattr(subprocess,"run")` 동적접근(import backstop) ⑤ `__import__("subprocess")`(→dynamic_code_exec) ⑥ 무-import `exec`/`eval` ⑦ 함수 내부 import(walk 전수). 각 "신호 제거→미감지 FAIL" 음성검증.
- 값 추정 금지(`yaml.load` 는 항상 신호·`open` 쓰기판별 제외), 파일 단위 fail-safe(parse_error/unreadable 격리·형제 보존·exit 0), 결정성 md5.
- 출력: `{path, capabilities:[{id,level,signals:[{kind,name,line}]}], unresolved_dynamic, errors, parse_error, unreadable}`. TASK-005 인벤토리 스키마 확장 금지(별도 게이트).

### TASK-011 ☑ before/after 능력 diff `check-new-capabilities.py` → 신규 도입만 승인요구  *(TASK-010 후)* — 리뷰통과 D-025 (1aa88d8·헤드 c3425cf)
**판정**: `base..head` → 파일별 **`head − base` 신규 능력**만 verdict. 능력 *제거*는 안전(경고 안 함), *신규 도입*만 approval. (TASK-009 의 `base∪head max` 와 **정반대** — 주의.)
- **🔴 AC 가드 — 신규만(계약 Q5)**: 능력 id 가 base·head **양쪽**이면 미감지 / head 만이면 감지 / 신규 파일(base 부재)→능력 전부 신규 / 삭제 파일(head 부재)→신규 없음. **음성검증**: base 무시 head-only 로 바꾸면 이미-있던 능력 오검출→FAIL(base∪head 아님을 고정). 판정 단위=파일별 능력 id 집합(형 override 가능).
- **🔴 AC 가드 — never-blocked 불변식(계약 Q2)**: verdict 는 `approval_required(2)` 상한 / watched 만이면 경고+`pass(0)` / 없으면 pass. **`blocked`·exit 1 절대 없음.** 음성검증: catalog 에 `frozen` 넣어도 protected clamp(clamp 제거 시 blocked → FAIL 로 잡히게).
- **🔴 AC 가드 — fail-closed(계약 Q6, A-0005 교훈)**: head 존재+`parse_error`/`unreadable` 변경 `.py` → **다른 결과 유무 무관** per-path `approval_required`(전역 "errors and not records" 조건 **금지** — D-020 세탁 재발 방지). base 존재+불능 → `base_caps` 빈 집합(head 능력 신규화 approval). 존재/부재는 `git cat-file -e` 결정적(문자열 파싱 금지). upstream error → records 무관 최소 approval. 회귀 픽스처 `new-cap-unreadable-head`(신규 불능+무관 동반→approval) + "fail-closed 무력화→FAIL" 음성검증.
- 출력: `{gate,verdict,new_capabilities:[{path,id,level,reason,reviewer,signals}],warned_capabilities,fail_closed,errors,exit_code}`.
- **하류(TASK-012)**: `errors`/`fail_closed` 비면 아님 → 통합측 최소 approval(D-021 원칙). 능력 게이트는 `@gov`·zone 과 독립, TASK-012 가 병합.
- **🟠 AC 가드 — call-only 모듈 동적 우회(D-024 리뷰 발견, 비차단→차기 가드)**: TASK-010 추출기는 `imports` 목록 밖 **call-only 모듈**(예: `os` — 잡음 이유로 import 무신호)에 대해 `getattr(os,"system")(cmd)`·재대입 별칭(`z=os; z.system()`)을 **놓친다**(import backstop 부재). 직접 `os.system(cmd)`·`import os as o; o.system()` 은 잡힘. 계약 Q4 세트(subprocess 기반)는 전부 잡히므로 **비차단**이나, 능력 도입 은닉 경로다. TASK-011/추출기 강화 시: `getattr(<바인딩된-모듈>, "<문자열 리터럴>")(...)` 를 점표기 호출로 해소해 call-only 모듈 동적 우회를 닫거나, catalog 에 문서화된 수용 잔여로 명시. (참고: subprocess 등 import-신호 모듈은 이미 backstop 으로 커버 — 주 실행 벡터는 안전.)
  - **[D-025 검수 결과]** 위 🟠 가드가 명시한 **두 형태(인라인 `getattr(os,"system")(cmd)` + 재대입 `z=os; z.system()`)는 둘 다 폐쇄·회귀픽스처(`valid.py`) 완료 = AC 충족.** ☑
- **🟠 AC 가드 — 분리대입 getattr 잔여(D-025 리뷰 신규 발견, 비차단→차기 가드)**: D-024 폐쇄 후에도 **제3 변형** `fn = getattr(os,"system"); fn(c)` (getattr 결과를 변수에 담아 별도 호출)는 call-only 모듈(os 계열)에서 **여전히 미감지**(fresh 실증: `caps=[]`·`unresolved_dynamic` 마커 전무). 원인: `build_import_bindings` 의 `ast.Assign` 핸들러가 value=`getattr(...)`(Call)을 `dotted_name` 로 해소 못 해 `fn` 미바인딩. import-신호 모듈(주 실행벡터)은 backstop 으로 무영향·2층 approval 상한이라 비차단이나 능력 은닉 잔여. 추출기 강화 시: `<var> = getattr(<모듈>,"<리터럴>")` 를 바인딩표에 callable 로 전파해 후속 `<var>(...)` 호출을 해소하거나, **catalog 에 문서화된 수용 잔여로 명시**. (참고: 완전폐쇄엔 지역 dataflow 추적 필요 — §2B 대규모 리팩터 강요 금지 하에 차기 가드로 이월.)
  - **[D-026 검수 결과]** 위 가드가 요구한 `<var> = getattr(<모듈>,"<리터럴>")` 바인딩 전파를 **구현·폐쇄**(impl `b6cc23d`, `Assign` 핸들러가 `resolve_getattr_call_name` 우선 시도). 회귀 픽스처(`valid.py`·하류 `new-capabilities/getattr-assignment/`) + 음성검증(rig→37/39) 실증 = **plain 형태 AC 충족.** ☑
- **🟠 AC 가드 — 별칭 base + getattr 삼중난독 잔여(D-026 리뷰 신규 발견, 비차단→차기 가드)**: 분리대입 getattr 폐쇄 후에도 **더 좁은 하위변형** `import os as o; fn = getattr(o,"system"); fn(c)` (별칭 base + getattr + 분리대입)는 **여전히 미감지**(fresh 실증 [B]). 원인: `Assign` 핸들러가 `resolve_getattr_call_name` 이 이미 `o→os` 해소해 반환한 `os.system` 을 **다시 partition** 해 root `os` 를 bindings 에서 찾는데 바인딩된 건 별칭 `o` 뿐 → `root not in bindings → continue`(이중 해소 결함). 직접 별칭 호출 `o.system()` 은 정상 감지. import-신호 모듈은 backstop 무영향·2층 approval 상한 → 비차단. **추출기 강화 시**: getattr 경로가 잡히면 값이 이미 완전 해소돼 있으므로 `Assign` 핸들러에서 **재-partition 없이 그대로 `target` 으로 사용**(≈3줄)하면 별칭 base 도 무료 폐쇄, 또는 **catalog 문서화 수용잔여로 명시**. (§2B 대규모 리팩터 강요 금지 하에 차기 가드로 이월.)

## Phase D — 통합·테스트  *(A 완료 후)*
- **TASK-012** ☑ 감사카드 통합 (`changed_functions[]` + verdict 반영) — 리뷰통과·머지 (D-023, impl 81147f5). 경로-clean + 함수-frozen → blocked 격리 실증·parse_error→approval fail-closed·음성검증 3종. 비차단 관찰 4건(errors 분기 중복방어 미테스트·name-status 입력 함수분석 스킵[git-ref 필수 문서권고]·예외→blocked·changed_functions 중복표기) → `review-notes.md`.
  - **🔴 AC 가드(TASK-006 리뷰 D-012 #1)**: 매핑/추출 게이트 출력의 `error`(top-level git 실패) 또는 파일별 `parse_error`(문법오류) 가 존재하면 **fail-closed** 로 처리(verdict = 최소 `approval_required`, 파괴적이면 `blocked`). **`files`/`changed_functions` 가 비었다고 "변경 없음(pass)" 으로 간주 금지.** 이유: TASK-006 은 보고용으로 하드 에러 시 exit 0 + `error` + `files:[]` 를 반환하므로(Phase A 설계), 통합측이 `error` 를 무시하면 git 실패가 *clean diff* 로 읽혀 민감 변경을 통째로 놓침(fail-open). **보강(TASK-013 재리뷰 D-016)**: map 출력에서 `parse_error` 파일이 헝크 부재(git 바이너리 취급 — NUL 바이트 `.py` 실증)로 `touched_functions: []` 일 수 있다 — **빈 `touched_functions` ≠ clean**, `parse_error` 가 있으면 `<module>` touched 와 동등하게 보수 취급하라. **보강(TASK-009 재리뷰 D-021)**: TASK-009 `check-function-gov-level` 출력의 `errors` 가 비어있지 않으면 통합측도 **최소 `approval_required`** 로 취급(게이트 자체 fail-closed 의 중복 방어선 — R-1 류 재발 대비). 상류 top-level error 주입 픽스처(TASK-009 AC ④ 회귀 가드)도 이 태스크에서 추가 검토.
  - **🔴 AC 가드(TASK-007 리뷰 D-013 #1)**: **TASK-007 함수 분류 출력 단독으로 판정 금지.** 모듈레벨 변경(상수·import·톱레벨 문장 — 예: `ADMIN_ROLE = "user"→"admin"`)은 TASK-007 에 **아무 표식 없이 비가시**(`function_changes: []`)이므로, 반드시 TASK-006 헝크 매핑의 `<module>` touched 와 **병합**해 판정한다. 또한 `fallback: true` 파일(비-py·신규/삭제·parse_error·리네임)은 함수 단위가 안 보이므로 **파일 단위 보수 취급**(zone/intent 게이트 결과로 판정, "함수변경 0 = clean" 간주 금지).
- **TASK-013** ☑ Python before/after fixtures + 러너 확장 — 재리뷰통과·머지 (D-016, impl 0aaadcc; 1차 보정요청 D-015)
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
