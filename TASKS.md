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

### TASK-014 ☑ 정책 자동 씨딩 스캐너 `bootstrap-sensitive-zones.py`  (Codex)  *(개선점 #1)*  — **통과·머지완료(D-035·D-036, 2026-07-11)**
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

### TASK-016 ☑ 동적 위험접근 감지 보강 (`extract-python-capabilities` 확장)  (Codex)  *(개선점 #2)*  — **완결(D-039)**
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
**리뷰 상태(2026-07-11, D-039)**: **완결 · Claude main 머지**. 추출기 AC #1~7(D-038 통과) · AC#8 Claude 완료 · **AC#9(R-1) 보정 재제출 `e839fe9` 통과** — `check-new-capabilities` 가 base∩head 공유 id 의 watched→protected 에스컬레이션을 감지해 approval_required(exit 2), 상설 회귀 픽스처 `new-capabilities-dynamic-level-escalation`+음성검증(루프 제거 시 pass 회귀). 68/68 PASS. 상세 D-039·A-0011 §해소·review-notes.

### TASK-017 ☑ 뮤테이션(음성검증) 자동화 `tests/mutation-check.sh`  (Codex)  *(개선점 #3)*  — **done·통과·머지완료 (D-040, 2026-07-11)**
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

### TASK-018 ☑ 정책 완화 방향 별도 승인 게이트 `check-policy-change.py`  (Codex)  *(개선점 #4/#5 · **P0 — MVP-1.5 선두**)*  — **통과·머지완료(D-030, 2026-07-09)**
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

### TASK-019 ☑ 감사카드 정직화 — coverage statement  (Codex)  *(GPT P1)*  — **통과·머지완료(D-032, 2026-07-11)**
**목적**: "PASS = 안전 인증" 오독을 **카드 출력 자체에서** 차단한다. 정직 고지가 지금은 문서(제안서)에만 있어 결과만 보는 리뷰어에게 닿지 않는다.
**수용기준**:
1. 카드·게이트 출력에서 `SAFE`/"안전" 류 표현 금지 — verdict pass 문구는 **"정책 위반 미탐지(no governance violation detected)"** 로 통일.
2. 카드에 **coverage statement 블록**: "이 판정이 본 것"(실제 실행된 게이트 목록에서 동적 생성 — 경로/의도/함수/능력 중 뭐가 돌았나) + "이 판정이 보지 않는 것"(고정 목록: 런타임 실행경로·미등록 민감로직·cross-commit 누적·비-Python 정밀분석·동적 난독 완전복원). 정적 문구가 아니라 **실행된 게이트 기반**이어야 함 — 게이트를 빼고 돌리면 "본 것"이 줄어야 정직.
3. 버전 기록 확장: 기존 `tool_version`/`policy_sha` 에 **python(parser) 버전** 추가 (결정론 재현 조건 — GPT 위험⑦).
4. 카드 스키마 회귀 픽스처 + 음성검증(기대변조 시 FAIL). 스키마 키는 템플릿과 일치(임의 키 추가 금지 원칙 유지 — `templates/change-evidence.template.yaml` 동시 개정).

### TASK-020 ☑ 규칙 성숙도(maturity) — shadow 도입 완충  (Codex)  *(GPT P2 · 개선점 "초기 시행착오")*  — **통과·머지완료(D-034, 2026-07-11)**
**목적**: 새 규칙을 켤 때 "즉시 전면 집행"이 아니라 **기록만(shadow) → 집행(enforcing)** 단계로 도입하게 해, 초기 룰셋 시행착오가 개발자를 막지 않게 한다.
**범위 명확화(정직)**: 우리 게이트는 diff 기반이라 "기존 코드 전수 finding" 자체가 없음 — GPT 의 new-code baseline 은 **절반이 이미 내장**. 이 태스크가 더하는 것은 **규칙 신설 시점의 완충**뿐. 별도 baseline store 는 스코프 아님(보류 목록).
**수용기준**:
1. `sensitive-zones`/`sensitive-capabilities` 항목에 `maturity: shadow|enforcing` 필드(**기본 enforcing** — 무기입 시 기존 동작과 완전 동일, 하위호환).
2. `shadow` 규칙에 걸린 변경: **판정(verdict)에 미반영** + 감사카드에 `shadow_hits` 로 별도 기록(무엇이 걸렸을지 관찰 가능). 판정 로직은 무변경 — 걸러내는 위치는 verdict 집계 직전.
3. 잘못된 maturity 값은 검증오류 + **enforcing 보수 취급**(fail-closed 계보 — 완충 장치가 완화 우회로 악용되지 않게. `maturity: shadow` 로 바꾸는 diff 는 TASK-018 이 "완화"로 잡는다 — 두 태스크 정합 필수).
4. 픽스처: 동일 입력이 shadow 면 pass+기록 / enforcing 이면 approval — 쌍으로 고정 + 음성검증.

### TASK-021 ☑ 광역 의도선언 격상 (`check-change-intent` 확장)  (Codex)  *(GPT 위험③)*  — **통과·머지완료(D-042·D-043, 2026-07-13)**
**목적**: `allowed_paths: ["**"]` 류 **사실상 무의미한 선언**으로 의도 게이트를 무력화하는 것을 막는다. 정상적인 넓은 선언은 건드리지 않는다 — "정확한 범위를 맞혀라"가 아니라 "선언을 무의미하게 만들지 마라".
**수용기준**:
1. 결정적 광역 판정: (a) 루트 전체 glob(`**`·`*`·`./**` 등 정규화 후 동치) 포함, 또는 (b) 선언 glob 들이 저장소 **최상위 디렉토리의 N% 이상**을 커버(N 은 정책값, 기본 80) → `scope_too_broad` 플래그 + 최소 `approval_required`.
2. **오탐 억제 필수**: 넓지만 유의미한 선언(복수 팀 폴더 나열 등, 임계 미만)은 무간섭 — pass 픽스처로 고정.
3. 기존 TASK-001 판정 로직 무변경(추가 검사만, 하위호환). blocked 로 승격 금지(선언 문제는 차단 사유 아님 — 확인 요청일 뿐).
4. 픽스처(광역→approval / 정상 넓음→pass / 기존 케이스 전부 무영향) + 음성검증.

## MVP-2 — 영향 추적(간접 영향 / sink 역도달성)

> **설계문서**: `docs/mvp2-impact-tracing-design.md` (Draft — 형 확정 대기, 2026-07-13).
> **왜 MVP-2인가**: MVP-0·1·1.5 는 **직접** 신호(경로·@gov 직접수정·새 능력·의도이탈)만 잡는다. sink 이 의존하는 **상류 함수를 고쳐 간접적으로** 민감 행동을 무너뜨리는 건 현행 완전 무탐지 — 이 층이 그 구멍을 메운다.
> **확정 방향(형 승인 2026-07-13)**: ① @gov↔sink = **레벨 차등**(frozen 자동 sink + `@gov(sink=true)` 옵트인, 일반 @gov·protected 는 sink 아님) · ② **최소 스코프**(단일 diff·N=1홉 시작·shadow 성숙도로 시작·래칫). **차단 절대 금지 → 승인요구 상한**.
> **명시 비범위**(설계 §7): cross-commit 누적(→ Phase B/MVP-3, baseline 저장 필요) · 비-Python artifact 함수수준(→ 언어별 후속) · 동적 호출 완전복원(→ 영구 한계, coverage 노출).

### TASK-022 ☑ sink 등록 스키마 (`@gov(sink=true)` + frozen 자동 + `sink-registry`)  (Codex)  *(MVP-2)*  — **통과·머지완료(D-045 보정요청 → D-046 재리뷰통과, 2026-07-15)**
**목적**: 간접 영향 추적의 **대상(sink)** 을 등록만 한다(판정 미변경). 콜그래프를 소수 고가치에만 걸어 신호대잡음 보존.
**수용기준**:
1. `@gov(sink=true)` 파싱 — 기존 @gov 데코레이터 인식(TASK-005 계열) 확장, **하위호환**(`sink` 미지정=기존 동작·직접수정만, 무회귀).
2. **frozen 존 함수 자동 sink** — `sensitive-zones.yaml` frozen 경로 내 함수는 등록 없이 sink.
3. 정책 `sink-registry`(신규 스키마 또는 sensitive-zones 확장) — @gov 못 다는 코드용 명시 등록. Claude 가 스키마 확정.
4. 일반 `@gov`(sink 미지정)·protected 존 함수는 **sink 아님**(직접수정 게이트가 커버). sink 집합에서 제외 검증.
5. sink 목록을 결정적 산출(다음 태스크 입력). 픽스처: 옵트인 sink / frozen 자동 / 비-sink 각각 + 하위호환 무회귀 + 음성검증.

