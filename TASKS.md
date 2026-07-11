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
  - **[D-027 검수 결과]** 위 가드가 제시한 **재-partition 없이 그대로 `target` 사용**을 **구현·폐쇄**(impl `27716df`, `Assign` 핸들러가 `resolve_getattr_call_name(..., require_bound_base=True)` 로 이미 완전 해소된 값을 그대로 전파). 하류 회귀 픽스처(`new-capabilities/getattr-assignment-alias/` — 형제 `import os` 오염 없는 모듈레벨 `import os as o` 단독) + 음성검증(rig→39/40 FAIL·원복 40/40) 실증 = **AC 충족.** ☑ 잔여(더 깊은 변형)는 아래 참조.
- **🟠 AC 가드 — getattr-builtin 별칭 잔여(D-027 리뷰 신규 발견, 비차단·수용잔여)**: 삼중난독 폐쇄 후에도 **`getattr` 빌트인 자체를 별칭**한 변형 `g = getattr; fn = g(o,"system"); fn(c)` 는 call-only 모듈에서 **여전히 미감지**(fresh 실증 [F] — `resolve_getattr_call_name` 이 `func.func.id != "getattr"` 로 조기 반환). 이는 D-024/D-025 가 이미 **문서화 수용잔여**로 분류한 "call-only 동적우회" 계열의 더 깊은 변형이며, 완전폐쇄엔 지역 dataflow(callable 별칭 추적)가 필요(§2B 대규모). (a) import-신호 모듈(주 실행벡터)은 backstop 무영향, (b) 2층 approval 상한 → 최악도 승인 프롬프트 누락(오차단·자동머지 아님), (c) 무한퇴행(동적 디스패치 난독)의 좁은 하위변형 → **비차단·catalog 수용잔여로 명시**(신규 AC 가드 escalation 아님). 필요 시 지역 dataflow 도입 태스크에서 일괄 폐쇄.

