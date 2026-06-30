# decisions.md — 확정 결정 (대화 ≠ 결정. 여기 적힌 것만 확정)

> Q/A 에서 합의된 것을 결정으로 승격한다. 번호·날짜·근거를 남긴다.

---

## D-001 (2026-06-28) 민감함 기준 = 경로(MVP-0) → 능력·데이터(MVP-1+)
경로는 약한 대리표지. MVP-0 은 경로기반으로 시작하되, 능력/데이터 기반을 MVP-1 로 확장한다.
근거: 신규 코드·재사용 모듈은 경로만으로 판단 불가.

## D-002 (2026-06-28) sensitive-zones 와 sensitive-capabilities 분리
경로기반·능력기반은 판정기준·감지방식이 달라 별도 정책으로 둔다. verdict 스키마(level+approval)는 공통.

## D-003 (2026-06-28) 공유 모듈 = "민감 모듈" 아님, "영향범위 큰 모듈"
분류 대신 도달범위(importers/민감 호출자 수) 표시. MVP-0 은 watched 경고, 정밀 산출은 MVP-2.

## D-004 (2026-06-28) 3층 자동차단 정책
1층(경로)만 차단 가능. 2·3층은 승인요구/참고로만 시작(오탐 관리). tier 는 규칙별 policy 선언, 승격 가능.

## D-005 (2026-06-28) 자기 머지 금지 (dogfooding)
이 repo 변경도 이 하네스 규칙 적용. main 머지는 상대 리뷰 통과(+민감변경은 사람 승인) 후에만.

## D-006 (2026-06-29) TASK-001 `check-change-intent` 리뷰통과
대상 commit: `ff75529` (브랜치 `codex/2026-06-29-task001-change-intent`).
수용기준 6/6 충족 — 경험적 검증(name-status 입력 8케이스 + glob 엣지 4케이스)으로 확인.
보수성: Codex 소유 파일(`.harness/gates/check-change-intent.py`)만 신규 + 허용된 handoff/summary 기록.
Claude 소유 파일 미수정·무관 리팩터 없음 — scope-creep/over-reach 없음.
판정 우선순위 확정(이 게이트 한정): **forbidden(blocked,1) > out_of_scope(approval,2) > pass(0)**.
부수 결정: **change-intent.yaml 누락 = blocked(exit 1)** 로 확정(거버넌스 불가 → fail-closed). TASK-004 fixture 는 이 기대로 작성.
상세·비차단 관찰사항: `review-notes.md` 참조.

## D-007 (2026-06-29) 머지 주체 정책 = A (비민감 Claude 자동 / 민감 사람) — 형 결정
D-005 의 운영 세부. **Codex 는 개발만**(자기 머지 금지). main 머지는:
- **비민감 변경**: Claude 리뷰 통과 시 **Claude 가 main 에 머지·push** (구현자≠머지자라 상호견제 유지).
- **민감 변경**(frozen/protected, 또는 정산·이자·자금이체·인증/인가·암호화·DB migration·infra 등 `CLAUDE.md` 리스크표 🔴🟠): **머지 보류** → `collab/needs-human/H-XXXX.md` 로 형 승인 요청 후에만 머지.
- 리뷰 **보정요청**: 머지하지 말고 `collab/answers/` 로 반려.
근거: 부트스트랩 속도 ↑ 하되 위험 변경은 사람 게이트 유지. (B=전부자동/C=항상사람 은 형이 반려)