### TASK-022b ☑ 배포용 킷(`kit/run.sh`) 교차리뷰 + 개선 구현 — **역할 역전(Codex 가 Claude 코드를 감사·보강)**  *(D-047)*  — **통과·머지완료(D-048 감사·보강 → D-049 보정요청 → D-050 재리뷰통과, 2026-07-15 · 킷 v0 main 수용)**
**대상 브랜치**: `claude/2026-07-15-kit-draft` (kit/ 만 최신 main 위에 얹은 클린 브랜치·충돌 없음). **설계 근거**: D-047.
**배경**: `kit/` 는 배포용 킷 초안(D-047) — 개발 게이트 13종을 co-located 로 묶고 `run.sh` 가 그 판정을 조립한다. **`run.sh` 의 verdict-combine 로직은 Claude 가 직접 작성**했다. 이 하네스의 상호견제 원칙("Claude 는 게이트 코드를 직접 작성하지 않는다")상 판정 조립 로직도 예외가 아니다 — main 머지 직전 거버넌스 분류기가 이 자기작성·자기머지 시도를 실제로 차단했다(2026-07-15). 그래서 **Codex 가 감사자**가 되어 검수하고, 아래 2개 개선을 **Codex 가 구현**한다(verdict-affecting 셸을 Codex 가 저자하게 되어 상호견제 정합).
**목적**: `kit/run.sh`(및 `sync-from-dev.sh`·`bootstrap.sh`·`selftest.sh`)를 판정 의도 대비 감사 + 적대검증(D-046 시절 5/5)이 짚은 2갭을 보강한다. 통과·보강 후 Codex 가 `collab/answers/` 에 기록, Claude 가 그 근거로 `kit/` 를 main 머지(상호승인).
**검수 + 구현 체크리스트**:
1. **[감사]** `run.sh` 최종판정 = 가장 센 것(차단 > 승인 > 통과), `max(ge_exit, cap_exit, pol_exit)` 조립이 각 게이트 실제 exit code 의미(카드3축 0/1/2·능력 0/2·정책 0/2)와 정확히 일치하는가 — 코드 대조. 특히 `HAS_RANGE`(`..` 없으면 능력·정책 게이트 생략) 조건이 조용한 누락을 만들지 않는지.
2. **[구현 — 갭①: 분석실패 정직성]** 현재 `run.sh` 는 **게이트 크래시(exit 1/2)와 진짜 판정을 구분 못 한다**(적대검증 실증: 게이트 `.py` 삭제 시 python 크래시 exit 를 판정으로 오흡수 + 감사카드가 Traceback 으로 대체돼도 종료코드가 가림 — ADR-001 D4 정직성 위배). 게이트 파일 부재·`Traceback`·비정상 종료(0/1/2 밖)를 **'분석 실패'로 명시하고 fail-closed(승인요구)+tool_owner 표시**하도록 보강. 놓친 실패모드(무한루프·타임아웃 등)도 적대적으로 점검.
3. **[구현 — 갭②: 대상 repo 정책 오버라이드]** 현재 `run.sh` 는 킷 정책(`kit/policies`)만 집행 → **대상 repo 자기선언 frozen 이 무보호 통과하는 온보딩 함정**(적대검증 실증). `--policies <dir>` 옵션 추가해 대상 repo 정책 집행 가능하게(3게이트 전부 일관 적용).
4. **[감사/관찰]** `sync-from-dev.sh` 의 "dev 게이트 수 == kit 게이트 수" 누락검증이 **개수만** 보고 **내용 드리프트**(파일명 같은데 내용 다름)는 못 잡음 — 개선 제안(체크섬 비교 등, 강제 아님·차기 관찰로 기록 가능).
5. **[실증]** fresh 적대 입력(우리 repo 밖 합성 시나리오)으로 rig-and-revert 재현: frozen 차단·신규 능력 승인요구·정책완화 승인요구·게이트 삭제 시 **분석실패 명시**(갭① 보강 검증)·`--policies` 로 대상 frozen 보호(갭② 보강 검증) — 각 1회 이상.
**산출**: `collab/answers/A-00XX.md`(감사·보강 결과) + `collab/decisions.md` D-XXX + 보강 커밋을 `claude/2026-07-15-kit-draft` 에 push(같은 브랜치). 통과면 Claude 가 `kit/` 를 main 머지.
**비고**: 통상 "Codex 구현·Claude 검수" 의 **역방향**(Codex 가 Claude 코드 감사 + verdict-affecting 개선 구현). 신규 기능이 아니라 셸 감사·보강이라 AC 형식이 다르다. 유실 경위: D-046 시절 개선(run_gate·--policies)을 커밋(7e1bfe8)했으나 브랜치 재작성 중 미푸시로 유실 → 재구현을 Codex 몫으로 돌려 상호견제 정합.
**진행상태(2026-07-15)**: Codex 교차감사·보강 `00bde19` 제출(D-048·A-0015) → Claude 최종리뷰 = **보정요청 R-1**(watcher sleep 파이프 점유 회귀·D-049·A-0016). 감사·보강 의도(갭①②)는 달성 확인 — 보정 델타(fd 분리 1줄+회귀가드 1건)만 재리뷰 후 머지 예정.

### TASK-023 ☑ intra-repo 정적 콜그래프 빌더 (결정론·이름기반 + coverage 정직)  (Codex)  *(MVP-2)*  — **통과·머지완료(D-052 보정요청 → D-053·D-054 재리뷰(R-1·R-2·R-3 동명 오버로드 3변형) → D-055 R-3 해소 통과, 2026-07-16)**
> **동반작업(비차단·소규모·~10분)**: ① D-046 R-2 이월분 **G-sink-1**(frozen-auto-sink 테스트의 라이브 정책 결합 → fixture-local 로 결정적 고정, A-0013 허용) ② **A-0017** 킷 러너 사용성 `⚠` 안내 2건(스키마 오기·카드오염 — 판정 무영향 echo 만, 스펙 `collab/answers/A-0017.md`, D-051).
**목적**: repo 내 함수 호출 엣지를 결정적으로 빌드. 판정 미연결(그래프 산출만).
**수용기준**:
1. AST 로 함수정의별 호출 수집, 기존 import 해소(별칭·from-import) 재사용 → **repo 내 함수정의로 해소되는 호출만 엣지**(caller→callee).
2. **해소 실패 호출**(getattr·동적·외부·미상 메서드)은 **버리지 않고** 함수별 `unresolved_calls` 로 기록 → coverage.unevaluated 노출(조용한 누락 금지, ADR-001 D4).
3. **결정론**: 같은 입력 → 같은 그래프(엣지·정렬 안정). md5 반복검증.
4. 동명 오버로드·조건부 정의는 **보수적 병합**(합집합, 기존 추출기 `strongest_level` 방식 정합).
5. 픽스처: 단순 체인·별칭 호출·미해소(getattr) 노출·조건부 def + 결정론 반복.

### TASK-024 ☑ 역도달성 게이트 (간접 영향 → 승인요구)  (Codex)  *(MVP-2)*  — **통과·머지완료(D-056, 2026-07-16)**
**목적**: 바뀐 함수가 sink 의 (전이적 N홉) 상류면 승인요구 라우팅.
**수용기준**:
1. 바뀐 함수(diff·기존 함수매핑 재사용) ∈ (sink 로부터 forward 도달 **N홉**, N=1 시작) → `indirect_impact` finding, 최소 `approval_required`. **차단 금지**.
2. finding 에 `sink_id`·`changed_function`·`path`(sink→…→changed)·`hops` — 감사카드 30초 판독.
3. 라우팅 = 영향받은 **sink 의 owner/reviewer**. 분석 실패면 ADR-001 F-2(최소 approval·route=tool_owner).
4. **shadow 성숙도**(TASK-020) 지원 — 신규 sink 는 shadow 로 시작(verdict 미반영·`shadow_hits`). enforcing 승격은 정책.
5. **N홉 경계 정확**: N=1 에서 2홉 상류는 미발화(경계) · sink 무관 수정 미발화(과탐경계). 픽스처 + 음성검증(역도달 필터 무력화 시 참케이스 뒤집힘).

### TASK-025 ☑ 과탐 통제 + 고정 적대 입력 세트  (Codex)  *(MVP-2)*  — **통과·머지완료(D-057, 2026-07-16)**
**목적**: 도입 실패 1순위(과탐으로 게이트 꺼버림) 방지 + 상설 회귀.
**수용기준**:
1. 설계 §9 **고정 적대 입력 세트 7종**을 상설 회귀 픽스처로(직접경로·N홉경계·동적 미탐 coverage노출·옵트인경계·과탐경계·음성검증·동명조건부).
2. 거리 N 은 **정책값**(기본 1) — 래칫 가능하게 파라미터화. 하드코딩 금지.
3. 동적 호출 미탐이 **coverage.unevaluated 로 노출**됨을 테스트로 고정(정직성 회귀 — 조용한 통과 아님).
4. 고팬인 dampening 은 **하지 않음**(초기) — 진짜 경로 은폐 위험. 후속 검토 주석만.

**의존·순서**: 022 → 023 → 024 → 025 (각 통과·머지 후 다음 착수, 기존 배치 규율).

### TASK-026 ☐ 킷에 MVP-2 반영 — 역도달성 게이트 배선 (`kit/run.sh` 확장)  (Codex)  *(MVP-2 킷 스냅샷)*
> 🔴 **철저 개발 요구(형 지시)**: 킷은 배포·실사용의 최전선이라 **빠진 부분 없이 세부까지** 개발할 것. 각 AC 를 체크리스트로 자가검증하고, "될 것 같다"가 아니라 **fresh 적대입력으로 실제 돌려 확인**(§2B). 특히 (a) 새 게이트의 내부 의존(`extract-sinks`·`extract-callgraph` co-located) 이 킷에서 실제 해소되는지, (b) `check-indirect-impact` 가 **HAS_RANGE·정책 부재·sink-registry 오버라이드** 전 경로에서 올바로 배선됐는지, (c) 최종 verdict 조립에 간접영향층이 실제 반영돼 **누락 0** 인지를 한 줄씩 확인. 인계 전 `kit/selftest.sh`(러너+진입점 적대) 전량 green + 간접영향 rig-and-revert 필수.
**배경**: MVP-2(TASK-022~025) 완결로 dev 게이트가 16종(신규 `extract-sinks`·`extract-callgraph`·`check-indirect-impact`)인데 배포 킷은 MVP-1.5 스냅샷(13종)에 머물러 있다. 형 계획("MVP 달성마다 킷 반영")대로 킷을 MVP-2 상태로 올린다. **★단순 sync 아님**: 새 `check-indirect-impact` 는 **판정 게이트**(exit 0=pass / 2=approval_required, "indirect sink impact")라 `run.sh` 에 **명시 배선**돼야 실제 작동한다. `run.sh` verdict 조립은 D-050 이후 **Codex 저자 파일**이라 이 확장도 Codex 몫(Claude 가 하면 상호견제 위반·분류기 차단 — 세션 중 2회 실증).
**수용기준**:
1. `sync-from-dev.sh` 실행 → 16종 게이트 + `policies/sink-registry.yaml` 정책이 킷에 반영(누락검증 dev수==kit수 통과). 필요시 sync 스크립트가 sink-registry 정책도 복사하도록 확장.
2. `run.sh` 에 **4번째 판정층 배선**: `check-indirect-impact.py <base>..<head> --sink-registry <sink-registry> [--repo .]` 를 `run_gate` 로 실행(허용 exit `0 2`), 최종판정 `max(카드3축, 능력, 정책, **간접영향**)` 에 포함. 차단 금지(승인 상한 — MVP-2 설계). `check-new-capabilities`·`check-policy-change` 배선 패턴 재사용.
3. `--policies` 오버라이드가 sink-registry 에도 일관 적용(대상 repo 자기 sink 등록 지원). sink-registry 부재 시 fail-safe(설계대로 — 조용한 통과 금지).
4. `manifest.yaml` 게이트 목록 13→16 갱신(runtime_verdict 에 check-indirect-impact, extraction 에 extract-sinks·extract-callgraph 추가). `README.md` "반영된 MVP" 에 MVP-2·게이트 표 갱신·"draft(MVP-0·1·1.5)" → MVP-2 반영.
5. `selftest.sh`/`run-entrypoint-tests.sh` 에 간접영향 층 검증 추가 — fresh 적대입력 1종 이상(sink 상류 함수 수정 → 승인요구, rig-and-revert). 기존 진입점 적대·selftest 무회귀.
**비고**: 통상 Codex 구현 → Claude 리뷰·머지. 킷 러너 verdict 배선이라 민감도는 기존 킷과 동일(비민감·2·3층 승인 상한). 동반: 킷 README §알려진갭 4번("MVP-2 개발 중") 문구도 갱신.