## Phase D — 통합·테스트  *(A 완료 후)*
- **TASK-012** ☑ 감사카드 통합 (`changed_functions[]` + verdict 반영) — 리뷰통과·머지 (D-023, impl 81147f5). 경로-clean + 함수-frozen → blocked 격리 실증·parse_error→approval fail-closed·음성검증 3종. 비차단 관찰 4건(errors 분기 중복방어 미테스트·name-status 입력 함수분석 스킵[git-ref 필수 문서권고]·예외→blocked·changed_functions 중복표기) → `review-notes.md`.
  - **🔴 AC 가드(TASK-006 리뷰 D-012 #1)**: 매핑/추출 게이트 출력의 `error`(top-level git 실패) 또는 파일별 `parse_error`(문법오류) 가 존재하면 **fail-closed** 로 처리(verdict = 최소 `approval_required`, 파괴적이면 `blocked`). **`files`/`changed_functions` 가 비었다고 "변경 없음(pass)" 으로 간주 금지.** 이유: TASK-006 은 보고용으로 하드 에러 시 exit 0 + `error` + `files:[]` 를 반환하므로(Phase A 설계), 통합측이 `error` 를 무시하면 git 실패가 *clean diff* 로 읽혀 민감 변경을 통째로 놓침(fail-open). **보강(TASK-013 재리뷰 D-016)**: map 출력에서 `parse_error` 파일이 헝크 부재(git 바이너리 취급 — NUL 바이트 `.py` 실증)로 `touched_functions: []` 일 수 있다 — **빈 `touched_functions` ≠ clean**, `parse_error` 가 있으면 `<module>` touched 와 동등하게 보수 취급하라. **보강(TASK-009 재리뷰 D-021)**: TASK-009 `check-function-gov-level` 출력의 `errors` 가 비어있지 않으면 통합측도 **최소 `approval_required`** 로 취급(게이트 자체 fail-closed 의 중복 방어선 — R-1 류 재발 대비). 상류 top-level error 주입 픽스처(TASK-009 AC ④ 회귀 가드)도 이 태스크에서 추가 검토.
  - **🔴 AC 가드(TASK-007 리뷰 D-013 #1)**: **TASK-007 함수 분류 출력 단독으로 판정 금지.** 모듈레벨 변경(상수·import·톱레벨 문장 — 예: `ADMIN_ROLE = "user"→"admin"`)은 TASK-007 에 **아무 표식 없이 비가시**(`function_changes: []`)이므로, 반드시 TASK-006 헝크 매핑의 `<module>` touched 와 **병합**해 판정한다. 또한 `fallback: true` 파일(비-py·신규/삭제·parse_error·리네임)은 함수 단위가 안 보이므로 **파일 단위 보수 취급**(zone/intent 게이트 결과로 판정, "함수변경 0 = clean" 간주 금지).
- **TASK-013** ☑ Python before/after fixtures + 러너 확장 — 재리뷰통과·머지 (D-016, impl 0aaadcc; 1차 보정요청 D-015)
  - **🔴 AC 가드(TASK-007 재리뷰 D-014 #1) — 리네임 회귀 픽스처 실효화**: 현행 리네임 픽스처(`renamed_source→renamed_target`, 초소형+내용 수정)는 git 유사도 감지에 안 걸려 renames 환경에서도 D+A → **`--no-renames` 를 제거해도 스위트가 통과해 회귀를 못 잡음(실증)**. **순수 리네임(내용 동일) 쌍**을 추가하라 — 내용 동일 리네임은 크기 무관 exact-match 로 항상 R100 감지되므로(실증) 플래그 제거 회귀 시 스위트가 확실히 FAIL. 검수 시 "`--no-renames` 제거 → FAIL" 음성검증 포함.
  - **🔴 AC 가드(TASK-007 재리뷰 D-014 #2) — 파일 단위 오류 격리**: 비-UTF8 소스(`# -*- coding: latin-1 -*-` 등) `.py` M 파일 1건이 현행 classify 게이트에서 `UnicodeDecodeError` → top-level `error`+`files:[]` **전역 붕괴**(R-1 동류, 실증 — 형제 M 파일 분류 소실). 게이트(classify·map 공통)는 **파일별 예외를 해당 파일 fallback**(예: `fallback_reason: "unreadable"`)으로 격리하고 형제 파일 분류를 보존하도록 강건화 + **픽스처(비-UTF8 파일 + 동반 M 파일 → 형제 보존 기대값)** 로 고정하라. (현행은 TASK-012 fail-closed 가드로 fail-open 은 아님 — 희귀 입력이라 비차단 처리하되 여기서 명시적으로 막는다.)

# MVP-1.5 (신뢰·운영성 보강) — 계획  *(설계 확정: 2026-07-07 적대적 리뷰, D-028)*

> **왜 1.5인가**: 이 묶음은 새 탐지 *층*(MVP-2 종단 역추적)이 아니라, **MVP-0·1 기존 층의 신뢰성·도입성·자기무결성 보강**이다. 성격이 달라 별도 마일스톤. MVP-2 앞에 먼저 간다.
> **근거**: 2026-07-07 적대적 리뷰에서 직접 실증된 갭들 — ① 도입 시 zones/functions 를 사람이 백지에서 손으로 씀(자동 후보 없음) ② 동적 문자열 난독(`getattr(os,"sys"+"tem")`·변수경유) 정적분석 누락(실측) ③ "40/40 PASS"의 신뢰가 사람 수동 변조검증에 의존(뮤테이션 자동화 없음) ④ 정책 *완화* 방향에 별도 승인 없음(자기무력화 경로) ⑤ 탐지율 실측(shadow) 프로세스 부재.
> **불변 원칙 유지**: 2층(능력·동적접근) 판정은 여전히 **자동 차단 금지 → 승인요구/경고 상한**(D-004). LLM·추정 금지(결정적). 자동 씨딩은 **후보 제안까지만** — 최종 채택은 사람 승인(무인 지정 금지).
> **외부 검토 반영(2026-07-07, GPT 아키텍처 리뷰 — Claude 가 항목별 평가·취사선택)**: TASK-014~018 AC 보강 + TASK-019~021 신설. 근거는 각 태스크에 개별 표기.
> **실행 순서(P0 먼저)**: **TASK-018(자기무력화 방지) → 019(감사카드 정직화) → 020(maturity) → 014·015(씨딩) → 016(동적접근) → 017(뮤테이션) → 021(광역 의도선언)**. 자기무력화 방지가 선두인 이유: 구현이 싸고, 안 막으면 나머지 통제 전부가 무의미해지는 구조적 구멍이라서.
> **명시 보류(파일럿 이후 — 이번에 하지 않기로 결정한 것)**: stack adapter 시스템·데이터카탈로그/API게이트웨이 connector·detector mutation·INFO 등급 분리·backtest 러너·자동 policy-PR 생성(구현자≠승인자 경계 침식)·풀 7-상태기계.

### TASK-014 ☐ 정책 자동 씨딩 스캐너 `bootstrap-sensitive-zones.py`  (Codex)  *(개선점 #1)*
**목적**: 도입 시 사람이 백지에서 zones YAML 을 쓰지 않도록, **저장소를 스캔해 민감 경로 후보를 자동 생성**한다(사람은 승인만).
**입력**: 대상 repo 경로. 선택 입력: `CODEOWNERS`, 네이밍 규칙 목록.
**출력**: `sensitive-zones` **초안 YAML**(후보 + 근거 signal + 제안 등급) + `--json`.
**수용기준**:
1. 최소 2개 씨딩 소스 구현 — (a) **경로 네이밍 규칙**(`auth`/`security`/`pii`/`billing`/`secrets`/`migrations`/`crypto` 등 관용 토큰, 목록은 정책파일로 외부화) → 매칭 경로를 등급 후보로, (b) **CODEOWNERS**(존재 시) 특정 팀(예: security/dba) 소유 경로 → protected 후보.
2. 각 후보에 **근거(어느 소스·어느 규칙에 걸렸나)** 를 반드시 첨부(감사성). 근거 없는 후보 생성 금지.
3. 출력은 **초안일 뿐** — 파일을 직접 덮어쓰지 않는다(stdout/지정경로 초안만). "자동 채택" 문구·동작 금지.
4. 결정적(2회 동일, 정렬 고정) + `--json`. LLM·휴리스틱 점수 추정 금지 — 규칙 매칭만.
5. 미지원/빈 결과는 오류 아님(빈 후보 + 사유). CODEOWNERS 부재 시 (a)만으로 동작.
6. **🔴 후보 상태 + 거절 원장(GPT P4 최소형)**: 후보마다 `status: proposed` 와 결정적 `fingerprint` 부여. **이전 실행 산출물(후보 파일)을 선택 입력으로 받아** — `rejected` fingerprint 는 재제안 금지(왜 제외됐는지 카운트만 보고), `accepted` 는 중복 제안 금지. `rejected` 항목은 `rejected_reason`/`rejected_by` 필드 스키마 포함. 이게 없으면 스캔 재실행마다 거절된 후보가 재출현해 씨딩 자체가 alert fatigue 원인이 된다.
   - **🔴 AC 가드(TASK-014 리뷰 D-035 O-2 — fingerprint 안정성)**: fingerprint 는 **후보 정체성**(`path` + `level` + 정렬된 `{(source, rule_id)}` 집합)으로 산출한다. **개별 매칭 파일 경로(evidence[].path)는 지문 산출에서 제외**하고 evidence 보고에는 남긴다. 이유: 초기 구현(`ecd5d68`)은 지문을 `path+evidence` 전체 리스트로 계산해 — **이미 accepted/rejected 된 존에 형제 파일 1개만 추가돼도 지문이 바뀌어 후보가 재출현**(fresh 실증: rejected `services/auth/**` 에 `logout.py` 추가 시 `suppressed_rejected` 1→0). 이는 본 AC#6 이 막으려던 alert-fatigue 를 살아있는 repo 성장에서 그대로 재현하는 논리 결함. **회귀 픽스처 필수**: 존 reject → 형제 파일 추가 → 재스캔 시 **여전히 suppressed**(rejected·accepted 양쪽). TASK-015 anchor(정규화 심볼+시그니처 해시) 조항과 동일 계열의 "조용한 무효화 방지" 원칙.
**비고(설계)**: import-그래프 중심성·데이터카탈로그 PII 태그·SAST 출력 연동은 **후속 확장 여지**로 남긴다(이번 스코프는 네이밍+CODEOWNERS 2종). 무리한 전수 자동화 금지 — 후보 리콜보다 **근거의 정확성** 우선.

### TASK-015 ☑ 함수 후보 랭킹 `bootstrap-sensitive-functions.py`  (Codex)  *(개선점 #1)*  — **통과·머지완료(D-037, 2026-07-11)**
**목적**: `@gov` 전수 주석이 비현실적인 레거시에서, **이미 위험 능력을 쓰는 함수**를 자동 후보로 뽑아 `sensitive-functions.yaml`(코드-밖 목록) 초안을 만든다. 주석 0, 파일 무수정.
**입력**: 대상 repo 의 `.py` 파일들 + `sensitive-capabilities.yaml`.
**수용기준**:
1. 기존 `extract-python-capabilities` + `extract-python-inventory` 를 **재사용**(중복 구현 금지)해, "위험 능력 신호가 위치한 함수"를 파일·함수 단위로 집계.
2. 출력 = `(경로, 함수, 걸린 능력 id[], 근거 라인)` 목록 → `sensitive-functions` 초안. **코드에 주석을 달지 않는다**(코드-밖 목록만).
3. 초안일 뿐(직접 채택 금지) + 근거 필수 + 결정적 + `--json`.
4. **정직 한계 명시**: 위험 프리미티브를 안 쓰는 "의미상 민감 함수"(순수 계산 정산 로직 등)는 못 뽑음 → 출력 헤더/문서에 이 한계를 표기(과대선전 방지). **특히 "아무도 의미를 모르는(신호도 없는) 순수 로직"은 이 스캐너뿐 아니라 하네스 전체의 미해결 영역**임을 함께 명시 — 부분 안전망은 MVP-2 종단 역추적(연결로 잡기)과 unknown-코드 표시(후속 검토)뿐.
5. **SQL 테이블 참조 근거(선택 입력)**: 민감 테이블명 목록이 주어지면, 함수 본문 내 문자열 SQL 의 테이블명 매칭을 추가 근거로. 목록 없으면 스킵(오류 아님). 은행 도메인 특화 — 정산·PII 테이블명은 코드에 문자열로 남는다.
6. **anchor + 상태(GPT 2-c)**: 출력 스키마에 `anchor`(정규화 심볼 + 시그니처 해시)와 `status/fingerprint`(TASK-014 ⑥과 동일 규약) 포함 — 경로·이름 변경 시 목록이 조용히 무효화(보호 해제)되는 것 방지. 해시 불일치 시 "이동/변경 의심 — 재확인" 표시.
   - **🟠 차기 AC 가드(TASK-015 리뷰 D-037 — 3건, 전부 fail-safe·후속 태스크에서 보정)**:
     - **G-1 (AC#6 rename 노트)**: 현 `signature_hash = sha256(name(args))` 는 함수명을 포함해 **rename 시 `symbol`·`signature_hash` 가 동시에 바뀌어** `anchor_note` 의 "move or rename" 재확인 노트가 **move(경로변경)에만 발화하고 rename(이름변경)엔 절대 발화 못 한다** → AC#6 "이름 변경 시 재확인" 의 이름측 미충족. **수정계약**: `signature_hash` 를 **인자 시그니처만(함수명 독립)** 으로 산출(심볼이 이미 이름을 담으므로 중복 제거) → rename 시 sig_hash 불변 → "move or rename" 노트 발화. **회귀 픽스처 필수**: accept 원장 → 함수 rename → 재스캔 시 (a) 재제안 되고 (b) `review_note` 에 move/rename 노트가 뜬다.
     - **G-2 (데코레이터 라인 능력호출)**: 능력 호출이 **데코레이터 식**(`@subprocess.getoutput(...)`)에 있으면 라인이 `def`(start_line) 위라 함수 미귀속·`<module>` 폴백(inventory start_line=def줄 한계). fail-safe(신호 드롭 없음·정확 라인 노출)이나 **함수-정밀 귀속 상실**. CLAUDE.md 고정 적대세트가 요구하는 **데코레이터 상설 회귀 픽스처를 추가**하고, 가능하면 함수 라인범위를 데코레이터 첫 줄까지 확장해 귀속(TASK-005/006 성질과 정합 유지).
     - **G-3 (동일 지문 충돌)**: 한 파일 내 이름·시그니처·능력·evidence 가 전부 같은 두 함수(조건부 twin/동일시그 `@overload`)는 같은 fingerprint → 한쪽 reject/accept 시 **둘 다 suppress**(유일 fail-unsafe 방향). suppression 키에 `start_line` 또는 본문 해시 disambiguator 를 더하되, **위치 churn(함수 이동만으로 재제안) 재유입을 피하도록** 신중히(예: 파일 내 동명 충돌시에만 tie-breaker 적용).

### TASK-016 ☐ 동적 위험접근 감지 보강 (`extract-python-capabilities` 확장)  (Codex)  *(개선점 #2)*
**목적**: `getattr(os,"sys"+"tem")`·`getattr(os, name)`(변수경유)·`__import__("subpro"+"cess")` 등 **동적 문자열 난독으로 민감 모듈을 만지는 행위**를 잡는다. 무엇을 부르는지 값 추정은 하지 않되(정적분석 한계 인정), **"민감 모듈을 동적으로 접근하는 행위 자체"** 를 신호화.
**수용기준**:
1. `getattr`/`setattr`/`__import__`/`importlib.import_module` 의 인자가 **비-리터럴**(BinOp 문자열 조립·Name 변수 등)이고, 그 대상 객체가 **민감 모듈**(`os`·`subprocess`·`socket`·`sys`·`importlib` 등 카탈로그 연동 목록)이면 → **`watched`(경고) 신호** 로 보고. 대상이 리터럴로 확정되면 기존 로직대로 정확 매칭.
2. **오탐 억제**: 대상 객체가 민감 모듈이 아닌 일반 동적 접근(예: `getattr(self, field)`)은 신호 아님. 신호 조건을 "민감 모듈 대상"으로 좁힌다.
3. 판정 상한 = **`watched`(경고)**. 자동 차단·승인요구 강제 금지(값 미상 → 저확신 → 약하게, 설계 §3 확신도 원칙).
4. **🔴 상설 회귀 픽스처(고정 적대 세트)**: `getattr(os,"sys"+"tem")`·`getattr(os,name)`·`__import__("sub"+"process")`·(음성) `getattr(self,"x")` 를 fixtures 로 고정. "리터럴은 정확매칭 / 조립·변수는 watched / 일반객체는 무신호"를 각각 검증 + 음성검증(기대변조 시 FAIL).
5. 결정적 + `--json`. LLM·값 실행 금지.
6. **리터럴 조립 상수접기(GPT 2-b)**: 인자가 **문자열 리터럴만의 결합**(`"sys"+"tem"` 등)이면 결정적으로 접어(fold) 리터럴과 동일하게 **정확 매칭**으로 처리(= watched 가 아니라 해당 능력으로 정확 보고). 리터럴만으로 접을 수 없으면(변수·호출 포함) ①의 watched 신호로. 상수접기는 AST 수준 계산이라 결정론 원칙과 충돌 없음.
7. **신호 목록 확대**: `globals()`/`locals()`/`vars()` 경유의 이름 접근, `base64` 디코드 결과가 import/exec 인자로 쓰이는 인접 패턴 → watched. 적대 픽스처 세트(④)에 각 1건 추가.
8. **카탈로그 출처 메타데이터(GPT 2-a)**: `sensitive-capabilities.yaml` 스키마에 `source`(`builtin: cwe/owasp/bandit` | `org: <팀>`)·`owner` 필드 추가, 기존 5종 전 항목 기입. "이 목록 왜 믿나"가 파일 자체로 답해지게(형 질문의 명문화). — ✅ **Claude 완료**(2026-07-11, Q-0003/A-0011, 5종 source+owner 기입).
9. **🔴 하류 정합 가드 — level 에스컬레이션(D-038/R-1 보정사유)**: watched 도입으로 "능력 id 1개 ⇒ level 1개" 전제가 깨졌다. `check-new-capabilities` 는 신규탐지(id 차분)에 더해 **base∩head 공유 id 의 level 이 `watched`→`protected` 로 강해지면 신규/승격으로 잡아 `approval_required`(exit 2)** 해야 한다. 안 그러면 base 의 동적 watched 가 head 의 **신규 protected 정적호출을 은닉**(실증: base `getattr(os,name)`+head `os.system` → main exit2 ↔ 브랜치 exit0). 상설 회귀 픽스처(그 세트)+음성검증 필수.
**근거**: 2026-07-07 리뷰 실측 — 현행은 조립·변수경유가 verdict=pass 로 완전 누락. 정적분석상 100% 차단은 불가하나 "동적으로 민감모듈 접근이 *새로 생김*"은 결정적으로 잡힌다.
**리뷰 상태(2026-07-11, D-038)**: 추출기 AC #1~7 실증 통과 · AC#8 Claude 완료 · **AC#9(R-1) 보정요청 — 코드 브랜치 머지 보류**. 재제출은 `check-new-capabilities` level 에스컬레이션 보정 델타만.

### TASK-017 ☐ 뮤테이션(음성검증) 자동화 `tests/mutation-check.sh`  (Codex)  *(개선점 #3)*
**목적**: "40/40 PASS"가 *시험이 죽어서* 나온 게 아님을 **매 CI 자동 보증**한다. 지금은 사람이 수동으로 기대값을 변조해야만 확인됨.
**수용기준**:
1. `tests/cases.yaml` 의 각 케이스 기대값(verdict/exit_code)을 **프로그램적으로 변조**한 뒤 스위트를 돌려, **반드시 FAIL 이 발생**함을 확인(원본은 자동 복원).
2. 변조했는데 PASS 가 유지되는 케이스(=죽은 테스트)를 **목록으로 보고**하고 종료코드 비0.
3. 최소 verdict·exit_code 두 필드 변조 지원. 결정적. 원본 파일 무변경 보장(복원 실패 시 에러).
4. CI/러너에서 호출 가능한 단일 진입점.
5. **policy mutation(GPT 3-c)**: 기대값 변조에 더해 **정책 변조** 1종 이상 — 민감 경로 규칙 1건 삭제(또는 frozen→watched 하향)를 임시 적용 → 관련 케이스가 FAIL 하는지 확인(원본 복원 보장). "정책이 실제로 판정을 지배한다"의 자동 증명.
6. **metamorphic 케이스(GPT 3-a)**: 의미 불변 변형 — (a) import 에 별칭 부여, (b) 공백·빈 줄·주석 삽입, (c) 함수 정의 순서 이동 — 각각에 대해 **판정 동일**을 검증하는 케이스 최소 3종. 결정론 주장의 실증 장치.
7. **negative corpus 명시 분리**: 무해 변경(주석만·docstring·비민감 경로 신규 함수)이 **어떤 경고도 만들지 않음**을 검증하는 케이스군을 러너에서 별도 그룹으로 표기 — 오탐 없음의 체계적 증거(alert fatigue 방어 근거).
**근거**: 리뷰에서 blocked→pass 변조 시 정상 FAIL(39/40) 확인 — 이 수동 절차를 상설화. detector mutation(탐지기 코드 자체 변조)은 비용 대비 후순위로 **명시 보류**.

### TASK-018 ☐ 정책 완화 방향 별도 승인 게이트 `check-policy-change.py`  (Codex)  *(개선점 #4/#5 · **P0 — MVP-1.5 선두**)*
**목적**: 통제 장치의 **자기 무력화**를 막는다. 정책 파일(`policies/*.yaml`) 변경 중 **강화(등급↑·규칙 추가)** 는 통과, **완화(등급↓·규칙/항목 삭제·범위 축소)** 는 **사람 승인 강제**. GPT 검토(위험④)로 범위 확대: 정책 파일만 지키면 **집행 스위치(CI·게이트 코드) 를 꺼버리는 우회**가 남는다 — 자기보호 대상을 집행 경로까지 넓힌다.
**수용기준**:
1. base/head 두 버전의 정책 YAML 을 파싱해 **의미 diff** 산출 — 항목 삭제, 등급 하향(`frozen`→`protected`→`watched`→없음), 민감경로 범위 축소, `new_only`/`max_verdict` 완화 등을 **완화(loosening)** 로 분류.
2. 완화가 하나라도 있으면 **`approval_required`**(정책 소유자 라우팅), 강화·무관 변경만이면 `pass`. 텍스트 diff 가 아니라 **구조 비교**로(주석·순서·포맷 변경은 무시).
3. **자기적용**: 이 게이트 자신과 라우팅 규칙 변경도 동일 검사 대상.
4. **🔴 회귀 픽스처 + 음성검증**: (완화) 등급 하향·규칙 삭제 → approval, (강화) 등급 상향·규칙 추가 → pass, (무관) 주석만 변경 → pass 를 각각 고정. 기대변조 시 FAIL.
5. 결정적 + `--json`. 종료코드 0/2(차단 없음 — 완화도 "승인 후 가능").
6. **🔴 자기보호 경로 세트(GPT 위험④)**: `policies/**`·`.harness/**`·`tests/run-tests.sh`·`tests/cases.yaml`·CI workflow 경로(`.github/workflows/**` 등, 생기면)·`CODEOWNERS` 를 **sensitive-zones 에 protected 로 등록**(새 차단 메커니즘 발명 금지 — 1층 재사용). 이 게이트 자신은 "완화 방향 의미 diff" 판정만 담당(역할 분리).
7. **집행 우회 탐지**: CI workflow/러너 diff 에서 (a) 게이트 호출 라인 제거, (b) `|| true`·`continue-on-error` 류 무력화 삽입, (c) required check 제거 — 를 **완화**로 분류(결정적 패턴 매칭, 의미 추정 금지). 픽스처 각 1건.
8. **policy bundle digest**: 감사카드에 판정 시점의 정책 파일 해시 목록 기록 — "당시 어떤 규칙으로 판정했나" 재현성(감사카드 신뢰성 절과 정합).
**근거**: 현행은 정책 변경도 하네스 검사를 받지만 **방향(강화/완화)을 구분 안 함** → 규칙을 몰래 느슨하게 만드는 변경이 일반 변경과 동급. shadow-측정(#6=개선점)은 **운영 과제**라 코드 태스크 아님 → `collab/needs-human/` 로 이관.

### TASK-019 ☐ 감사카드 정직화 — coverage statement  (Codex)  *(GPT P1)*
**목적**: "PASS = 안전 인증" 오독을 **카드 출력 자체에서** 차단한다. 정직 고지가 지금은 문서(제안서)에만 있어 결과만 보는 리뷰어에게 닿지 않는다.
**수용기준**:
1. 카드·게이트 출력에서 `SAFE`/"안전" 류 표현 금지 — verdict pass 문구는 **"정책 위반 미탐지(no governance violation detected)"** 로 통일.
2. 카드에 **coverage statement 블록**: "이 판정이 본 것"(실제 실행된 게이트 목록에서 동적 생성 — 경로/의도/함수/능력 중 뭐가 돌았나) + "이 판정이 보지 않는 것"(고정 목록: 런타임 실행경로·미등록 민감로직·cross-commit 누적·비-Python 정밀분석·동적 난독 완전복원). 정적 문구가 아니라 **실행된 게이트 기반**이어야 함 — 게이트를 빼고 돌리면 "본 것"이 줄어야 정직.
3. 버전 기록 확장: 기존 `tool_version`/`policy_sha` 에 **python(parser) 버전** 추가 (결정론 재현 조건 — GPT 위험⑦).
4. 카드 스키마 회귀 픽스처 + 음성검증(기대변조 시 FAIL). 스키마 키는 템플릿과 일치(임의 키 추가 금지 원칙 유지 — `templates/change-evidence.template.yaml` 동시 개정).

### TASK-020 ☐ 규칙 성숙도(maturity) — shadow 도입 완충  (Codex)  *(GPT P2 · 개선점 "초기 시행착오")*
**목적**: 새 규칙을 켤 때 "즉시 전면 집행"이 아니라 **기록만(shadow) → 집행(enforcing)** 단계로 도입하게 해, 초기 룰셋 시행착오가 개발자를 막지 않게 한다.
**범위 명확화(정직)**: 우리 게이트는 diff 기반이라 "기존 코드 전수 finding" 자체가 없음 — GPT 의 new-code baseline 은 **절반이 이미 내장**. 이 태스크가 더하는 것은 **규칙 신설 시점의 완충**뿐. 별도 baseline store 는 스코프 아님(보류 목록).
**수용기준**:
1. `sensitive-zones`/`sensitive-capabilities` 항목에 `maturity: shadow|enforcing` 필드(**기본 enforcing** — 무기입 시 기존 동작과 완전 동일, 하위호환).
2. `shadow` 규칙에 걸린 변경: **판정(verdict)에 미반영** + 감사카드에 `shadow_hits` 로 별도 기록(무엇이 걸렸을지 관찰 가능). 판정 로직은 무변경 — 걸러내는 위치는 verdict 집계 직전.
3. 잘못된 maturity 값은 검증오류 + **enforcing 보수 취급**(fail-closed 계보 — 완충 장치가 완화 우회로 악용되지 않게. `maturity: shadow` 로 바꾸는 diff 는 TASK-018 이 "완화"로 잡는다 — 두 태스크 정합 필수).
4. 픽스처: 동일 입력이 shadow 면 pass+기록 / enforcing 이면 approval — 쌍으로 고정 + 음성검증.

### TASK-021 ☐ 광역 의도선언 격상 (`check-change-intent` 확장)  (Codex)  *(GPT 위험③)*
**목적**: `allowed_paths: ["**"]` 류 **사실상 무의미한 선언**으로 의도 게이트를 무력화하는 것을 막는다. 정상적인 넓은 선언은 건드리지 않는다 — "정확한 범위를 맞혀라"가 아니라 "선언을 무의미하게 만들지 마라".
**수용기준**:
1. 결정적 광역 판정: (a) 루트 전체 glob(`**`·`*`·`./**` 등 정규화 후 동치) 포함, 또는 (b) 선언 glob 들이 저장소 **최상위 디렉토리의 N% 이상**을 커버(N 은 정책값, 기본 80) → `scope_too_broad` 플래그 + 최소 `approval_required`.
2. **오탐 억제 필수**: 넓지만 유의미한 선언(복수 팀 폴더 나열 등, 임계 미만)은 무간섭 — pass 픽스처로 고정.
3. 기존 TASK-001 판정 로직 무변경(추가 검사만, 하위호환). blocked 로 승격 금지(선언 문제는 차단 사유 아님 — 확인 요청일 뿐).
4. 픽스처(광역→approval / 정상 넓음→pass / 기존 케이스 전부 무영향) + 음성검증.

## MVP-2 설계 시 검토 기록 (미결 — 설계 단계에서 결정)
- **🔴 `@gov` ↔ sink 관계 (형 지시로 기록, 2026-07-07)**: `@gov`(이름표)는 그 함수 **직접 수정만** 잡고, 그 함수를 떠받치는 상류 함수 수정(간접 영향)은 sink 등록 + 종단 역추적이 있어야 잡힌다. 대표 시나리오: 다운로드 함수에 `@gov` 를 달아도 `check_permission()` 을 고치는 변경은 현행 무탐지. **설계 질문**: ① `@gov` 함수를 자동으로 sink 취급(편의↑, 콜그래프 비용·간접경고 오탐↑) ② 분리 유지 + `@gov(sink=true)` 옵트인 ③ level 별 차등(frozen 은 자동 sink 등). MVP-2 설계 문서에서 결정·근거 기록.
- cross-commit 누적 위험(여러 PR 에 쪼개 넣기)은 sink 그래프의 누적 비교와 함께 검토(GPT 위험⑥).
- 비-Python·비-코드 artifact(SQL·YAML·notebook·IaC) 함수-수준 정밀화는 경로 겹이 이미 커버하는 범위 확인 후 언어별 로드맵으로.

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