## D-008 (2026-06-30) TASK-002 `check-sensitive-zones` 리뷰통과 + Claude 머지
대상 commit: `704f7a0` (브랜치 `codex/2026-06-30-task002-sensitive-zones`).
수용기준 6/6 충족 — 경험적 검증(name-status 입력 6케이스 + 엣지 6케이스)으로 확인.
- AC5(하드코딩 금지) 확증: policy 의 `protected` 를 `block_levels` 로 옮기니 auth 가 차단으로 바뀜 → defaults 를 코드가 아닌 policy 에서 읽음.
- AC6(가장 강한 level): 경로별 `strongest_records` 로 frozen>protected>watched 채택. mixed diff 에서도 세 목록 전부 증거(path+zone+reason+required_approval) 보존.
보수성: Codex 소유 파일(`.harness/gates/check-sensitive-zones.py`)만 신규 245줄 + 허용된 handoff/summary 기록. Claude 소유 policy(`sensitive-zones.yaml`) 무수정·무관 리팩터 없음 — scope-creep/over-reach 없음.
판정 우선순위(이 게이트 한정): **frozen(blocked,1) > protected(approval_required,2) > watched/pass(0)** — TASK-001 종료코드 계약(0/1/2)·fail-closed(except→blocked 1)와 일관.
**머지 판정(D-007)**: 변경 대상이 하네스 게이트 코드(`.harness/gates/`)로 생산 정산·인증/인가·암호화·DB migration·infra 경로 미접촉 → **비민감**. TASK-001 과 동일 범주(선례: Claude 머지). 구현자(Codex)≠머지자(Claude) 성립 → **Claude 가 main 에 머지**.
상세·비차단 관찰사항: `review-notes.md` 참조.