## MVP-2 보강 — 패치 생존성(부재 탐지)  *(형 질문 2026-07-16 → 설계 D-059)*

> **왜 필요한가**: 지금까지 하네스의 **모든** 게이트는 "무언가가 diff 에 **있으면** 발화"하는 **존재 탐지기**다. 벤더-브랜치 전략(오픈소스 origin 이 갱신되면 patch/custom 브랜치를 재적용)에서 형이 물은 질문 — "패치 브랜치에 **명시된 파이썬 파일들이 실제로 수정됐는지**"(Q2) — 은 **반대 방향**이다: **선언한 파일이 diff 에 없으면**(패치 유실/미적용) 발화하는 **부재 탐지**.
> **민감경로(존재 탐지)로는 이 구멍을 못 막는다(실증적 논리)**: 패치가 적용되면 존재 탐지가 (중복) 발화하고, **패치가 유실되면 그 파일이 diff 에 없어 침묵** — *정확히 필요한 순간에 실패*한다. 그래서 `change_intent.expected_paths`(반드시 건드려야 하는 파일 선언)라는 **첫 부재 탐지 신호**를 추가한다.
> **불변 원칙 유지**: 판정 상한 = `approval_required`(**차단 없음** — 선언 문제는 확인 요청이지 차단 사유 아님, TASK-021 #3 계보). **기본 off**(미선언=기존 동작 완전 동일·하위호환). LLM·추정 금지(결정적).
> **구조**: TASK-027(dev 게이트 확장) → TASK-028(킷 스냅샷 반영). MVP-2 를 최종 반영 지점으로.

### TASK-027 ☑ 변경 의도 "필수 변경 파일" 선언 (`change_intent.expected_paths`) — 부재 탐지  (Codex)  *(MVP-2 보강 · 패치 생존성)*
**목적**: `change_intent.expected_paths` 로 "이 변경이 반드시 건드려야 하는 파일"을 선언하고, 실제 diff 가 그걸 안 건드리면(패치 유실) **승인요구**로 올린다. 존재 탐지만 있던 하네스의 첫 **부재 탐지**.
**배경**: 형 질문(2026-07-16, 벤더-브랜치 Q2). 상세 논거·적대분석 = `collab/decisions.md` D-059.
**입력**: 기존 TASK-001/021 동일(`<diff/ref>` + `change-intent.yaml`). **출력**: `--json` 에 `expected_paths`·`missing_expected` 추가.
**수용기준 (Claude 검수 체크리스트)**:
1. 신규 **선택** 필드 `change_intent.expected_paths`(glob/리터럴 리스트). **미선언/빈 리스트 → 기존 동작과 완전 동일**(하위호환). **🔴 #1 회귀 가드 — 기존 전 픽스처(현행 91/91) 무회귀**가 최우선.
2. **부재 탐지**: `expected_paths` 각 항목에 대해 **변경 파일 집합 중 하나도 매칭 안 되면**(기존 `match_glob` 재사용) `missing_expected` 에 그 항목 기록. `missing_expected` 비면 아님 → 최소 `approval_required`(exit 2). **차단(exit 1) 절대 금지.**
3. **판정 우선순위**: `forbidden_touched`→`blocked` 최우선 유지. 그 외 `out_of_scope` ∨ `scope_too_broad` ∨ `missing_expected` 중 하나라도 있으면 → `approval_required`. **🔴 빈 diff(변경 0건) + `expected_paths` 선언 → 전부 missing → `approval_required`**. (TASK-001 #6 "빈 diff=통과"와 상충 아님: `expected_paths` **선언이 있을 때만** 빈 diff 가 missing 으로 뒤집힌다. 선언 없으면 빈 diff 는 종전대로 pass.) — 이게 패치-유실의 핵심 신호.
4. 출력: `--json` 에 `expected_paths`(에코)·`missing_expected`(정렬). 텍스트 출력에 `missing_expected: {pattern}` 라인. 결정적(2회 동일).
5. **🔴 매칭 시맨틱 정직성(TASK-019 정직화 계보)**: 각 expected 항목은 "**변경 파일 중 ≥1 매칭이면 충족**". **리터럴 경로(`vendor/foo/A.py`)가 주 용도** — glob(`vendor/**`)은 "그 아래 아무 파일 1건만 변경돼도 충족"이라 **거친 보증**임을 게이트 출력/템플릿 주석/카드 coverage 문구에 명시(과신 방지). **rename**(name-status R = 목적지 경로만 changed 로 잡힘)·**delete**(경로가 changed 로 잡혀 수정/삭제 구분 안 함)의 한계도 문서화. 판정 cap 이 `approval_required`(사람 확인)라 거친 오탐도 **비파괴**(사람이 한 번 본다).
6. **🔴 상설 회귀 픽스처 + 음성검증**:
   - `expected-present`(선언 파일 전부 변경됨) → pass(missing 없음)
   - `expected-missing`(선언 파일이 diff 에 없음 = 패치 유실) → approval_required + `missing_expected` 에 그 파일
   - `expected-empty-diff`(변경 0건 + expected 선언) → approval_required(전부 missing)
   - `expected-none`(expected_paths 미선언) → 기존 판정 그대로(무영향·하위호환 실증)
   - 음성검증: 기대값(missing 목록/verdict) 변조 → FAIL(항상-PASS 아님).
7. **🔴 카드 미러링 필수** — `generate-change-evidence.py` 인라인 intent 로직(`load_intent`·`intent_result`·집계 verdict)에 `expected_paths`/`missing_expected` 동일 반영. **이유**: 킷 `run.sh` 는 `check-change-intent` 단독이 아니라 **`generate-change-evidence`(카드) 게이트를 intent 층으로 호출**한다 → 카드에 미러링 안 하면 킷에서 부재 탐지가 **안 돈다**(TASK-028 전제). 카드 스키마 키는 템플릿과 일치(임의 키 금지 — 필요 시 `templates/change-evidence.template.yaml` 동시 개정).
8. 템플릿·예시 갱신: `policies/change-intent.template.yaml`·`change-intent.example.yaml` 에 `expected_paths` 예시 + 벤더-브랜치 주석(패치 생존성 용도·**리터럴 권장**·glob 거친 보증 경고).
**산출**: `.harness/gates/check-change-intent.py`·`generate-change-evidence.py`(Codex 저자) + `tests/fixtures/` + `tests/cases.yaml`(+ 필요 시 템플릿). 통상 Codex 구현 → Claude 리뷰(비민감 intent 층 → Claude 머지 D-007).
**비고**: 첫 부재 탐지. 상한 `approval_required`(차단 없음)·기본 off(하위호환). 게이트 코드는 Codex 저자(Claude 미작성 — 상호견제).

### TASK-028 ☑ 킷에 `expected_paths` 반영 (부재 탐지 스냅샷)  (Codex)  *(MVP-2 킷 스냅샷)*  — **통과·머지완료(D-063 보정요청 → D-064 재리뷰통과, 2026-07-16)**
**배경**: TASK-027 로 dev 카드 게이트가 `expected_paths` 부재 탐지를 갖추면, 킷은 `sync-from-dev.sh` 로 그 게이트 사본을 받는 것만으로 **자동으로** 부재 탐지가 작동한다 — 킷 `run.sh` 가 이미 `generate-change-evidence` 를 intent 층으로 배선했기 때문(TASK-026/D-058). **★TASK-026 과 달리 신규 판정층 아님 → `run.sh` 배선 변경 불필요**(기존 카드 게이트 내부 확장). 따라서 이 태스크는 **경량 스냅샷 동기화 + 진입점 실증**.
**수용기준**:
1. `sync-from-dev.sh` 실행 → `kit/gates/check-change-intent.py`·`generate-change-evidence.py` 가 dev 최신본과 **바이트 동일**(`cmp` 확인, 누락검증 dev수==kit수 통과). 게이트 개수 무변화(16종 유지 — 기존 게이트 내부 확장).
2. `kit/tests/run-entrypoint-tests.sh` 에 **부재 탐지 진입점 케이스** 1종 이상 추가: 대상 repo `change-intent.yaml` 에 `expected_paths` 선언 + 그 파일을 **안 건드린** diff → 킷 `run.sh` 최종 exit 2(승인요구) + 카드에 `missing_expected` 노출. **rig-and-revert**(기대 2→0 변조 시 FAIL). 기존 진입점(11/11) 무회귀.
3. `manifest.yaml`/`README.md` 에 `expected_paths`(패치 생존성·부재 탐지) 능력 명기 — intent 층 설명 갱신. 버전은 MVP-2 point 추가 표기(예: `0.2.1-mvp2`, 강제 아님·Codex 판단).
4. `kit/selftest.sh` 전량 green + 부재 탐지 rig-and-revert 실증(§2B — "될 것 같다" 금지·fresh 적대입력 실제 실행). **`run.sh` 무변경 확인**(diff 로 `kit/run.sh` 무접촉 실증 — Claude 리뷰 체크).
**산출**: `kit/*`(Codex 저자·`run.sh` 미변경) + handoff/summaries. Codex 구현 → Claude 리뷰·머지(비민감 킷 스냅샷 — TASK-026 선례).
**의존**: TASK-027 통과·머지 후 착수(027 → 028).
**진행**: 2026-07-16 1차 제출(`c858c9b`) 리뷰 → **보정요청 R-1**(진입점 케이스가 load-bearing 아님 — 선언 수정이 diff 에 실려 exit 2 이중 원인·카드 grep 이 스키마 에코에 매칭. detection-kill rig 에서 12/12 유지로 실증). AC#1·#3·#4 는 통과 — **보정 커밋만 재리뷰**. 상세 `collab/answers/A-0022.md`·D-063. → 보정 커밋 `0f4d1a0` 재리뷰 **통과**(선언 선행커밋 분리 + reasons 정확 grep — detection-kill rig 에서 케이스 단독 FAIL 11/12 = load-bearing 회복·fresh 단독원인·음성검증 2종·selftest 96/96+12/12+mutation 161·sync 멱등). Claude main 머지(`d1e3c94`). **완결** — 상세 D-064. 비차단 O-D(out_of_scope 부재 단언 보강)는 TASK-033 에 병합 권고.

### TASK-033 ☑ 킷 `run.sh` 견고성 — intent 부재 크래시(bash 3.2) 수정 + 콘솔 부재탐지 표기  (Codex)  *(MVP-2 킷 후속 · D-063 O-A/O-B)*
**배경**: TASK-028 리뷰 중 발견한 **기존 결함**(main 킷 재현·TASK-028 도입 아님). ① 대상 repo 에 `change-intent.yaml` 이 **없으면** `set -u` + 빈 배열 확장(`"${INTENT_ARGS[@]}"`)이 bash<4.4(macOS 기본 3.2)에서 `unbound variable` 크래시 → **exit 1(차단 오인)·카드 미생성·2/3/메타층 미실행**. 과차단 방향이라 놓침은 아니나 배포 최전선 견고성 결함. ② 콘솔 1층 요약 grep 에 `missing_expected` 라인 미포함(카드에는 있음).
**수용기준**:
1. 빈 배열 확장을 bash 3.2 안전 관용구(`${INTENT_ARGS[@]+"${INTENT_ARGS[@]}"}` 류)로 수정 — intent 없는 repo 에서 크래시 없이 "의도이탈 층 생략" 정직 문구 + 나머지 층 정상 실행·판정·카드 생성. `run.sh` 내 다른 빈 배열 확장(`ANALYSIS_FAILURES` 등)도 전수 점검.
2. ~~진입점 케이스 추가: intent 없는 repo → (타층 무위반 시) exit 0 + 생략 문구 + 카드 생성.~~ **🔴 정정(D-065 · 2026-07-16 · Claude 오류)**: 원 AC 의 전제("exit 1 = 크래시 산물")가 **틀렸다** — bash≥4.4 에선 크래시 없이 게이트가 돌아 **설계된 `blocked`(exit 1)** 를 낸다(`load_intent`→`FileNotFoundError`→정직 카드 `reasons:[의도 선언 누락…]`·`coverage.checked: []`). 크래시 결함의 실체 = **카드 미생성·2/3/메타층 미실행·판정 없는 죽음** 셋뿐. → **정정 AC**: intent 없는 repo → **크래시 없이(`unbound variable` 부재) 게이트 자신의 판정이 그대로 흐른다**(현행 계약 rc=1·TASK-034 가 2 로 정규화하면 그때 갱신) + **카드 생성·비어있지 않음** + **2층/3층/메타층 전부 실행** + **카드 정직성 단언**(`reasons` 에 `의도 선언 누락` 존재 · `verdict: pass` 아님 · `in_allowed_paths: true` 부재 = 합성 주입 재유입 자동검출). **판정 완화 금지 — 합성 intent 주입 금지**(`allowed_paths:["**"]` 류 가짜 선언 = 카드 위조 + 의도층 우회). **`/bin/bash`(3.2)로 실행 실증** + **음성검증 필수**: 안전관용구를 `"${INTENT_ARGS[@]}"` 로 되돌리면 신규 케이스가 **단독 FAIL** 해야 한다(= 관용구가 load-bearing 임을 증명). 부수: 151행 `(change-intent.yaml 없음 — 의도이탈 층은 생략)` 문구는 실동작(층 생략 아님·게이트가 차단 판정)과 모순 → 사실 문구로 정정(표시만·판정 무변경).
3. 콘솔 1층 요약 grep 에 `missing_expected` 포함(O-B) — 판정 로직 무변경(표시만).
4. 기존 진입점·selftest 전량 무회귀 + rig-and-revert.
5. *(D-064 O-D 병합)* `expected-path-missing-approval` 케이스에 `out_of_scope` reasons **부재 단언** 추가 — 케이스 구성 드리프트로 exit 2 이중 원인이 재유입되면 자동 검출(현재는 단독 원인 실증 상태·가드 보강).
**산출**: `kit/run.sh`+`kit/tests/run-entrypoint-tests.sh`(Codex 저자). **의존**: TASK-028 보정 통과 후(028 → 033 → MVP-3 병행 가능·경량).
**진행**: 2026-07-16 1차 제출(`8e6b54b`) 리뷰 → **보정요청 R-1**(합성 intent 주입 = 카드 위조 + 의도층 우회 + AC#1 가드 dead code) · 코드 머지 보류. 검증 주장은 전부 재현(13/13·96/96·mutation 161)이나 크래시를 **가짜 `allowed_paths:["**"]` 선언 주입**으로 없애 카드가 없는 선언을 통과로 위조하고, `change-intent.yaml` 삭제만으로 forbidden/expected 층이 우회됨(bash≥4.4 에선 BLOCKED→PASS 회귀). **AC#3·AC#5 는 통과·재작업 금지.** AC#2 는 위와 같이 **정정**(Claude 오류 자인). 보정안·실증 = `collab/answers/A-0023.md`·D-065. **보정 커밋만 재리뷰**(멱등 — `8e6b54b`·`c8d8e7b` 재처리 금지). → 보정 커밋 `9769ece` 재리뷰 **통과**(D-066): 합성 주입 전량 제거 — 카드 정직성 회복(`verdict: blocked`·`checked: []`·`in_allowed_paths: true` 부재)·**fresh 적대 repo 에서 intent 삭제해도 BLOCKED 유지**(우회 소멸)·**RIG-A(관용구 원복)→단독 FAIL 12/13 = 가드 load-bearing 회복**·RIG-B(rc 변조) 단독 FAIL·96/96+진입점 13/13+mutation 161+sync 멱등·dev 무접촉. `run.sh` 델타 = 관용구 1줄+콘솔 grep 1줄+문구 정정. **비민감→Claude main 머지. 완결.** 다음 = **TASK-034**(rc 1→2 정규화). 비차단 O-E(225행 `+` 관용구는 가드 뒤 도달불가·무해). 상세 D-066·`review-notes.md`.

### TASK-034 ☑ "의도 선언 누락" 판정 정규화 — blocked(1) → approval_required(2) + 카드 정직 표기  (Codex)  *(D-065 · 정책 판정 Claude 완료 · **완결 D-068**)*
**배경**: TASK-033 리뷰 중 확인한 **선행 결함**(TASK-033 브랜치 탓 아님). `generate-change-evidence.py` 의 `load_intent` 는 `change-intent.yaml` 부재 시 `FileNotFoundError` → 카드 `verdict: blocked`(exit 1). 카드 자체는 정직하나(`reasons:['의도 선언 누락…']`·`coverage.checked: []`) **판정이 하네스 불변식과 충돌**: ① **"1층 frozen 만 차단"** — 미선언은 frozen zone 터치가 아니다 ② 러너 fail-closed 관례는 필수입력 부재·분석불가를 **approval_required(2)** 로 정규화한다(`run_gate` 실패→2 · `show_analysis_failure` "fail-closed → approval_required"). **Claude 정책 판정 = approval_required(2)** — 미선언은 "위반 확정"이 아니라 "검증 불가 → 사람이 본다".
**수용기준**:
1. `change-intent.yaml` 부재 → 카드 `verdict: approval_required`(exit 2). **`pass` 금지**(조용한 통과)·**`blocked` 금지**(1층 frozen 아님). reasons 에 안정적 기계판독 토큰 `intent_not_declared` 포함(현행 한글 문구는 유지 가능·둘 다).
2. **정직성 유지·강화**: `coverage_statement` 에 의도층 **미검사** 명시(`checked` 에 `check-change-intent` 를 **넣지 않는다**) + `not_checked` 또는 전용 필드로 "의도 미선언 — 의도이탈 미검사" 노출. `intent_check.status` 는 `pass` 가 될 수 없다(`not_declared` 신설 또는 `fail` 유지 — 스키마는 `templates/change-evidence.template.yaml` 동시 개정).
   **🔴 미검사 범위는 의도층 *뿐* (D-067 R-1)**: 민감경로층·@gov 함수층은 intent 를 입력으로 쓰지 않으므로 **미선언이어도 계속 검사하고 `checked` 에 정상 등재**한다. `sensitive_zone_check.status: not_checked` 로 통째 생략 금지.
   **🔴 카드 사실 보존 (D-067 R-2)**: 미선언 카드도 `summary.files_changed`·`changed_files`·`base_commit`·`policy_sha` 를 **실제값**으로 채운다. "변경 없음"이라 주장하는 것도 위조다(`files_changed: 0`·`changed_files: []` 금지 — 실제 변경이 있는 한). 정직성 = "검사 안 한 걸 했다고 안 함" **+ "본 사실을 안 봤다고 안 함"**.
3. **위조 방지 불변식**: 선언이 없으면 `changed_files[].in_allowed_paths` 는 `true` 가 될 수 없다(`null`/`false`/키 부재 중 택1·템플릿 명기). 러너·게이트 **어디서도 합성 선언 생성 금지**(D-065 R-1).
4. **하위호환**: 선언이 있는 기존 경로 전 판정 무변경(96/96 무회귀 = #1 가드). 빈 `allowed_paths` 선언(존재하나 비어있음) → 현행대로 전 변경 out_of_scope 승인요구(미선언과 구분 유지).
5. 고정 픽스처 + **음성검증**: 미선언 repo → exit 2·`intent_not_declared`·coverage 미검사 노출 각각 단독 단언, 기대 변조 시 FAIL. 킷 **sync 반영 + 진입점 케이스 rc 1→2 갱신**(TASK-033 보정 통과 후).
6. **🔴 미선언이 1층을 먹지 않음 — 고정 적대 픽스처 + 음성검증 (D-067 R-1 · 상설 회귀)**: 미선언과 1층 차단은 **독립**이다. ① **frozen 존 변경 + 미선언 → `blocked`(exit 1)** · 카드 `frozen_touched` 비어있지 않음 ② **`@gov(level=frozen)` 함수 변경 + 미선언 → `blocked`(exit 1)** · `changed_functions` 비어있지 않음 ③ 무해 경로 + 미선언 → `approval_required`(exit 2, = AC#1). 각 기대값 변조(1→2) 시 **단독 FAIL** 확인. 기존 `missing-change-intent` 픽스처 기대값도 **실제 변경 파일수로 정정**(현행 `files_changed: 0` 은 입력 `good/name-status.txt`=1건과 불일치하는 허위 계약).
**설계 주의(D-067)**: `build_evidence()` 가 미선언 시 abort 하면 `run.sh` 의 1층 판정 주체(`ge_exit`)가 사라져 **`change-intent.yaml` 삭제만으로 frozen 차단 우회**가 생긴다. 의도층만 `not_declared` 로 표시하고 파이프라인은 계속 돌릴 것. **합성 선언 주입은 금지**(D-065 R-1).
**산출**: `kit/gates/`·`.harness/gates/` 게이트 + 픽스처(Codex 저자) + `templates/change-evidence.template.yaml`(Claude 소유 — 개정 위임). **의존**: **TASK-033 보정 통과·머지 후**(진입점 케이스가 rc 계약을 고정하므로 순서 필수).
**진행**: 2026-07-16 1차 제출(`22fe433`) 리뷰 → **보정요청 R-1/R-2**(미선언이 1층 frozen 차단 무력화 + 카드 `files_changed: 0` 허위) · 코드 머지 보류 · **AC#6 신설**(D-067). → 보정 커밋 `9ecad20` 재리뷰 **통과**(D-068): `intent_not_declared_evidence()` 삭제·의도층만 `not_declared` 표시하고 파이프라인 계속(합성 선언 주입 없음)·`blocked > not_declared` 우선순위. **fresh 적대 실증**: frozen 경로+미선언 **2→1** · `@gov(frozen)` 함수+미선언 **2→1** · 무해+미선언 2 · 빈 선언은 `status: fail`(구분 유지) · **E2E `kit/run.sh` 🔴 BLOCKED(exit 1)·전층 실행**. 카드 정직성 회복(실제 `base_commit`/`policy_sha`/`files_changed`/`frozen_touched`+사유·`checked` 2종 등재·`in_allowed_paths: null`). **음성검증**: RIG-1 → frozen-zone 단독 FAIL(97/98) · RIG-2 → 미선언 3케이스 전부 FAIL(95/98) = 가드 load-bearing. 허위 픽스처 계약 정정 + 상설 회귀 2종 신설. 98/98·mutation 165·진입점 13/13·selftest PASS·게이트 16종 md5 동일. **AC 6/6 · 비민감 → Claude main 머지 · 완결.** 비차단 O-F(`kit/tests/run-tests.sh` 게이트 경로가 `.harness/gates` — 킷 단독 실행 0/98·**선재**·차기 킷 태스크에서 해소 또는 "dev 전용" 명시 권고)·O-G(분석실패 `blocked` — 선재·과탐 안전). 상세 D-068·`collab/answers/A-0025.md`·`review-notes.md`. **다음 = MVP-3(TASK-029~032).**

# MVP-3 (다국어 확장 — Java/Spring 우선)  *(설계 확정: `docs/multi-language-adapter-design.md`, 형 방향승인 2026-07-16, D-061)*

> **왜 MVP-3인가**: 깊은 층(함수레벨 `@gov`·신규능력·간접영향)이 Python `ast` 전용. 경로층은 이미 언어무관이라 작동하나 Java/Spring·프론트의 **함수·능력·영향**은 못 본다. **판정 엔진 하나 + 언어별 추출기** 구조로 다국어 확장.
> **🔴 최우선 합격기준 = 파이썬 동등성(parity)**(형 지시 2026-07-16 "가장 중요한 건 파이썬과 동일 성능"): 새 언어는 Python 과 ① 탐지 ② 엄밀성 ③ 정직성 ④ **안전 방향**(불완전 시 과탐 쪽·과소탐 절대 금지) **동등**. **교차언어 등가 픽스처**(같은 위험 클래스의 py판+java판 → 동일 verdict 단언)를 `tests/parity/` 상설 회귀로 강제. 정의 = 설계문서 §1.5.
> **확정 방향(형 승인)**: ① **Java/Spring 먼저**(은행 핵심 로직·Spring 어노테이션이 민감도 개념과 1:1·정적타입) ② **tree-sitter 백본**(Java/JS 파서), **Python `ast` 는 현행 유지**(무개조·무회귀 — 검증자산 보존).
> **불변 원칙 유지**: 1층 frozen 만 차단·2·3층 승인상한·LLM/추정 금지·결정적. 미지원/미해소는 **coverage 정직 노출**(TASK-019 계보).
> **핵심 seam**: 공통 IR 4종(인벤토리·능력·주석·콜그래프) + 확장자 라우터(파일별 분배·미지원=coverage). 상세 = 설계문서 §3.
> **parity 가 공짜 아닌 유일 지점 = L3(간접영향)**: Java DI/AOP/인터페이스로 이름기반 콜그래프가 실제 엣지를 놓침 → **보수적 과대근사**(인터페이스 호출→모든 구현체 엣지·`@Autowired`→모든 구현·프록시 직접엣지)로 **상위집합 산출 = 안전 parity 달성**(놓침 없음·과탐은 승인상한이라 감내). 정밀 parity 는 후속 네이티브 심볼솔버. 상세 = 설계문서 §5.
> **명시 비범위(설계 §7)**: cross-commit 누적(→ 후속 마일스톤·baseline 저장 필요)·타입기반 정밀 콜그래프(→ 네이티브 보강)·전 언어 동시.

### TASK-029 ☑ 다국어 어댑터 seam — 공통 IR 계약 + 확장자 라우터 + tree-sitter 도입  (Codex)  *(MVP-3 · J0)*  — **통과·머지완료(D-072, 2026-07-20)**
**목적**: 언어별 파서를 판정 엔진에서 분리하는 **배관**을 깐다. Java 파싱 자체는 J1 — 여기선 seam·라우터·정직성·의존 도입까지.
**수용기준**:
1. **공통 IR 4종 스키마 확정**(설계 §3.1) — 인벤토리·능력신호·거버넌스주석·콜그래프. 현행 Python 게이트 출력에 `lang` 필드 추가로 정합(스키마 문서화 + 예시). **기존 Python 게이트 로직 무개조**(필드 추가만·현행 91/91 무회귀 = #1 가드).
2. **확장자 라우터**: 바뀐 파일을 확장자→어댑터로 **파일별 분배**. 매핑은 **정책 파일**(`policies/language-routing.yaml` 신설 또는 기존 확장 — 하드코딩 금지). `.py`→python(기존 추출기 위임)·`.java`/`.js`/`.ts` 계열은 J1+ 에서 채우되 **자리(stub) 등록**. 결정적(확장자 기준·내용 추정 금지).
3. **🔴 미지원 확장자 fail-safe + coverage 노출**: 심층 어댑터 없는 확장자(`.go`·`.java`(J1 전)·기타)는 경로층은 그대로 판정하되 **감사카드 coverage 에 "심층분석 미지원: `<ext>`" 명시**. "지적 없음"을 "분석·안전"으로 오해하게 두지 않음(조용한 통과 금지). 픽스처: 미지원 확장자 변경 → 경로층 판정 유지 + coverage 노출 실증 + 음성검증(coverage 문구 누락 시 FAIL).
4. **tree-sitter 도입**: 의존 추가(prebuilt wheel) + Java/JS 문법 로드 **스모크 테스트**(파서가 실제 로드·파싱되는지 배포환경 실증). 결정성(같은 소스→같은 파스트리) 확인. `kit` 동봉·설치 경로 문서화(배포 시 의존).
5. 라우터·coverage 확장이 **기존 카드 스키마와 정합**(임의 키 금지 — 필요 시 `templates/change-evidence.template.yaml` 동시 개정). generate-change-evidence 카드에 coverage 언어 항목 반영.
6. **🔴 parity 기반장치**(설계 §1.5·§3.3): (a) **`tests/parity/` 그룹 신설** — 교차언어 등가 픽스처 러너 훅(J2·J3 가 케이스를 채움·같은 위험 클래스 py판+java판 동일 verdict 단언). (b) tree-sitter **문법 버전 고정(pin)** + 카드에 **언어별 파서/문법 버전 기록**(재현성 계약·Python parser 버전 계보). 라우터가 언어별 파서 버전을 coverage 에 노출.
**산출**: 라우터·IR 문서·정책(Codex 저자) + 픽스처 + tree-sitter 도입. **비고**: Python `ast` 무개조가 최우선. Java 파싱 없음(J1).
**진행**: 2026-07-19 1차 제출(`d1dbdca`) 리뷰 → **보정요청 R-1/R-2/R-3** · 코드 머지 보류 (D-069). 제출 주장 전부 재현(101/101 · tree-sitter 4문법 실로드 · pin=실설치본 · `ast` 무개조 · frozen `.java` fresh 실증 exit 1 + coverage 병기 · RIG-1 단독 FAIL). **R-1** `validate_inventory` 전체비교→부분비교 전환이 **가드를 죽임**(유령 아이템 rig: main FAIL 97/98 vs 브랜치 101/101 무음). **R-2** `language-routing.yaml` **부재 시 무음**으로 언어 coverage 전멸(형제 정책은 fail-closed) · 픽스처 0건. **R-3** 킷 무접촉 = AC#4 미충족 · dev↔kit md5 동일성 최초 균열((a) sync 또는 (b) "dev 전용" 명시 택1). 비차단 이월: **O-A** 카드에 파서/문법 버전 0건(AC#6b 부분) → **TASK-030 AC 로**, **O-B** `tests/parity/` 러너 훅 부재(AC#6a 부분) → **TASK-031 AC#7 전제로**, O-C `not_checked` dedup, O-D 스모크 환경의존. 상세 `collab/answers/A-0026.md`·D-069·`review-notes.md`.

### TASK-030 ☑ Java 함수/메서드 인벤토리 추출기 (tree-sitter → 공통 IR)  (Codex)  *(MVP-3 · J1)*  — **통과·머지완료(D-074, 2026-07-20)**
**목적**: `.java` 를 tree-sitter 로 파싱해 class/method/constructor 인벤토리를 **공통 IR #1** 로. Python 인벤토리와 동일 스키마 → `map-diff-to-functions` 헝크↔메서드 교집합·classify 재사용.
**수용기준**:
1. class/method/constructor **정규화 이름**(`Class.method`·중첩·이너클래스)·**시작/끝 라인범위**·**어노테이션 목록** 추출. `lang: java`.
2. 오버로드(동명·다른 시그니처)·중첩/이너 클래스·`static`/생성자 전부 포함. **🔴 동명 오버로드 가드**(TASK-007 계보): before/after 매칭 키를 이름 단독 아닌 `(정규화이름, 시그니처 또는 라인순서)` 로 — 오버로드 added/deleted/modified 오판 방지. 고정 적대 픽스처.
3. **🔴 어노테이션 라인 포함**(TASK-006 데코레이터 계보): 메서드 매핑 시작범위에 어노테이션 줄 포함 — `@PreAuthorize`·`@Transactional` **어노테이션만 변경**해도 해당 메서드에 매핑(미포함 시 인가·트랜잭션 변경을 놓침).
4. 파싱 실패(문법오류)·비-UTF8 → **파일 단위 격리**(형제 보존·빈 인벤토리+오류표시·fail-safe, TASK-013 계보). exit 0(보고용).
5. 결정적(md5 2회) + `--json`. `map-diff-to-functions` 가 Java IR 을 소비해 Java 헝크↔메서드 매핑 산출됨을 픽스처로 실증(공통 교집합 로직 재사용 확인).
**의존**: TASK-029 통과 후.

### TASK-031 ☑ Java `@Gov` + Spring 어노테이션 카탈로그 → 함수레벨 민감도  (Codex)  *(MVP-3 · J2)*  — **통과·머지완료(D-078, 2026-07-21)**
**목적**: Java 어노테이션을 민감도 신호로. 변경 메서드의 effective level → 기존 `check-function-gov-level` 판정 재사용(frozen=blocked/protected=approval/watched=warn).
**수용기준**:
1. `@Gov(level=, reason=, [owner=])` 파싱(문자열 리터럴 keyword) — Python `@gov` 규약 이식(strongest-wins 승계·중복필드 strongest·invalid→protected 보수, TASK-008 계보).
2. **🔴 Spring 어노테이션 카탈로그**(신규 정책 `policies/framework-annotations.yaml`, source/owner 메타 필수 — TASK-016 AC#8 계보): `@PreAuthorize`/`@Secured`/`@RolesAllowed`/`@PostAuthorize`→protected · `@Transactional`→watched · `@GetMapping`/`@PostMapping`/`@RequestMapping`→watched+진입점 · `@Query(nativeQuery=true)`/`@Modifying`→protected · `@Scheduled`/`@EventListener`/`@KafkaListener`→watched. **카탈로그 외부화**(코드 하드코딩 금지)·등급은 정책값.
3. **🔴 base∪head max**(TASK-009 계보): 어노테이션 *제거* 우회 방지 — 판정은 base·head 양측 주석의 max. `@PreAuthorize` 삭제+본문수정 시 base 지배.
4. 변경 메서드에 invalid/unresolved 주석·parse_error → 최소 approval(조용한 pass 금지·fail-closed).
5. **🔴 고정 적대 세트**(상설 회귀): `@Gov` 부착 메서드·Spring 인가/트랜잭션 어노테이션·오버로드·어노테이션 제거 PR 각각 + 음성검증(기대변조→FAIL). **+ 익명 내부클래스·로컬 클래스**(D-073 O-1 — J1 이 `Outer.run`·`Outer.Local` 같은 **실존하지 않는 이름**을 부여하므로, 이름으로 인가 등급을 귀속시키면 잘못된 함수에 붙는다) **+ 게이트 파일 결손**(D-074 O-4 — co-located 게이트 결손 시 파일단위 격리 + 형제 Python 보존; 이 경로 현재 픽스처 0건 = 미측정).
6. 결정적 + `--json`. 정직성: 어노테이션은 잡되 **AOP 프록시/DI 간접은 coverage 노출**(§5 — 이 층은 선언 기반이라 런타임 실제 적용 여부는 못 봄).
7. **🔴 parity 픽스처 + 러너 훅**(설계 §1.5 · D-069 O-B — 픽스처만이 아니라 **`run-tests.sh` 가 수집·집계해 `Group parity` 를 출력**하는 것까지가 AC. 두 태스크 연속 README 만 있었다): 이 층의 Python 대응 위험 케이스(민감함수 직접수정→frozen=blocked/protected=approval · 주석제거 우회→base 지배)와 **동일 verdict** 를 내는 **Java 등가 픽스처를 `tests/parity/` 에 쌍**으로 + 음성검증(한쪽 기대 변조 시 parity FAIL). Spring 카탈로그 신호는 Java 고유 초과분이라 등가 대상 아님 — `@Gov` 대칭 케이스로 parity 단언.
8. **🔴 정책 계약·불변식**(Q-0005·A-0032·**D-075** — 정책 파일은 Claude 작성 완료, 수정 금지):
   (a) 스키마 = `annotations` **리스트**(형제 `sensitive-capabilities.yaml` 동형) · 항목 = `{name, level, entrypoint, reason, reviewer, fqns?, when?, source, owner}` · **중복 `name` = 검증오류**.
   (b) **🔴 매칭은 어노테이션 이름의 마지막 점-세그먼트 기준** — `@PreAuthorize` 와 FQN 인라인 `@org.springframework...PreAuthorize` 를 **둘 다** 잡을 것(원문 토큰 비교 시 **과소탐**). `fqns` 는 감사용이며 매칭에 쓰지 않는다.
   (c) **인자 조건 `when`**(`@Query(nativeQuery=true)` 만 신호, JPQL `@Query` 는 무신호) · 값이 결정적으로 **미해소면 추정 금지·매칭 취급**(`defaults.unresolved_argument: match` — 과탐 반올림).
   (d) **🔴 이 카탈로그는 `frozen` 을 만들 수 없다**(추론 신호 = 2·3층 자동차단 금지 · D-004). 정책에 frozen 오면 **검증오류 + protected clamp**. ↔ `@Gov(level=frozen)` 은 명시 선언이라 blocked 가능 ⇒ 게이트는 **declared vs inferred 출처를 구분해 보존**(뭉쳐 max 만 취하면 카탈로그가 frozen 을 만드는 경로가 열림).
   (e) **`entrypoint` 는 판정 무영향** — verdict 는 `level` 에서만. 카드 메타데이터 + 후속 L3 진입점 시드로만 사용(등급 드리프트 금지).
   (f) **정책 부재 fail-closed**: 명시됐는데 부재 → `approval_required` + 사유(**차단 금지**). **`kit/run.sh` 에 `$POL/framework-annotations.yaml` 절대경로 배선 + preflight 필수정책 루프 추가**(TASK-029 **R-4** 재발 방지 — 동일 패턴 3회차 금지) + 해당 회귀 픽스처.
9. **🔴 Java `stub → supported` 전환 조건**(D-074 O-5 승격 — 이걸 못 지키면 `stub` 유지가 정직):
   (a) `language-routing.yaml` 에 **층별 `layers:`**(`inventory`/`gov_level`/`capabilities`/`callgraph`) 도입 — J2 시점 java = inventory·gov_level 만 supported, **capabilities 는 stub**(J3 미착수). python 도 동형 부여. dev+kit 동시.
   (b) 소비자는 `layers.<layer>` 를 읽고 **`supported` 정확일치만 available**(`partial`·미지값은 available 아님 = fail-safe). 현행 `route["status"] == "supported"` 단일 비교(`language-router.py:117·120·125`)를 교체.
   (c) 카드 coverage 를 **층별로 서술** — 언어 단위 이분법으로는 "인벤토리는 했고 능력은 안 했다"를 표현할 수 없다.
   (d) **🔴 가용성은 정책이 아니라 실측**: `parse_error`(파서/문법 부재 등) 파일은 정책 status 와 무관하게 **카드 미분석 목록에 노출**. 미구현 시 `supported` 플립은 **열화됐는데 정상이라 말하는 허위 카드**가 된다.
   (e) 회귀 픽스처(**현재 0건 = 미측정**): 파서 부재 강제 + 정책 supported → 미분석 노출·`exit 0` / 층별 문구가 capabilities 미분석 명시 / 각각 **음성검증 단독 FAIL**.
**의존**: TASK-030 통과 후.

### TASK-032 ☑ Java 능력 카탈로그 + 신규능력 감지  (Codex)  *(MVP-3 · J3)*  — **통과·머지완료(D-080 → 킷보정 D-082, 2026-07-21)**
**목적**: Java 위험 능력을 카탈로그로 추출 → 기존 `check-new-capabilities`(base..head 신규 도입만 approval) 재사용. 2층 불변식(자동 차단 금지·승인상한).
**수용기준**:
1. Java 능력 카탈로그(`sensitive-capabilities.yaml` 확장 또는 언어별 분리·source/owner 메타): `Runtime.exec`/`ProcessBuilder`(command_exec) · `ObjectInputStream.readObject`(unsafe_deserialization) · `Class.forName`/`Method.invoke`(reflection) · 문자열 SQL `Statement.execute*`(sql_injection_surface) · `Cipher`/`MessageDigest`(crypto) · `InitialContext.lookup`(jndi_lookup) · `RestTemplate`/`WebClient`/`HttpClient`(outbound_http). 등급은 정책값(protected 상한·frozen 오면 clamp — 2층 불변식).
2. **신호 3종 이식**(TASK-010 계보): import 신호(`import` 문)·call 신호(정규화 호출이름)·해소불가 동적(리플렉션)→`unresolved_dynamic` 노출. import backstop 원칙. **🔴 Java import 뉘앙스**: `java.lang.*`(`Runtime` 등)는 **암시적 import**(import 문 없음) → Python import-backstop 이 그대로 안 통함. `java.lang` 계열은 **call 신호로 커버**(import 없어도 `Runtime.getRuntime().exec` 잡힘). 명시 import 모듈(`java.io.ObjectInputStream` 등)은 import backstop 유효. 이 비대칭을 픽스처로 고정.
3. **🔴 Java 대응 우회 벡터 고정 적대 세트**: 리플렉션 경유 호출(`Method.invoke`)·문자열 조립 SQL·`Class.forName("...")` 동적 로드 각각 + 음성검증. (Python `getattr` 난독의 Java 대응 — parity 축2 엄밀성 동등.)
4. **base..head 신규 도입만**(TASK-011 계보): 양쪽 있으면 미감지·head 만 신규·삭제 안전. never-blocked 불변식(approval 상한·exit 1 없음). fail-closed(head 파싱실패→per-path approval).
5. 결정적 + `--json`. 정직성: 값추정 금지·동적 미탐 coverage 노출.
6. **🔴 parity 픽스처**(설계 §1.5): Python 신규능력 대응(신규 위험능력 도입→approval · 양쪽 존재→미감지 · 삭제 안전)과 **동일 verdict** 를 내는 **Java 등가 픽스처를 `tests/parity/` 쌍**으로 + 음성검증(한쪽 기대 변조 시 parity FAIL).
7. **🔴 frozen clamp 를 코드 하드 플로어로**(D-077 O-2 폐쇄 · 비차단으로 미루지 않음): 2층 never-blocked 불변식을 **정책 파일의 `allowed_levels` 만 읽어** 판단하지 마라 — 그러면 정책을 고쳐 불변식을 끌 수 있다. 게이트 **코드에 하드코딩된 상한**(능력 카탈로그발 판정은 `approval_required` 초과 불가)을 두고, 정책값은 *더 좁히는* 방향만 허용한다. 검증: 정책을 `level: frozen` + `allowed_levels: [frozen]` 로 **동시에 rig** → 여전히 검증오류 + `protected` clamp + verdict ≤ approval_required. 음성검증(하드 플로어 제거 시 단독 FAIL) 필수.
8. **🔴 시험용 env override 게이팅**(D-078 O-1 폐쇄 · 비차단으로 미루지 않음): `ACGH_JAVA_INVENTORY_PATH` 계열 **임의 파이썬 파일 실행** 경로는 프로덕션 기본값에서 **비활성**이어야 한다 — 명시 시험 플래그(예: `ACGH_ALLOW_TEST_OVERRIDES=1`) 없이는 무시하고 그 사실을 coverage 에 남긴다. TASK-032 가 새로 env override 를 추가한다면 동일 규칙 적용. 검증: 플래그 없이 override 지정 → 무시 + 정상 판정 유지, 플래그 있으면 동작.
9. **🔴 정책 파일은 별도 · Python 게이트 오염 금지**(Q-0007 · D-079): Java 카탈로그는 `policies/java-sensitive-capabilities.yaml`(**Claude 소유 · 신규 · 이미 커밋됨**)에서 읽는다. `policies/sensitive-capabilities.yaml` **수정 금지** — Java 항목을 공유 파일에 넣으면 Python 추출기가 `unknown_signal_kind` 오류를 내고 `check-new-capabilities` 가 **Java 무관 순수 Python PR 까지 전부 approval_required** 로 만든다(A-0036 실측). **회귀 픽스처 필수**: 무해한 Python 전용 PR → `pass`/exit 0 유지(이 픽스처가 오염을 잡는다) + 음성검증. Python 추출기 `extract-python-capabilities.py` 는 **무개조**(통과·배포된 층에 손대지 않는다).
10. **킷 배선**(TASK-029 R-4 계보 — 3회 연속 누락 방지): `kit/policies/java-sensitive-capabilities.yaml` **sync 반입**(dev↔kit md5 동일) + `kit/run.sh` 에 Java 능력 게이트 배선(`JAVA_CAPS` 변수 · verdict max 조립 · 정책 부재 preflight · `--policies` 오버라이드 경로) + 진입점 테스트. `run.sh` 는 Java 카탈로그를 **Java 게이트에만** 넘긴다(교차 소비 시 11건 검증오류 = 시끄럽게 실패하지만 애초에 배선하지 마라).
11. **language-routing 승격은 Claude 가 한다**(Q-0007 Q5): `java.layers.capabilities` 는 이 태스크 **리뷰 통과 전까지 `stub` 유지**. Codex 는 `policies/language-routing.yaml` 을 건드리지 않는다. 통과 후 Claude 가 `supported` 로 올리고 `status:` 하한도 재평가한다(D-076 under-claim 계약).
**의존**: TASK-031 통과 후. **정책 선행조건 충족**: `policies/java-sensitive-capabilities.yaml` · `collab/answers/A-0036.md` · D-079.

**MVP-3 의존·순서**: 029(seam) → 030(인벤토리) → 031(주석/Spring) → 032(능력). J 라인 **완결**(2026-07-21). 이후: **035(잔손질) → 036·037(X = Java 간접영향 L3) → 038(킷 반영)** → 그 다음 W1(프론트) AC 정밀화.

# MVP-3 X 단계 — Java 간접영향(L3) + 잔손질 + 킷  *(설계 D-083, 2026-07-21 · 형 지시 "자바까지 완성 후 킷 업데이트")*

> **왜 X 인가(parity)**: J 라인(029~032)으로 Java **직접 탐지**(함수·@Gov/Spring·능력)는 완결됐으나, **간접영향(L3 = sink 역도달성)은 Java 에서 stub** — Python(MVP-2)엔 있는 층이 Java 엔 없다 = **parity 구멍**(D-062 최우선 원칙 위반). 프론트(W1) 얹기 전에 이 구멍을 닫아 Java↔Python parity 회복.
> **현행 코드 사실(2026-07-21 확인)**: `check-indirect-impact.py`·`extract-callgraph.py`·`extract-sinks.py` 는 **아직 `.py` 하드코딩**(언어중립 아님). `language-router` 는 `callgraph` 층을 알지만 `java.layers.callgraph=stub`. → X = **Java 콜그래프/sink 추출기 신설 + 간접영향 게이트 언어중립화**.
> **불변 원칙**: 차단 절대 금지·승인요구 상한(MVP-2 L3 동일). Python 골든패스(간접영향 기존 픽스처) **무회귀 최우선**.

### TASK-035 ☐ MVP-3 J 라인 잔손질 — 열린 관찰 7건 폐쇄  (Codex)  *(D-080·D-082 O-건 소진)*
**목적**: W1(프론트)로 같은 결함을 복제하기 전에, J 라인이 남긴 관찰 7건을 닫는다(소규모·Codex 1회전 목표).
**수용기준**:
1. **🔴 (D-080 O-1·위험 최대) 언어 카탈로그 지연 로드(lazy load)**: 변경에 `.java` 가 **하나도 없으면** Java 정책/카탈로그를 **로드하지 않는다** — 현재는 무조건 선로드라 **Java 정책 부재 시 순수 Python PR 이 exit 2 오작동**(D-079 실패모드 dev 경로 재진입). 검증: `.py` 만 바뀐 PR + Java 정책 부재 → **pass/exit 0**(회귀 픽스처 + 음성검증). 킷 preflight 도 동일 원칙 재확인.
2. **(D-080 O-2) 무정보 바인딩 미탐 씨앗**: Java `var`/`Object` 무정보 바인딩이 `unresolved_dynamic` 노출을 **억제하지 않도록** — 해소불가 호출은 반드시 coverage 로 노출(조용한 미탐 방지). 픽스처 고정.
3. **(D-080 O-3) coverage 문구 이행**: `ACGH_*_OVERRIDE` 무시 사실을 coverage 문구에 실제 반영(AC#8 override 게이팅의 정직 표기).
4. **(D-082 O-1) 킷 진입점 grep 정확일치**: `run-entrypoint-tests.sh` 의 층 문구 grep 이 **접두 부분일치**라 층 회귀 맹점 — 정확일치(또는 경계 앵커)로 좁혀 회귀를 실제로 잡게. 음성검증(층 문구 변조 시 FAIL).
5. **(D-082 O-2) capabilities 실패 카드 trace 대칭**: `gov_level` 은 분석실패 흔적을 카드에 남기는데 `capabilities` 는 안 남김(D-076 trace 계약 비대칭) — capabilities 분석 실패도 카드에 trace 노출.
6. **(D-082 O-3) `kit/manifest.yaml` J3 반영**: manifest 가 J3(Java 능력) 미반영 — 게이트 목록·버전 갱신.
7. **(D-082 O-4) 정책 `status:` 주석 스테일 정리**(사소).
**비고**: 판정 로직 변경 최소·대부분 정직성/위생. O-1 만 실판정 영향(과차단 제거) → 회귀 픽스처 필수. Codex 저자·Claude 리뷰.

### TASK-036 ☐ Java 콜그래프 추출기 (tree-sitter → 공통 IR · 보수적 과대근사)  (Codex)  *(MVP-3 · X · Java L3-a)*
**목적**: `.java` 함수 호출 엣지를 결정적으로 빌드해 **공통 IR #4**(`edges`·`unresolved_calls`)로. 판정 미연결(그래프 산출만). TASK-023(Python 콜그래프) 대응.
**수용기준**:
1. tree-sitter 로 메서드 정의별 호출 수집 → **repo 내 메서드로 해소되는 호출만 엣지**(caller→callee, 정규화 이름 `Class.method`). TASK-030 인벤토리·TASK-031 어노테이션 재사용.
2. **🔴 보수적 과대근사(설계 §5 · parity 안전방향)**: 정적으로 대상이 불확정인 호출을 **버리지 말고 상위집합으로 연결** — ① **인터페이스 메서드 호출 → repo 내 그 인터페이스의 모든 구현체(`implements`/`extends` 열거)로 엣지** ② **`@Autowired`/생성자 주입 필드 → 그 타입의 모든 구현으로 해소** ③ **`@Transactional`·AOP 프록시 경유 → 직접 엣지로 취급**(프록시 무시). 결과 = 실제 런타임 엣지의 superset(진짜 엣지 안 놓침).
3. **해소 실패 호출**(리플렉션·완전 동적·컨테이너 밖 배선)은 버리지 않고 `unresolved_calls`/`coverage.unevaluated` 로 노출(조용한 누락 금지·ADR-001 D4).
4. **결정론**(md5 2회) + `--json`. 동명 오버로드·조건부 정의는 보수적 병합(합집합).
5. **🔴 고정 적대 세트**: 인터페이스 다형성(1인터페이스 N구현)·`@Autowired` 주입·리플렉션 미해소 각각 + 음성검증(과대근사 무력화 시 참케이스 엣지 소실 → FAIL). **parity 픽스처**: 동일 구조 Python 콜그래프와 엣지 도달성 등가(구조 대응).
**의존**: TASK-035 후(또는 병행 가능). Python `extract-callgraph.py` **무개조**(별도 Java 추출기 신설).

### TASK-037 ☐ Java sink 추출 + `check-indirect-impact` 언어중립화 + Java 간접영향 배선  (Codex)  *(MVP-3 · X · Java L3-b — Java L3 완결)*
**목적**: Java sink 을 등록하고, 간접영향 게이트를 **언어중립화**해 Java 콜그래프(TASK-036)를 소비 → 바뀐 Java 함수가 sink 상류면 승인요구. TASK-022·024·025(Python L3) 대응.
**수용기준**:
1. **Java sink 추출**(TASK-022 대응): frozen-zone Java 함수 자동 sink · `@Gov(sink=true)` Java 어노테이션 · `sink-registry` 명시 등록. 일반 @Gov·protected 는 sink 아님. `extract-sinks.py` 를 어댑터 분기(Java 추출)로 확장하거나 Java sink 추출기 신설.
2. **🔴 `check-indirect-impact` 언어중립화**: 현행 `.py` 하드코딩(라인 55·76·`extract-callgraph`/`extract-sinks` 직접호출)을 **어댑터 분기**로 — 변경 파일을 language-router 로 라우팅해 언어별 콜그래프·sink 을 **병합**해 판정. **🔴 Python 골든패스 무회귀 최우선**(기존 Python 간접영향 픽스처·85+ 스위트 전량 유지 = #1 가드).
3. 바뀐 Java 함수 ∈ (sink 로부터 forward N홉) → `indirect_impact`+최소 `approval_required`. **차단 금지**(exit 0/2 만). 감사필드 `sink_id`·`changed_function`·`path`·`hops`. 라우팅 = sink owner. 분석실패 → fail-closed(tool_owner·최소 approval).
4. N홉 = 정책값(기본 1·하드코딩 금지). shadow 성숙도 지원(신규 sink shadow 시작).
5. **🔴 parity 픽스처(설계 §1.5 · 이 태스크의 핵심 합격기준)**: MVP-2 의 Python 간접영향 대표 케이스(sink 상류 함수 수정→approval · 무관 수정→pass · N홉 경계)와 **동일 verdict** 를 내는 **Java 등가 픽스처를 `tests/parity/` 쌍**으로 + 음성검증. **과대근사 정직성**: Java 미해소 동적은 `coverage.unevaluated` 노출을 테스트로 고정.
**의존**: TASK-036 통과 후. → **통과 시 Java L3 완결 = Java↔Python parity 회복.**

### TASK-038 ☐ 킷에 Java L3 + 잔손질 반영 (MVP-3 킷 스냅샷 갱신)  (Codex)  *(MVP-3 · X · 킷)*
**배경**: TASK-035·036·037 로 dev 가 Java 전 계층(J1~J3 + L3) 완비되면 킷을 그 상태로 올린다(형 지시 "자바까지 하고 킷 업데이트"). TASK-026/028 킷 스냅샷 선례.
**수용기준**:
1. `sync-from-dev.sh` → 신규 Java 콜그래프/sink 추출기 + 언어중립화된 `check-indirect-impact` + 정책이 킷에 반영(dev↔kit md5 동일·누락검증 통과·게이트 수 갱신).
2. `run.sh` 에 **Java 간접영향층이 기존 간접영향 배선을 통해 작동**(언어중립화 덕에 별도 배선 불필요할 수 있음 — 확인). `--policies`·sink-registry 오버라이드 일관. 정책 부재 fail-safe.
3. `manifest.yaml`/`README.md` — Java L3(callgraph·sink) 반영·"Java 간접영향 지원" 명기. `language-routing.yaml` `java.layers.callgraph` **stub→supported 승격은 Claude 가**(리뷰 통과 후·D-076 계약).
4. `kit/selftest.sh` 전량 green + **Java 간접영향 rig-and-revert**(sink 상류 Java 함수 수정→승인요구·fresh 적대입력). 기존 진입점 무회귀.
5. **(D-085 G-1·G-2·G-3 — TASK-035 재리뷰 신규 발견 · 킷 콘솔/가드 정직성)** 아래 3건을 닫는다. 전부 판정 무영향이라 **출력·테스트 계층만** 손댄다(판정 로직 변경 금지):
   - **🔴 G-1 `try/except` 가드 고정**: `run.sh` `append_capability_trace` 의 두 가드 중 **`isinstance` 쪽만 픽스처에 고정돼 있고 `try/except` 는 제거해도 진입점 26/26 PASS** 다(D-085 실증). 원인 = 기존 리그 `raise RuntimeError("forced evidence failure")` 가 **YAML dict 로 파싱되는 형태(V1)** 라 `safe_load` 가 예외를 안 던짐. → **예외 메시지에 콜론이 든 리그**(예: `raise RuntimeError("boom: bad value: x")` → `ScannerError`, 형태 V2) **진입점 케이스 1건 추가** + **음성검증**(`try/except` 만 제거 시 그 케이스 단독 FAIL·PyYAML traceback 재출현). 두 형태 모두 **최종 verdict·exit 불변** 단언 포함.
   - **G-2 게이트 출력 파싱 실패 고지**(카드 실패와의 비대칭 해소): `run_gate` 가 `2>&1` 이라 게이트가 **stderr 를 한 줄이라도 뱉고 정상 exit** 하면 `json.loads` 가 깨져 **2층 블록이 헤더만 남고 완전 무출력**이 된다. → `if result:` 에 **`else` 고지 1줄**(예: `능력 게이트 출력 파싱 불가 — 원문 앞 N줄`) + 회귀 케이스. 판정은 지금도 fail-closed 이므로 **고지만** 추가.
   - **G-3 shadow 렌더 `level=` 복원**: 현행 `shadow: path::id` 는 게이트 `print_text` 의 `shadow: path::id level=<level>` 대비 등급을 잃는다. → `level=` 복원(1줄) + `maturity: shadow` 픽스처로 고정.
**의존**: TASK-037 통과·머지 후 착수. **단 AC#5 는 TASK-036/037 과 무관**하므로 먼저 처리해도 된다(권장 — 회귀 픽스처 공백 기간 단축).

## MVP-3 공통 (Codex)
- **🔴 파이썬 동등성(parity) = 최우선 합격기준**(형 지시): 각 J-태스크는 Python 대응층과 **동일 성능**을 실증해야 통과. **교차언어 등가 픽스처**(`tests/parity/`·py판+java판 동일 verdict 단언 + 음성검증)가 없으면 미완. 불완전성은 **항상 과탐(approval) 쪽으로 반올림 — 과소탐(놓침) 금지**(놓침 = parity 위반). 정의 = 설계 §1.5.
- **tree-sitter 허용**(Java/JS 파서). **Python 은 `ast` 유지**(tree-sitter 로 이관 금지 — 무개조·무회귀). 문법 버전 pin + 카드 기록(재현성).
- 새 언어라도 판정 불변식 동일: 1층 frozen 만 차단·2·3층 승인상한·LLM/추정 금지·결정적.
- 미지원 확장자·미해소 호출·프레임워크 간접(DI/AOP) 은 **coverage 정직 노출**(조용한 통과 금지). L3 간접영향은 **보수적 과대근사로 안전 parity**(설계 §5).
- 판정 게이트는 **공통 IR 만 소비**(언어중립) — 언어 종속은 추출기(어댑터)에 격리.

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