## D-009 (2026-06-30) TASK-003 `generate-change-evidence` 리뷰통과 + Claude 머지
대상 commit: `f2ecb50` (브랜치 `codex/2026-06-30-task003-evidence`).
수용기준 5/5 충족 — 경험적 검증(name-status/numstat 시나리오 8종 + 실제 git ref)으로 확인.
- AC1(zone_level·in_allowed_paths): admin 파일=free/allowed, common=watched, auth=protected, settlement∩common=frozen(가장 강함 채택) — 정확.
- AC2(verdict 합성): `frozen 또는 forbidden → blocked` > `protected 또는 out_of_scope → approval_required` > `pass`. settlement→blocked, auth(forbidden)→blocked, crypto(protected+out_of_scope)→approval, allowed-only→pass 로 확증. TASK-001/002 종료코드 계약(0/1/2)·우선순위와 일관.
- AC3(reviewer 중복제거): auth×2+security+crypto 4파일 → `security-reviewer` 단일. multi-route 파일(settlement∩common)은 settlement-owner+module-owner 둘 다 보존하되 전체 dedup. review-notes #2(TASK-002) 의 중복레코드 정리 요청 충족.
- AC4(base_commit·summary): git ref 입력 시 `base_commit`=실제 `rev-parse` 해시(=main), summary 파일/라인 수(482) 정확. (name-status 파일 단독 입력 시 base_commit="unknown"·라인 0 — 비차단 관찰 #2).
- AC5(템플릿 키 일치): 최상위/중첩 키 전부 일치, 임의 최상위 키 추가 없음. `*_touched` 리스트 항목의 {path,zone,level,reason,required_approval} enrich 는 템플릿이 빈 리스트로 둔 항목 스키마이며 TASK-002 에서 이미 수용된 계약(비차단 관찰 #1).
보수성: Codex 소유 파일(`.harness/gates/generate-change-evidence.py`)만 신규 476줄 + 허용된 handoff/summary 기록. Claude 소유 파일(`templates/`·`policies/`) 무수정·무관 리팩터 없음 — scope-creep/over-reach 없음. 결정성(2회 실행 동일)·fail-closed(except→blocked 1) 확인.
**머지 판정(D-007)**: 변경 대상이 하네스 게이트 코드(`.harness/gates/`)로 생산 민감경로 미접촉 → **비민감**. TASK-001/002 동일 범주(선례: Claude 머지). 구현자(Codex)≠머지자(Claude) 성립 → **Claude 가 main 에 머지**.
상세·비차단 관찰사항: `review-notes.md` 참조.

## D-010 (2026-07-01) TASK-004 테스트 fixtures + 러너 리뷰통과 + Claude 머지
대상 commit: `93e2c40` (브랜치 `codex/2026-06-30-task004-tests`).
수용기준 4/4 충족 — 경험적 검증(`bash tests/run-tests.sh` 실행 → 6/6 PASS, exit 0)으로 확인.
- AC1(6 fixture): good/out-of-scope/forbidden/frozen/protected/watched 전부 존재. fixture 가 정책과 정합(rigged 아님) 확증 — settlement→frozen, auth→protected(security-reviewer), lib/common→watched, good(app/features)→free & allowed_paths 안.
- AC2(cases.yaml): 케이스마다 `gate`·`input`·`expect`(verdict/exit_code + 게이트별 touched/paths) 선언. 게이트별 호출(check-change-intent·check-sensitive-zones·generate-change-evidence) 분기.
- AC3(러너): `run-tests.sh` 일괄 실행 + `Summary: N/M PASS` 요약. **음성 검증**: frozen 기대값을 pass 로 변조하니 `FAIL frozen` + `Summary: 5/6` + exit 1 → 항상-PASS 가 아니라 실제 불일치를 잡음. exit code 가 python→bash 로 정확히 전파.
- AC4(6개 전부 기대대로): 6/6 PASS. good 케이스는 numstat 동반으로 evidence 생성기까지 경유(lines_added 3·removed 1·files_changed 1·changed_files zone_level/in_allowed_paths 검증) — review-notes#2(TASK-003)의 "numstat 동반" 정합 요청 충족.
보수성: Codex 소유 영역(`tests/*` 신규, `tests/fixtures/README.md`) + 허용된 공동기록(`handoff-log`·`summaries`) + `README.md` 실행절 갱신(러너 실행법·실제 게이트 시그니처 문서화 — TASK-004 직접 관련, 무관 리팩터 아님). Claude 소유 policy/templates 무수정. scope-creep/over-reach 없음.
**머지 판정(D-007)**: 변경 대상이 테스트 하네스(`tests/`)·문서(`README`)로 생산 정산·인증/인가·암호화·DB migration·infra 경로 미접촉 → **비민감**. TASK-001/002/003 동일 범주(선례: Claude 머지). 구현자(Codex)≠머지자(Claude) 성립 → **Claude 가 main 에 머지**.
상세·비차단 관찰사항: `review-notes.md` 참조.

## D-011 (2026-07-01) TASK-005 Python 함수/클래스 인벤토리 추출 리뷰통과 + Claude 머지
대상 commit: `1115a22`(=impl `86c9a75`, 브랜치 `codex/2026-07-01-task005-function-inventory`). **MVP-1 Phase A 첫 게이트.**
수용기준 4/4 충족 — 경험적 검증(`bash tests/run-tests.sh` → 8/8 PASS, exit 0 + 픽스처 밖 신규 입력 독립검증)으로 확인.
- AC1(정규화 이름·라인범위·데코레이터): `Class.method`·중첩 `outer.inner`·`Service.Nested.method`·`decorator.wrapper` 모두 정확. `start_line`/`end_line`(=`end_lineno`)·데코레이터 목록 추출 — 픽스처 밖 fresh 입력(`functools.lru_cache` Call·`property`·`staticmethod`)에서도 `cached`/`A.x`/`A.x.helper`/`A.s` 정확 재현(rigged 아님).
- AC2(async·메서드·중첩·데코레이터 함수): `async def`→`async_function` 타입, 메서드(`Service.load`), 중첩(`outer.inner`·`A.x.helper`), 데코레이터 정의함수(`decorator`)·피데코 함수(`decorated`) 전부 포함. 데코레이터 resolve: `Name`/`Attribute`/`Call`/`Subscript` 재귀 처리 — `functools.lru_cache`(Call→Attribute) 정확.
- AC3(파싱실패 fail-safe): `invalid.py`(문법오류) → 예외 없이 `items: []` + `parse_error` 채움 + **exit 0**. 추출기는 분석 전용이라 차단 책임 없음(판정은 Phase B) → 비차단 fail-safe 적절.
- AC4(결정성·`--json`): 2회 실행 byte-identical. `--json` 은 `sort_keys=True` 로 키 순서 고정. AST 방문은 깊이우선 전위순(부모→자식) 결정적.
- **음성 검증**: `cases.yaml` 의 `Service.load` start_line(13)을 99로 변조 → `FAIL python-inventory` + `Summary: 7/8` + exit 1, 원복 후 8/8 — 러너가 항상-PASS 아님 확인.
보수성: Codex 소유 영역만 변경 — `.harness/gates/extract-python-inventory.py`(신규 114줄), `tests/fixtures/python-inventory/*`(신규), `tests/cases.yaml`(+2 케이스, 기존 6 무변경), `tests/run-tests.sh`(인벤토리 검증 분기 **추가만**, 기존 게이트 검증 무수정) + 허용된 `handoff-log`·`summaries`. Claude 소유 policy/templates 무수정. 무관 리팩터·이름변경·포맷 노이즈 없음 → scope-creep/over-reach 없음.
**머지 판정(D-007)**: 변경 대상이 **분석 전용 게이트**(AST 인벤토리 추출, verdict·차단 없음)·테스트 하네스(`tests/`)로 생산 정산·인증/인가·암호화·DB migration·infra 경로 미접촉 → **비민감**. TASK-001~004 동일 범주(선례: Claude 머지). MVP-1 공통(D-004): 2층 자동차단 금지 — 본 게이트는 애초에 판정을 내지 않으므로 무관. 구현자(Codex)≠머지자(Claude) 성립 → **Claude 가 main 에 머지**.
상세·비차단 관찰사항: `review-notes.md` 참조.
**2차 적대적 리뷰 보강(2026-07-01)**: 형 지적("다 통과 아니냐")을 받아 데코레이터·동명 함수로 2차 검증 → 거버넌스 직접영향 결함 2건 발견(`review-notes.md` #4·#5). ① 데코레이터가 함수 라인범위 밖(`@requires_auth`만 바꾸면 TASK-006 매핑서 누락) ② 정규화 이름 중복(getter/setter 동일 `Class.x` → TASK-007 매칭 오판). **둘 다 TASK-005 AC 위반 아님**(추출 정확) → **머지 유지**. 단 후속 누락 방지 위해 **TASK-006 AC5(데코레이터 줄 포함)·TASK-007 AC5(동명 매칭 가드)** 신설. 1차 리뷰 누락분을 수용기준 가드로 전환.

## D-012 (2026-07-01) TASK-006 diff 헝크↔함수 매핑 리뷰통과 + Claude 머지
대상 commit: `e5b4c2d`(=impl `32ac41c`, 브랜치 `codex/2026-07-01-task006-function-mapping`). **MVP-1 Phase A 2번째 게이트.** D-011(TASK-005) 2차 리뷰가 신설한 **AC5(데코레이터 줄 포함)** 가 실제로 막혔는지가 핵심 검증 대상.
수용기준 5/5 충족 — 경험적 검증(`bash tests/run-tests.sh` → 9/9 PASS, exit 0 + **픽스처 밖 fresh 입력** 독립검증)으로 확인.
- AC1(헝크∩함수범위 교집합): `git diff --unified=0` 헝크의 after 라인범위 ∩ 인벤토리 `[decorator_start_line, end_line]` 교차로 "닿은 함수" 판정. fresh repo 에서 setter 본문 변경(라인20)이 getter(13-16) 아닌 setter(18-20) `C.val` 에만 매핑 — 동명 함수도 라인범위로 정확 분리(rigged 아님).
- AC2(다중 함수 전부·모듈레벨 `<module>`): 중첩 변경(라인14)→`[outer, outer.inner]` 둘 다, 클래스 메서드 변경→`[Service, Service.method]` 둘 다, 모듈레벨(`VALUE=2`)→`<module>`. 교집합 함수 전부 보고 확인.
- AC3(after 기준 라인범위): head 버전을 `git show head:path` 로 파싱 + 헝크의 `+new_start,new_count`(after) 사용. 삭제(`remove_me` 2줄→1줄)·추가 오프셋 정확.
- AC4(결정성·`--json`): 2회 실행 byte-identical(md5 동일). `sort_keys=True`. `--json` 정상.
- **🔴 AC5(데코레이터 줄 포함 — D-011 #4 가드)**: `mapping_start_line = min(decorator.lineno)` → 매핑 범위를 데코레이터 첫 줄까지 확장. **fresh 입력 실증**: 멀티라인 `@requires_auth("user"→"admin")` **데코레이터만** 바뀐 헝크(라인6)가 `<module>` 아닌 함수 `secure`(decorator_start 4, def 9) 에 정확 매핑. **인증·라우팅·권한 데코레이터 변경을 흘려보내지 않음 = 거버넌스 핵심 목적 충족.** D-011 1차 리뷰 누락분을 가드로 막은 것이 실제로 동작함을 확인.
- **fail-safe**: 비-`.py`(`conf.yaml`)→`language: unsupported`+`<module>`, 삭제파일(status D)→`<module>`(head 파싱 시도 안 함, 크래시 없음), head 문법오류→`parse_error` 기록+`<module>`+exit 0(예외 없음), 신규파일(status A)→정상 매핑. 모두 fresh 입력으로 확인.
- **음성 검증**: `cases.yaml` 의 `secure_view` 기대를 `WRONG_NAME` 으로 변조 → `FAIL function-mapping` + `Summary: 8/9` + 러너 exit 1, 원복 후 9/9 — 항상-PASS 아님 확인.
보수성: Codex 소유 영역만 변경 — `.harness/gates/map-diff-to-functions.py`(신규 315줄), `tests/fixtures/function-mapping/{base,head}/*`(신규), `tests/cases.yaml`(+1 케이스 **추가만**, 기존 8 무변경), `tests/run-tests.sh`(임시 git repo 준비 + `map-diff-to-functions` 검증 분기 **추가만** — 기존 게이트 무수정) + 허용된 공동기록(`handoff-log`·`summaries`). **Claude 소유 policy/docs/templates 무수정.** 무관 리팩터·이름변경·포맷 노이즈 없음 → scope-creep/over-reach 없음.
**머지 판정(D-007)**: 변경 대상이 **분석 전용 매핑 게이트**(verdict·차단 없음, exit 0 보고용)·테스트 하네스(`tests/`)로 생산 정산·인증/인가·암호화·DB migration·infra 경로 미접촉 → **비민감**(TASK-005 와 동일 범주: auth 변경을 *분석*할 뿐 auth 를 *구현*하지 않음). 구현자(Codex)≠머지자(Claude) 성립 → **Claude 가 main 에 머지**.
**비차단 관찰 + 차기 AC 가드**: 상세 `review-notes.md`. 핵심: **하드 에러(잘못된 git ref·git 실패) 시 exit 0 + `error` 필드 + `files: []`** 로 보고만 함(Phase A 설계상 판정 안 함 — TASK-007 AC4 와 정합). **이는 본 게이트 결함은 아니나**(에러를 정직하게 노출), 후속 통합(**TASK-012**)이 `error`/`parse_error` 를 "함수 변경 없음"으로 오해하면 git 실패가 *clean diff* 로 읽혀 **fail-open** 위험 → 거버넌스 직접영향이므로 비차단으로 흘리지 않고 **TASK-012 AC 에 명시적 가드 신설**(`error`/`parse_error` 존재 시 fail-closed = approval_required/blocked). `TASKS.md` 반영.
