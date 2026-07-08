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

## D-013 (2026-07-02) TASK-007 함수 변경 분류 — **보정요청 (머지 보류)**
대상 impl: `0502589` (브랜치 `codex/2026-07-02-task007-function-change-classification`, `classify-python-function-changes.py`). **MVP-1 Phase A 3번째(마지막) 게이트.** 핵심 검증축: **🔴 AC5 동명 매칭 가드** + 고정 적대 세트(CLAUDE.md §2B — 데코레이터·동명 오버로드·조건부 def) + TASK-006 리뷰 #2 가 예고한 status R 처리.
**통과 실증** (`run-tests.sh` 10/10 PASS·exit 0 + 픽스처 밖 fresh repo ×3 독립검증):
- AC2(시그니처 vs 본문): **데코레이터 인자만 변경** `@requires_auth("user"→"admin")` → `modified signature_changed=True` — 권한 상향이 함수 단위로 정확 포착. 매칭키(데코레이터 이름만·느슨)/변경감지(전체 ast.dump·엄밀) 분리 설계 정확.
- **🔴 AC5(동명 매칭 — D-011 #5 가드)**: 키 = `(정규화이름, sorted 데코셋, 그룹 내 등장순서)` — 이름 단독 아님. property/setter(픽스처)·`@overload` 3연속(fresh)·if/else 조건부 동명 def(fresh) 전부 해당 정의만 정확 분류, 오판 없음.
- AC4: 2회 md5 byte-identical, `--json`·exit 0. 음성검증: 기대 변조→`FAIL`/9-10/exit 1(항상-PASS 아님). fallback(비-py/A/D/parse_error) 파일 단위 표시 정상.
**🔴 보정요청 사유 R-1 (fresh 입력으로 실증)**: diff 에 **리네임(R) 1건**만 있어도 R 레코드가 새 경로만 남긴 채 `git show base:<새경로>` 를 시도 → top-level 예외 → **전체 출력이 `error`+`files:[]` 로 붕괴, 같은 diff 의 무관한 M 파일(정산 `charge_fee` 도입) 분류까지 소실**. AC1·AC2 위반(형제 파일 미보고)·AC3 취지 위반(파일 단위 안전 스킵 아닌 전역 붕괴)·**AC4 결정성 위반**(host `diff.renames` config 에 따라 같은 입력이 정상/전체 error 로 갈림). fail-open 은 아니나(top-level `error` 는 D-012 가드로 TASK-012 가 fail-closed) 리네임은 흔한 입력이라 매번 감사카드가 빈손 = 게이트 목적 무력화. TASK-006 리뷰 #2 예고 사항이기도 함. → **`collab/answers/A-0001.md` 로 보정요청**: `--no-renames` 명시 또는 R/C 파일 단위 fallback + 형제 파일 분류 보존 + 회귀 픽스처. 국소 수정이며 나머지 구현 품질 높음 — 재제출 시 신속 재리뷰.
**비차단 관찰 → 차기 AC 가드 1건**: **모듈레벨 변경 비가시**(`ADMIN_ROLE="user"→"admin"` → `function_changes:[]`, 표식 없음)는 함수 분류기 설계상 범위 밖(TASK-006 `<module>` 매핑 몫)이나, TASK-012 가 TASK-007 출력 **단독**으로 "함수변경 0 = clean" 으로 읽으면 fail-open → **TASK-012 AC 가드 보강**(TASKS.md): 함수분류 단독 판정 금지·TASK-006 `<module>` 매핑과 병합 필수·`fallback:true` 파일 보수 취급. 기타 비차단(데코레이터 전면교체=deleted+added 쌍(가시성 유지), occurrence-shift 귀속 모호(변경은 안 놓침·보수 방향), dead `type_comment`, three-dot 입력 error)은 `review-notes.md`.
보수성: 순수 추가 + Codex 소유 README 갱신만, 공유 러너 헬퍼 수정은 D-fixture 에 필요하며 기존 케이스 green. **Claude 소유 무수정, scope-creep 없음.**
**머지 판정(D-007): 보류** — 보정요청이므로 머지하지 않음. (변경 자체는 분석 전용 게이트로 비민감 범주 — 보정 후 통과 시 Claude 머지 예정.)

## D-014 (2026-07-02) TASK-007 함수 변경 분류 — 재리뷰 **통과** + Claude 머지
대상 impl: `2243173`(브랜치 `codex/2026-07-02-task007-rename-fix`, 헤드 `25b80f1`). D-013/A-0001(R-1) 보정 재제출. **MVP-1 Phase A 3/3 게이트 완료.**
**재제출 형식**: A-0001 은 "같은 브랜치에 커밋 추가"였으나 Codex 는 최신 main(e673412) 기준 새 브랜치로 재제출 — 리뷰 기록이 main 에 머지된 상태라 합리적 이탈로 수용하되, **이전 리뷰본(0502589) 대비 전체 트리 diff 로 델타 동일성 검증**: 게이트 +7줄(`--no-renames` 명시 + R/C 파일 단위 fallback 방어 분기) + 회귀 픽스처 4파일 + cases.yaml 기대값 — **그 외 D-013 에서 실증 검증한 코드와 byte-identical.**
**R-1 수정 실증** (전부 fresh repo, 픽스처 밖):
- 재현→수정: `git mv payments.py settlement.py`+수정(R091)+형제 `other.py` M — **구 게이트 = `error`+`files:[]` 붕괴 재현 / 신 게이트 = 형제 분류 보존**(`charge_fee_stub added`·`helper modified`), 리네임 쌍 D/A fallback, 전역 error 없음.
- 환경 의존 제거: `diff.renames=true/false` 출력 **md5 동일** + 2회 실행 md5 동일(AC4).
- 스위트 10/10 PASS·exit 0 + 음성검증(`companion` 기대 변조 → FAIL·9/10·exit 1, 원복 10/10).
- 고정 적대 세트 재실행(CLAUDE.md §2B): `@requires_auth("user"→"admin")` → `secure modified signature_changed=True`, property/setter·`@overload`×3·조건부 동명 def 전부 정확.
**재리뷰 신규 발견 2건 — 비차단, TASK-013 AC 가드로 명시적 차단**(비차단 판정 전 필수 질문 적용: 현행 동작 정확·fail-closed 보수 방향, 직접 구멍 아님):
1. **회귀 픽스처 무력**: 픽스처 리네임(초소형 파일+내용 수정)은 git 유사도 감지에 안 걸려 renames 환경에서도 D+A → 구 게이트도 통과하고 **`--no-renames` 제거해도 10/10 PASS(실증)** = 회귀를 못 잡음. A-0001 문면은 충족(내 요구서가 감지 조건 미명시) → TASK-013 AC 가드: **순수 리네임(내용 동일) 쌍 추가**(크기 무관 R100 항상 감지 — 실증) + 플래그 제거 음성검증.
2. **비-UTF8 소스 전역 붕괴(R-1 동류)**: latin-1 등 디코드 불가 `.py` 1건 → `UnicodeDecodeError` → `error`+`files:[]` 형제 소실(실증). 희귀 입력 + TASK-012 fail-closed 로 fail-open 아님 → TASK-013 AC 가드: 파일별 예외를 파일 단위 fallback 으로 격리 + 픽스처 고정.
보수성: 델타가 A-0001 요구에 정확히 국소. Claude 소유 무수정, scope-creep/over-reach 없음.
**머지 판정(D-007)**: 분석 전용 게이트(verdict·차단 없음, exit 0 보고용)·테스트 하네스 — 정산·인증/인가·암호화·DB migration·infra 미접촉 → **비민감**(TASK-005/006 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.**
상세: `review-notes.md` TASK-007 재리뷰 절.

## D-015 (2026-07-02) TASK-013 분류 회귀 가드 — **보정요청** (map 게이트 비-UTF8 격리 미달), 머지 보류
대상 impl: `fb7a098`(브랜치 `codex/2026-07-02-task013-classification-regressions`, 헤드 `824502d`). D-014 에서 신설한 AC 가드 2건(순수 리네임 회귀 + 파일 단위 오류 격리) 구현. **보정요청 → `collab/answers/A-0002.md`. 머지 보류.**
**통과 실증 (classify 측 — 재검증 불요)**:
- 스위트 **10/10 PASS**·exit 0(브랜치 워크트리 실측).
- **AC 가드 #1 (pure-rename) 유효**: `pure_rename_source↔target` byte-identical(`def renamed_only`) 확인 → 게이트 `--no-renames` 제거 시 `R100` 단일 레코드 붕괴(host `diff.renames` unset=git 기본 on) → **스위트 9/10 FAIL**(음성검증 성립). 구 `renamed_*` 픽스처는 --no-renames 제거해도 D+A 유지(=무력) → 새 pure-rename 만이 실효 가드임 실증.
- **classify 비-UTF8 격리 유효**(픽스처 밖 fresh repo, `sibling.py` 정상 M + `bad.py` latin-1 `0xe9` M): **구 게이트(main)=`error`+`files:[]` 붕괴 재현 / 신 게이트=`sibling transfer:modified` 보존 + `bad→fallback:unreadable`, 전역 error 없음.** classify 는 전범위 패치 미독해(name-status+per-file `show`)라 `:276/285` 감싼 위치 정확.
**🔴 R-1 (보정 사유) — map 게이트 비-UTF8 붕괴 잔존 (AC 가드 #2 미달)**:
- 브랜치는 `map-diff-to-functions.py:260` `source_at_ref(head,...)` 를 감쌌으나, 비-UTF8 M 파일 붕괴는 **그 이전 `:238` `git diff --unified=0`(전범위 패치)** 에서 발생 — 패치 본문의 `0xe9` 바이트 → `run_git`(text=True strict) `UnicodeDecodeError` → per-file 루프 진입 전 top-level except → **`error`+`files:[]` 전역 붕괴.** `:260` wrap 은 도달 불가 = 死코드. **map 은 fix 전후 동작 무변화**(fresh repo 실측: classify `files=2` 보존 / map `error, files=0`).
- **`:238` 만 바이트-관용(surrogateescape) 디코드로 바꾸면 붕괴 해소 실증**: `sibling→transfer` 보존 + `bad→parse_error`+`<module>`(이 경우 `:260` wrap 가 파일 단위로 정상 격리). → 결함 근원이 `:238` 임 확정.
- **거버넌스 직접 구멍**: 단일 비-UTF8 `.py` 하나가 map 리포트 전체 `files:[]` → 형제 파일(인증/정산 함수 포함 가능) 함수 매핑 전량 소실 = D-013 R-1 동류. §2B 필수 질문 → 비차단 불가.
- **테스트 위양성**: `function-mapping` 픽스처는 `sample.py`(UTF-8) 하나뿐 → map 가드 **미실행**. 비-UTF8 케이스는 `function-classification` 픽스처에만 추가됨. 10/10 은 map 가드를 증명 못 함.
**요구 수정(최소)**: ① `:238`(필요 시 `:237`) 전범위 diff 읽기 바이트-관용화(surrogateescape/replace) **또는** 파일 단위 `diff -- <path>` + 파일별 try/except → 형제 매핑 보존·실패 파일만 `<module>` 격리. ② `function-mapping` 픽스처에 비-UTF8+동반 정상 M 회귀 케이스 추가 + "격리 제거→FAIL" 음성검증(가드 미검증 방지).
보수성: 델타는 AC 가드 요구에 국소, Claude 소유 무수정, scope-creep 없음 — 품질 자체는 양호하나 map 한 곳 국소 결함으로 반려.
**머지 판정(D-007): 보류** — 보정요청이므로 머지 안 함. (변경 자체는 분석 전용 게이트로 비민감 범주 — 보정 후 통과 시 Claude 머지 예정.)
상세: `collab/answers/A-0002.md`, `review-notes.md` TASK-013 절.

## D-016 (2026-07-04) TASK-013 분류 회귀 가드 — 재리뷰 **통과** + Claude 머지
대상 impl: `0aaadcc`(브랜치 `codex/2026-07-04-task013-map-nonutf8-fix`, 헤드 `bfbc1e8`). D-015/A-0002 보정 재제출 — 새 브랜치(main `fbc2490` 기준) 재제출은 D-014 전례대로 수용하되 **구 리뷰본(`824502d`) 대비 게이트 직접 diff 로 델타 검증**: map `git diff --unified=0` 읽기 surrogateescape 화(+ 死코드 wrap 을 extract_inventory 포함 try 로 교체), classify except 협소화(기능 동등), function-mapping 픽스처 신설(비-UTF8 0xe9 + sibling), pure_rename blob 동일(`f7a18b4` = byte-identical → R100 보장).
**실증(워크트리·fresh)**: 스위트 10/10 PASS·exit 0(실패 시 exit 1 확인) + **음성검증 5종 전부 성립** — 기대 변조 / surrogateescape 제거(A-0002 "격리 제거→FAIL") / `--no-renames` 제거(AC 가드#1) / classify·map 격리 except 무력화 → 각각 해당 케이스만 9/10 FAIL, 원복 10/10. **R-1 해소 fresh 실증**: `sibling.py` M + `bad.py`(0xe9) M — 구 게이트 `error`+`files=0` 붕괴 ↔ 신 map `files=2`·`transfer` 보존·`bad→<module>`+parse_error / 신 classify 형제 보존·`bad→unreadable`. **적대 입력**: NUL 바이트 `.py` → host 3.11.4 `SyntaxError` → parse_error 격리·전역 붕괴 없음·형제 보존, base-측만 비-UTF8 → head 기준 정상 매핑(classify 는 보수 폴백), 반복 실행 md5 동일(결정성).
**AC 가드#1·#2 (D-014 신설분) 모두 충족.** 비차단 관찰 3건(`review-notes.md` TASK-013 재리뷰 절): ① map `parse_error`+헝크 부재 시 `touched_functions:[]` — TASK-012 AC 가드(D-012 #1)가 이미 fail-closed 강제 → 구멍 아님, AC 문구에 "빈 touched_functions ≠ clean" 명시 보강(TASKS.md, 이번 커밋) ② 격리 except 에 `ValueError` 미포함 — 호스트 3.11.4 실증상 안전, 차기 강건화 권고 ③ 비-UTF8 파일명은 APFS 상 재현 불가, 기록만.
보수성: 델타가 A-0002 요구에 정확히 국소, Codex 소유 파일만, scope-creep 없음.
**머지 판정(D-007)**: 분석 전용 게이트·테스트 픽스처 — 비민감(TASK-005/006/007 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** MVP-1 Phase A 회귀 가드 완결 — 다음은 Phase B TASK-008(`@gov` 규약, Claude 설계 선행).
상세: `review-notes.md` TASK-013 재리뷰 절.

## D-017 (2026-07-04) TASK-008 설계질문(Q-0001) 인계 리뷰 **통과**·머지 + `@gov` 설계 계약 확정 (A-0003)
대상: `codex/2026-07-04-task008-design-question`(`5ea0b79`·헤드 `775e145`) — **코드 없는 문서 인계**: `collab/questions/Q-0001.md`(TASK-008 `@gov` 규약 설계 요청, blocking) + handoff-log + summaries.
**리뷰 실증**: ① 보수성 — diff 3파일 전부 추가만(질문·인계·요약), 구현/픽스처/Claude 소유 무접촉, `collab/questions/` 는 COMMON-RULES §1 명시 경로 ② 커밋 2건 모두 §3 상세 형식 준수 ③ "테스트 green" 주장 실증 — 스위트 10/10 PASS·exit 0 재확인 ④ 내용 정확성 — TASKS.md `:95` "Claude 설계 선행" 인용 정확, 질문 7항이 계약에 필요한 결정을 빠짐없이 커버(문법·필드·심각도·scope·검증실패·스키마·테스트 AC). **Codex 가 정책 의미를 임의 구현하지 않고 차단 질문으로 멈춘 것 = 역할 경계 준수(모범 사례).**
**설계 답변**: `collab/answers/A-0003.md` — ⑴ 문법: `@gov(level=,reason=,[owner=])` 데코레이터(AST 리터럴만) + 모듈 `__gov__` dict, 주석/독스트링 마커는 명시 거부 ⑵ 어휘: sensitive-zones 와 동일 frozen/protected/watched (TASK-009 policy 재사용) ⑶ **엄격 승계(stricter-wins)** — 내부 주석으로 레벨 하향 우회 불가 ⑷ 검증실패는 기록+보수 취급(invalid→protected), 파일 단위 격리(TASK-013 계보) ⑸ 출력은 **별도 게이트**(TASK-005 스키마 확장 금지 — 하류 계약 보호) ⑹ 테스트 AC 7항(고정 적대 세트 포함).
**층 분류 정책 결정**: `@gov` 주석은 사람이 명시 선언한 규칙 → **1층(선언적) 범주** — D-004 "2·3층 자동 차단 금지"는 추론 기반 층 대상이므로 TASK-009 `frozen=blocked(1)` 와 모순 없음(TASKS.md 기존 "0/1/2" 명세와 정합). 형 override 가능.
**하류 가드 신설(TASK-009 AC, TASKS.md 반영)**: ① **주석 제거 우회 방지** — 판정은 base ∪ head 양측 max(같은 PR 에서 `@gov(frozen)` 삭제+본문 수정 우회 차단) ② base 에 frozen/protected 주석 있던 파일이 head unreadable/parse_error → 최소 approval_required (fail-closed).
**머지 판정(D-007)**: 협업 문서 전용(질문·인계·요약) — 비민감. 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** Q-0001 은 answered 로 전환. 다음: Codex 는 A-0003 계약대로 **TASK-008 구현 진행 가능**.
상세: `collab/answers/A-0003.md`, `review-notes.md` TASK-008 질문 리뷰 절.

## D-018 (2026-07-04) TASK-008 `@gov` 주석 추출 게이트 — **보정요청** (중복 level last-wins 다운그레이드 + `__gov__` 비정식 형태 silent drop), 머지 보류
대상 impl: `787a47d`(브랜치 `codex/2026-07-04-task008-gov-annotations`, 헤드 `2fa3635`) — `.harness/gates/extract-gov-annotations.py` + `tests/fixtures/gov-annotations/` + 러너 확장. **보정요청 → `collab/answers/A-0004.md`. 머지 보류.**
**통과 실증 (재검증 불요)**: 스위트 14/14 PASS·exit 0 + 결정성 md5 동일 + **음성검증 3종**(기대 effective_level 변조 → 13/14 / stricter-wins 승계 제거 → 12/14 / order_key 카운팅 무력화 → 13/14 — 픽스처가 승계·동명 부착 모두 실가드) + **고정 적대 세트**(setter-만-주석 order_key 1·overload·조건부/중첩 def) 정확 + **fresh 적대 입력 7종**(bare `@gov`→protected 보수 / `__gov__` 재할당 frozen→watched 시도→frozen 유지+기록 / 모듈+클래스+중첩 3계층 승계 frozen / `*.gov` attribute 인식 / `**kw`·bytes·f-string→unresolved 보수 / fresh 비-UTF8→unreadable 격리 / stdin 정상). 보수성 OK(신규 게이트·테스트만, Claude 소유 무접촉, 커밋 §3 준수).
**🔴 R-1 (보정 사유) — 동일 주석 내 `level` 키 중복 → last-wins 다운그레이드 (A-0003 Q4 "하향 우회 불가"·Q5 "silent pass 금지" 위반)**:
- (a) `@gov(level="frozen", level="watched", ...)` — **`ast.parse` 는 중복 keyword 를 안 거른다**(SyntaxError 는 compile 단계, 호스트 3.11.4 실측). 게이트 실측 `level=watched, errors=[duplicate]` — 필드 대입이 마지막 값으로 덮어씀. frozen=blocked 가 최대 approval_required 로 강등.
- (b) `__gov__ = {"level":"frozen","level":"watched"}` — dict 중복 키는 **합법·실행 가능**. 게이트 실측 `level=watched, errors=[]` — **무기록 silent downgrade**. TASK-009 의 invalid→approval_required 안전망조차 못 받고, base∪head max 도 신규/기존-오염 파일엔 무력 → 이 게이트가 스스로 막아야 함. §2B 필수 질문("거버넌스 목적에 직접 구멍?") → 그렇다 → 비차단 불가.
- 수정: 같은 call/dict 내 중복 필드 → 오류 기록 + level 은 **유효값 중 strongest-wins**. 픽스처 2건 + 음성검증.
**🔴 R-2 (보정 사유) — `__gov__` 비정식 형태 silent drop (계약 갭 → A-0004 로 A-0003 개정)**:
- (a) 톱레벨 `AnnAssign`(`__gov__: dict = {...}`·`: Final`) — 완전 무시(module null·오류 0). 실행 의미는 Assign 동일, 타입힌트 코드베이스의 자연 표기 → 선언된 frozen 이 무주석 pass. base∪head 로도 못 잡음(양측 비가시). 계약이 Assign 만 명시한 **내 설계 누락**(Codex 는 계약대로 구현) → 계약 개정: 값 있는 톱레벨 AnnAssign 도 정식 인정.
- (b) 그 외 위치 `__gov__` 바인딩(if 안·클래스 본문·AugAssign·다중 타겟) — 무기록 무시 → 계약 개정: 발견 시 `invalid_module_gov` 기록+protected 보수(false positive 는 보수 방향이라 수용).
**비차단 관찰 5건**(A-0004 §관찰): bare `@gov` missing_reason 미기록(보수 유지)·stdin path 표기·누락 파일 traceback(사용법 오류 범주)·`type` 필드 추가 수용·**order_key ≠ TASK-007 occurrence**(per-name vs per-(name,decoset)) → **TASK-009 join 은 `(path, name, def_line↔start_line)` 로** — TASKS.md TASK-009 에 보강.
**머지 판정(D-007): 보류** — 보정요청. (변경 자체는 분석 전용 게이트로 비민감 범주 — 보정 통과 시 Claude 머지 예정.) 리뷰 기록(decisions·review-notes·A-0004·TASKS 보강)은 main 머지.
상세: `collab/answers/A-0004.md`, `review-notes.md` TASK-008 구현 리뷰 절.

## D-019 (2026-07-05) TASK-008 `@gov` 주석 추출 게이트 — 보정 재리뷰 **통과** + Claude 머지
대상: 보정 커밋 `2272a47`(브랜치 `codex/2026-07-04-task008-gov-annotations`, 헤드 `bc03b5e`) — D-018/A-0004 R-1·R-2 보정 재제출. 멱등성 준수: `787a47d`·`2fa3635` 재처리 안 함, **보정 델타만 재리뷰**(게이트 diff 97줄 + 픽스처 4파일 + cases 3건 한 줄씩 검토).
**R-1 해소 실증 (strongest-wins)**: `parse_gov_call`·`parse_module_gov_value` 양쪽에서 `level` 후보를 `level_values` 로 모아 `strongest_level`(유효값 중 최강) 채택 + 중복 시 오류 기록(`duplicate`/`invalid_module_gov`). 픽스처 실측 — `@gov(level="frozen", level="watched")` → frozen+duplicate / `__gov__` dict 중복 키 → frozen+invalid_module_gov(무기록 silent downgrade 해소). **역순 dup(watched,frozen)→frozen / 3중 dup→frozen / 유효+invalid(critical,watched)→watched+invalid_level+duplicate / 유효+비리터럴→frozen+unresolved** — fresh 전부 A-0004 명세 그대로. `missing_level` 은 `level_field_seen` 으로 분리해 이중 기록 없음(정합).
**R-2 해소 실증 (silent drop 금지)**: ① 값 있는 톱레벨 `AnnAssign` 정식 인정(`__gov__: dict = {...}` 픽스처 + fresh `: Final` → frozen·errors=[]) ② 그 외 바인딩은 `ast.walk` 전수 탐지(Assign 다중 타겟·Tuple/List 언패킹·AnnAssign·AugAssign·NamedExpr, 정식 문장은 id() 로 제외) → `invalid_module_gov`+protected. fresh 실측 — if 안/클래스 본문/함수 본문/`__gov__ = X = {...}`/`+=`/walrus/값 없는 `__gov__: dict` 전부 기록+protected, **정식 frozen + 중첩 watched 바인딩 → frozen 유지**(stricter-wins 머지라 하향 경로 없음).
**실증(워크트리)**: 17/17 PASS·exit 0 + md5 결정성(2회) + **음성검증 4종 전부 성립** — ① 기대 변조(module_duplicate frozen→watched) 16/17 ② **strongest-wins → last-wins 원복** 15/17(데코·모듈 픽스처 둘 다 가드) ③ walk 탐지 제거 16/17 ④ AnnAssign 정식 인정 제거 16/17, 각 원복 17/17. AC 7·8(D-018 신설) 충족 — "strongest-wins 제거→FAIL" 요구 그대로 재현.
**보수성(COMMON-RULES §1)**: 델타가 R-1·R-2 에 정확히 국소(게이트 1파일+픽스처+cases+인계·요약), 무관 리팩터 없음, Claude 소유 무접촉, 커밋 §3 상세 형식·`git diff --check`·`py_compile` 준수.
**비차단 관찰 4건**(`review-notes.md` 재리뷰 절): ① for/with/import-as/starred 등 비선언적 `__gov__` 바인딩 미탐지 — AC 8 열거 범위 밖·하향 경로 불가(stricter-wins+TASK-009 base∪head)·기록만 ② 유효+invalid/unresolved 혼재 중복은 "유효값 중 최강" 채택(명세 문면대로) — 오류가 항상 기록되므로 TASK-009 의 "errors 비어있지 않으면 최소 approval_required" 조항이 최종 방어선 → TASK-009 리뷰 때 재확인 ③ 정식+비정식 공존 시 merge 가 `duplicate` 오류도 부가 — 과잉 표기지만 보수 방향·결정적 ④ module 출력에 `unresolved` 플래그 미노출 — errors 가 신호 대체(표기만).
**머지 판정(D-007)**: 분석 전용 보고 게이트·픽스처 — **비민감**(TASK-005/006/007/013 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** TASK-008 완료 — 다음: **TASK-009**(변경함수↔주석 level 게이트, TASK-008 머지 후 진행 가능. AC: base∪head max·fail-closed 연동·join 키 `(path,name,def_line↔start_line)`).
상세: `review-notes.md` TASK-008 재리뷰 절.

## D-020 (2026-07-05) TASK-009 변경함수↔`@gov` level 게이트 — **보정요청** (분석-불능 파일 fail-closed 가 동반 레코드에 꺼지는 fail-open), 머지 보류
대상 impl: `2a41a7e`(브랜치 `codex/2026-07-05-task009-function-gov-level`, 헤드 `e42c87f`) — `.harness/gates/check-function-gov-level.py` + `tests/fixtures/function-gov-level/` 6종 + 러너 확장. **보정요청 → `collab/answers/A-0005.md`. 머지 보류.**
**통과 실증 (재검증 불요)**: 스위트 23/23 PASS·exit 0 + md5 결정성 + **음성검증 4종**(기대 verdict 변조 19/23 / **base 측 lookup 제거(head-only 판정)** 19/23 — base∪head max 실가드 / head fail-closed 제거 21/23 / errors→protected 제거 22/23, 원복 23/23) + **고정 적대 세트 fresh**(setter-만-frozen 세터 수정 → blocked — 조인 `(name,def_line)` 이 D-018 #5 order_key 함정 회피 실증, getter 만 수정 → pass 오발 없음, `@overload` impl·조건부 def → blocked) + **fresh 적대 하향·우회 8종 전부 차단**(신규 파일 frozen → blocked / `git mv`+주석 제거(renames ON) → 구경로 fail-closed blocked / 모듈 `__gov__` 제거·값 하향 → blocked / 데코 인자 하향 → blocked / 모듈 protected 승계 미주석 함수 → approval / frozen 함수만 삭제 → blocked). 보수성 OK(신규 게이트·픽스처·README 2줄만, Claude 소유 무접촉, 커밋 §3 준수).
**🔴 R-1 (보정 사유) — head 존재·분석-불능 `.py` 의 pass 세탁**: 신규 비-UTF8 `.py`(latin-1 코딩 선언 = 합법 실행 파이썬, `@gov(frozen)` 은닉 가능·게이트 비가시) 단독 → approval_required 인데, **watched 변경 1건 동반 → verdict pass·exit 0**(errors 에만 기록). 근원: 전역 fail-closed 가 `errors and not records` 라 records 1건이면 꺼지고, per-path fail-closed 는 base-민감일 때만 레코드 생성(신규/재작성 파일은 base 민감 없음 → 0). TASK-012 "빈/불능 분석 ≠ clean" 계보 위반 = §2B 필수 질문 해당 → 비차단 불가. 수정: head 존재+불능 → per-path fail-closed 무조건(base 민감 시 그 레벨, 아니면 protected) / 부재(삭제)는 base 가독·비민감이면 통과 허용(과차단 방지) / top-level upstream error 도 records 무관 최소 approval.
**🔴 R-2 (보정 사유·AC 개정) — base 측 불능 → head 정상화 세탁**: base 비-UTF8(frozen 은닉) → head UTF-8 재인코딩+주석 제거+watched 동반 → **pass**(base 항 증발 = 무기록 하향). AC 문면이 head 측만 명시한 내 설계 누락 — A-0005 로 개정: base 존재+불능 → per-path 최소 protected fail-closed. TASKS.md TASK-009 AC 보강.
**요구 픽스처**: unreadable-head-laundering·unreadable-base-laundering → approval / plain-delete-pass(무주석 삭제 단독 → pass — 현행 approval 에서 동작 변경 명시) + "fail-closed 무력화 → FAIL" 음성검증.
**비차단 관찰 4건**(A-0005 §관찰): protected 리터럴 하드코딩·added/deleted 반대편 라인 재사용·`<unknown>` path 소실(R-1 로 자연 해소)·**frozen 신규 도입도 blocked = 정책 확정**(선언 도입은 인간 확인 — 형 override 가능).
**머지 판정(D-007): 보류** — 보정요청. (변경 자체는 분석 전용 판정 게이트 — 보정 통과 시 Claude 머지 예정.) 리뷰 기록(decisions·review-notes·A-0005·TASKS 보강)은 main 머지.
상세: `collab/answers/A-0005.md`, `review-notes.md` TASK-009 리뷰 절.

## D-021 (2026-07-05) TASK-009 변경함수↔`@gov` level 게이트 — 보정 재리뷰 **통과** + Claude 머지 (MVP-1 Phase B 완결)
대상: 보정 커밋 `aacdfe9`(브랜치 `codex/2026-07-05-task009-function-gov-level`, 헤드 `d8a777c`) — D-020/A-0005 R-1·R-2 보정 재제출. 멱등성 준수: `2a41a7e`·`e42c87f` 재처리 안 함, **보정 델타만 재리뷰**(게이트 +78/-10 + 픽스처 3세트 + cases 3건 한 줄씩).
**R-1 해소 실증**: `git cat-file -e` 기반 존재 판별 신설(에러 문자열 파싱 아님 — 계약 준수) + head 존재·분석-불능 → **records 유무 무관** per-path fail-closed(base 민감 시 그 레벨, 아니면 protected) + 전역 `errors and not records` → **`upstream_errors` 스냅샷 무조건 발동**으로 교체(AC ④). 픽스처 `unreadable-head-laundering`(watched 동반 → approval) 고정.
**R-2 해소 실증**: base 존재·불능 → head 가독 여부 무관 per-path protected fail-closed(`side=base`). 픽스처 `unreadable-base-laundering` 고정. base 불능+head 삭제 조합도 동일 블록이 잡음(F3 fresh).
**과차단 정상화**: 무주석·가독 base `.py` 삭제 단독 → pass(`plain-delete-pass`, A-0005 §요구 3 의 동작 변경 명시대로).
**실증(워크트리)**: 26/26 PASS·exit 0 + md5 결정성 + **음성검증 4종**(head 무조건 레코드 → 구 조건 원복 FAIL / base측 제거 FAIL / **존재판별 무력화 → plain-delete-pass FAIL** — 존재판별이 과차단 방지 실가드 / 기대 변조 FAIL, 각 원복 26/26) + **fresh 적대 6종**(F1 head 문법오류+동반 → approval — parse_error 경로도 세탁 불가 / F2 양측 불능 / F3 base-불능+삭제 / F4 불능 파일 순수 리네임 renames ON — 양경로 fail-closed / F5 가독 무주석 리네임 단독 → pass / F6 신규 불능 단독 → approval — 전역 조건 교체 무회귀).
**보수성(COMMON-RULES §1)**: 델타 국소·무관 리팩터 없음·Claude 소유 무접촉·커밋 §3 준수.
**비차단 관찰 4건**(`review-notes.md` 재리뷰 절): AC ④ 픽스처 부재(결정적 재현 곤란 — 코드 검토·F6 으로 확인, TASK-012 때 옵션)·양측 불능 레코드 2건(보수 방향)·`absent` 필드 정보성·D-020 관찰 3·5 해소 확인.
**머지 판정(D-007)**: 분석 전용 판정 게이트·픽스처 — **비민감**(TASK-005~008·013 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** TASK-009 완료 = **MVP-1 Phase B 완결**(TASK-008+009).
**하류 반영**: TASKS.md TASK-012 AC 가드에 "TASK-009 `errors` 비어있지 않으면 통합측도 최소 approval(중복 방어선)" 한 줄 보강. 다음: **TASK-012(감사카드 통합) 진행 가능**(Phase D — AC 가드 3건 준수). Phase C TASK-010 은 Claude catalog 설계 선행 — Codex 대기.
상세: `review-notes.md` TASK-009 보정 재리뷰 절.

## D-022 (2026-07-05) TASK-010/011 능력 카탈로그 설계 확정 (선제 — 2층 신규 능력 감지)
Codex 질문 없이 Claude 가 먼저 낸 설계(TASK-010 = "Claude 설계 선행"). 계약 전문: `docs/capability-catalog-design.md`, 카탈로그 draft: `policies/sensitive-capabilities.yaml`.
**층·불변식**: 능력은 **추론 2층**(설계 §3) — `@gov`(선언 1층, D-017)와 달리 **자동 차단 금지, `approval_required` 가 상한**(D-004). catalog `level ∈ {protected, watched}`, `frozen` 오면 검증오류+protected clamp. 차단이 필요하면 2층이 아니라 1층(`@gov frozen`/zone)에서 사람이 선언.
**게이트 분리(A-0003 패턴)**: TASK-010 `extract-python-capabilities.py`(추출·보고 전용·exit 0) / TASK-011 `check-new-capabilities.py`(판정). TASK-005 인벤토리 스키마 확장 금지.
**감지 신호(결정적 AST)**: `imports`(모듈 import 자체가 신호) / `calls`(별칭·from-import 해소한 점표기 전체이름) / `builtins`(무-import `eval`/`exec`). **핵심 방어 = import-레벨 backstop**: 호출 해석은 별칭·`getattr`·재대입·star-import 로 우회 가능하나 import 는 정적으로 잡힘 → 우회해도 import 신호가 능력 포착. `__import__`/`getattr` 동적 경로는 `dynamic_code_exec`·import backstop 이 받음. 값 추정 금지(`yaml.load` 항상 신호, `open` 쓰기판별 제외).
**신규 판정 = `head − base`(파일별 능력 id 차집합)**: TASK-009 `base∪head max` 와 **정반대** — 능력 제거는 안전(무경고), 신규 도입만 approval. 신규 파일 전부 신규, 삭제 파일 무신규.
**fail-closed(A-0005 교훈 반영)**: head 존재+분석불능 → per-path 무조건 approval(전역 `errors and not records` 조건 금지 — D-020 세탁 재발 차단). base 불능 → base_caps 빈 집합(head 능력 신규화 approval). 존재판별 `git cat-file -e`(문자열 파싱 금지).
**시작 카탈로그(🟡 조직 채움)**: subprocess_exec·dynamic_code_exec·unsafe_deserialization·outbound_network·crypto_primitive. **자격증명·PII 취급은 명시 이연**(값·데이터흐름 분석 필요 — 잡음 폭증 방지, 설계 §3 "정밀도 우선").
**정책 선택 4건(형 override 가능·비차단)**: A. 판정단위=파일별 능력 id 집합(기존 능력 추가사용 무경고) B. import-of-민감모듈=도입 간주 C. 시작 카탈로그 내용 D. 자격증명/PII 이연.
**테스트 AC**: 고정 적대 세트 7종(별칭·from-별칭·star·getattr·`__import__`·내장·함수내 import) 상설 픽스처 + 신규만/never-blocked/fail-closed 3대 음성검증.
**머지 판정(D-007)**: 이 설계 산출물(정책 draft·설계 문서·TASKS AC·기록)은 문서 전용·비민감 — 단 형 지시대로 **다음 리뷰 사이클에서 그 리뷰 기록과 함께 main 에 번들 머지**(지금 단독 푸시 안 함). Codex 는 main 반입 후 TASK-010 구현 착수 가능(브랜치 `codex/<날짜>-task010-capabilities`).
상세: `docs/capability-catalog-design.md`.

## D-023 (2026-07-05) TASK-012 감사카드 통합 (`generate-change-evidence` ← 함수 gov) — 리뷰 **통과** + Claude 머지 (+ TASK-010 설계 번들 반입)
대상: impl `81147f5`(브랜치 `codex/2026-07-05-task012-evidence-integration`, 헤드 `20067e8`) — `generate-change-evidence.py` + 통합 테스트 3종 + evidence-integration change-intent 픽스처.
**통합 구조(정합)**: evidence 게이트가 `check-function-gov-level`(TASK-009)를 `importlib` 로 로드해 git-ref 입력에서 실행 → `changed_functions` 를 감사카드에 싣고, `combine_verdicts` 로 경로판정(intent∪zone)과 함수판정을 합성. TASK-009 가 내부적으로 TASK-006 map ∪ TASK-007 classify(`<module>` 포함)를 이미 병합하므로 D-013 "TASK-007 단독 판정 금지·모듈레벨 병합" 이 자연 충족. 상류 error 는 TASK-009 `errors`+fail-closed 레코드로 전달돼 승격.
**핵심 실증(경로-clean인데 함수-frozen → blocked, fresh 격리)**: 신규 repo 에서 intent=pass·sensitive=pass(경로상 어떤 zone·forbidden 도 아님)인데 `@gov(frozen)` 함수 본문만 수정 → **최종 verdict=blocked**. 경로판정은 frozen zone 이 아니면 최대 approval 이므로 blocked 는 오직 함수-gov 가 만든 것 = MVP-1 의 핵심 갭(경로에 안 보이는 민감 함수)이 감사카드에서 실제로 막힘. + parse_error 신규 `.py`(경로-clean) → approval_required(`function_analysis_error` reason, "빈 결과 ≠ clean" 실증) / 무주석 함수 변경 → 함수 reason 없이 경로대로 pass(과차단 없음) / name-status 파일 입력 → 함수분석 스킵·MVP-0 호환.
**음성검증 3종**: ① `combine_verdicts` 를 경로판정만으로 되돌림 → frozen·module-protected·fail-closed **3 픽스처 전부 FAIL**(통합 실가드) ② frozen 기대 pass 변조 → FAIL ③ (M2) `or function_gov.get("errors")` 제거 → **변화 없음**(비차단 관찰 1 참조). 29/29 PASS·md5 결정성. exit 경로: 최상위 try/except 가 어떤 예외든 blocked fail-closed(bad ref 등 — 기존 MVP-0 핸들러).
**보수성(COMMON-RULES §1)**: 변경 = `generate-change-evidence.py` + tests(cases·run-tests·픽스처 change-intent)만. **Claude 소유 무접촉**(docs/policies/templates/CLAUDE/decisions/answers/review-notes), scope-creep 없음. `git diff --check`·`py_compile` PASS, 커밋 §3 준수.
**비차단 관찰 4건**(`review-notes.md`): ① `or function_gov.errors` 분기는 중복 방어선이나 독립 테스트 픽스처 없음(post-D-021 TASK-009 는 errors 있으면 항상 verdict≥approval → 현재 단독 발화 불가·死코드 아님) ② name-status 파일 입력은 함수분석 조용히 스킵 — canonical 호출은 git-ref(README 확인)라 운영 갭 아님, 문서화 권고 ③ 일반 예외→blocked(AC "최소 approval" 보다 강함, 안전 방향·기존 핸들러) ④ `changed_functions` 가 base·head 후보를 중복 표기(TASK-009 출력 그대로, 결정적·감사용 무해).
**머지 판정(D-007)**: 분석 전용 감사카드 생성 게이트 — **비민감**(TASK-005~009 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** **번들**: 형 지시로 보류했던 **TASK-010/011 설계(D-022)를 이 리뷰 사이클에 함께 main 반입**. **MVP-1 Phase D(TASK-012) 통합 완료.** 다음: **TASK-010(능력 추출기) 진행 가능**(설계 계약 `docs/capability-catalog-design.md`). 멱등성: 81147f5·20067e8 재처리 금지.
상세: `review-notes.md` TASK-012 리뷰 절.

## D-024 (2026-07-05) TASK-010 능력 추출기 `extract-python-capabilities.py` — 리뷰 **통과** + Claude 머지
대상: impl `1ed4222`(브랜치 `codex/2026-07-05-task010-capabilities`, 헤드 `cb58354`) — 신규 게이트 `.harness/gates/extract-python-capabilities.py`(296줄) + 픽스처 `tests/fixtures/capabilities/`(valid.py·invalid.py·frozen-policy.yaml) + tests(cases +142·run-tests +49) + README 실행 예시 1줄. **2층 능력 추출(보고 전용·exit 0·판정 없음)** — 계약 `docs/capability-catalog-design.md`(D-022).
**계약 정합(A-0003 패턴)**: 추출기는 카탈로그 `imports`/`calls`/`builtins` 신호를 AST 로 결정적 추출만 하고 verdict 를 내지 않는다(판정은 TASK-011). TASK-005 인벤토리 스키마 확장 없음(별도 게이트). 출력 `{path, capabilities:[{id,level,signals:[{kind,name,line}]}], unresolved_dynamic, errors, parse_error, unreadable}` = Q7 스키마 정합.
**핵심 방어 실증(fresh 격리, 픽스처 밖)**: 신규 적대 파일로 독립검증 — ① 별칭 `import subprocess as sp` ② from-별칭 `from subprocess import run as r` ③ star `from subprocess import *`(→star_import backstop) ④ 동적접근 `getattr(subprocess,"run")`(→import subprocess backstop) ⑤ `__import__`(→dynamic_code_exec builtin) ⑥ 무-import `exec`/`eval`/`compile` ⑦ **중첩-중첩** def 안 def 안 `import pickle`(walk 전수) — **7종 전부 감지**. 재대입 별칭 `x=subprocess; x.run()` 도 import backstop 으로 subprocess_exec 포착.
**음성검증(rigged 차단 — 3종 mutation → 스위트 FAIL, 원복 33/33)**: ① star_import 핸들링 제거 → FAIL ② Import backstop 신호 방출 제거 → FAIL ③ `build_import_bindings` 의 `ast.walk`→`tree.body`(톱레벨만) → FAIL(중첩 import 미감지). 단일 `valid.py` golden 이 전체 capabilities/signals 구조 exact-match 라 각 감지경로 제거가 실FAIL 로 잡힘 = 상설 회귀 가드 유효.
**never-blocked clamp(Q2)**: `frozen-policy.yaml`(level=frozen) → `invalid_capability_level` 기록 + **protected clamp**(추출기 레벨 불변식). `unknown_signal_kind`(mystery) 기록. verdict-never-blocked 자체는 TASK-011 몫.
**fail-safe(TASK-013 계보)**: fresh 문법오류 → `parse_error`(메시지)·caps=[]·exit 0 / fresh 비-UTF8 → `unreadable`(메시지)·caps=[]·exit 0 / stdin(`-`) path="stdin". 단일 파일 추출기라 형제 보존 무관(격리=파일 전체). 결정성 md5 동일(fresh 입력 2회).
**보수성(COMMON-RULES §1)**: 변경 = 신규 게이트 + tests + README 1줄 + 인계기록(handoff/summaries)만. **Claude 소유 무접촉**(`policies/sensitive-capabilities.yaml`·docs·CLAUDE·decisions·answers·review-notes 미수정), scope-creep 없음. `git diff --check`·`py_compile` PASS, 커밋 §3 준수.
**비차단 관찰 3건**(`review-notes.md` TASK-010 절): ① **call-only 모듈 동적 우회 갭** — `os`(잡음 이유 import 무신호)에 `getattr(os,"system")`·재대입 별칭은 import backstop 부재로 놓침(직접·alias os.system 은 잡힘). 계약 Q4(subprocess 기반)는 전부 통과·주 실행벡터 subprocess 완전 backstop → 비차단, **TASK-011 AC 가드 신설**(getattr(<바인딩>,"<리터럴>") 점표기 해소 또는 수용 잔여 문서화). ② `parse_error`/`unreadable` 이 bool 아닌 문자열 메시지(Q7 예시는 bool) — truthy 라 하류 무해·감사 정보 enrich, 수용. ③ star_import 이 call-파생 catalog 모듈까지 과매칭(`from urllib import *`→outbound_network 등) — 과경고(안전 방향) 수용.
**머지 판정(D-007)**: 분석 전용 능력 추출 게이트(exit 0·판정 없음·차단 불가) — **비민감**(TASK-005~009 동일 범주, 2층은 approval 상한). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** 다음: **TASK-011(`check-new-capabilities.py`, 신규 능력 판정)** 진행 가능 — AC 가드(head−base·never-blocked·fail-closed A-0005·call-only 동적우회 D-024) 준수. 멱등성: 1ed4222·cb58354 재처리 금지.
상세: `review-notes.md` TASK-010 리뷰 절.

## D-025 (2026-07-05) TASK-011 신규 능력 diff 게이트 `check-new-capabilities.py` — 리뷰 **통과** + Claude 머지
대상: impl `1aa88d8`(브랜치 `codex/2026-07-05-task011-new-capabilities`, 헤드 `c3425cf`) — 신규 게이트 `.harness/gates/check-new-capabilities.py`(304줄) + TASK-010 추출기 D-024 보강(+34줄, AC 인가) + 픽스처 `tests/fixtures/new-capabilities/`(new-only·delete-only·unreadable-head·unreadable-base·frozen-policy) + tests(cases +81·run-tests +72) + README 1줄. **2층 신규 능력 판정(`head − base`·exit 0/2·never-blocked)** — 계약 `docs/capability-catalog-design.md` Q5·Q6·Q2(D-022).
**계약 정합**: `base..head` 변경 `.py`(`--name-status --no-renames`)마다 TASK-010 추출기를 양측 ref 에서 `git show` 로 실행 → 파일별 capability id 집합의 **`head − base`**(신규 도입만) 판정. protected→`approval_required(2)` / watched-only→경고+`pass(0)` / 없음→`pass(0)`. 출력 `{gate,verdict,new_capabilities,warned_capabilities,fail_closed,errors,exit_code}` = Q7 정합.
**🔴 AC 실증(3종 전부, fresh 격리·픽스처 밖)**:
- **head−base 신규만(Q5)**: base·head 양쪽에 `subprocess_exec` 있는 파일(base `subprocess.run`, head 에 `subprocess.Popen` 추가 — 같은 id)은 **미검출**, 신규 파일 능력만 검출. **음성검증(rigged 차단)**: gate 의 `set(head_caps) - set(base_caps)` → `set(head_caps)` 로 변조 시 이미-있던 파일이 오검출(pass→approval)로 **FAIL** = head−base 가 실가드(base∪head 아님을 고정). 신규파일=전부 신규·삭제파일=신규 없음(Q5)도 픽스처.
- **never-blocked 불변식(Q2)**: fresh frozen-level catalog 주입 → `invalid_capability_level` 기록 + protected clamp → `approval_required`·exit 2, **결코 blocked/exit 1 아님**. **구조적 실증**: 게이트 소스에 `exit_code=1`/blocked 경로 자체가 부재(상수 `PASS=0`/`APPROVAL_REQUIRED=2` 뿐). 이중 안전: clamp 없어도 level `frozen`≠`watched` → `new_capabilities`(approval), blocked 승격 불가.
- **fail-closed per-path(Q6, A-0005)**: fresh 로 문법오류 head 파일 + 비-UTF8 head 파일이 **각각** per-path `fail_closed`(`head file could not be parsed after the change`) 로 뜨면서 **동시에** 무관한 신규 `requests`(outbound_network) 캡도 `new_capabilities` 에 살아있음 = **D-020 세탁 없음**(전역 "errors and not records" 조건이 아니라 파일별 무조건 `continue`). base 불능 → `base_caps` 빈 집합(head 능력 신규화) + `errors` 추가 → approval. 상위 예외 → 최상위 try/except 가 blocked 아닌 `approval_required` fail_closed(`<unknown>`).
**D-024 추출기 보강(AC 인가·검증)**: `resolve_getattr_call_name`(인라인 `getattr(<모듈>,"<리터럴>")(...)` → 점표기 해소) + `ast.Assign` 바인딩 전파(`z=os; z.system()`·연쇄 `s=z`)로 **call-only 모듈(os) 동적우회 2형태 폐쇄**. fresh 실증: 인라인 getattr·재대입·재대입연쇄 os.system 모두 감지, `valid.py` 회귀 픽스처(중첩 def 내 `import os`+두 형태)로 golden 고정. import-신호 모듈은 backstop 으로 무관.
**보수성(COMMON-RULES §1)**: 변경 = 신규 게이트 + 추출기 D-024 보강(AC 인가) + tests + README 1줄 + 인계기록만. **Claude 소유 무접촉**(`policies/sensitive-capabilities.yaml`·docs·CLAUDE·decisions·answers·review-notes·templates 미수정 — diff 확인), scope-creep 없음. `git diff --check`·`py_compile` PASS, 38/38 PASS·md5 결정성, 커밋 §3 준수.
**⚠️ 비차단 관찰 1건 → 차기 AC 가드(§2B 명시)**: D-024 🟠 가드가 명시한 **두 형태(인라인 getattr + 재대입)는 둘 다 닫히고 회귀픽스처화 = AC 충족**. 그러나 리뷰 중 **제3 변형 — 분리대입 getattr**(`fn = getattr(os,"system"); fn(c)`)가 call-only 모듈(os 계열)에서 **여전히 미감지**(신규캡·`unresolved_dynamic` 마커 전무, fresh 실증). 원인: `Assign` 핸들러가 value=Call(`getattr(...)`)를 `dotted_name` 로 해소 못 해 `fn` 미바인딩. **거버넌스 판단(§2B)**: (a) import-신호 모듈(subprocess/pickle/socket 등 주 실행벡터)은 import backstop 이 모든 난독을 포착·무영향, (b) 2층 approval 상한이라 최악도 "승인 프롬프트 누락"(오차단 아님·자동머지 아님), (c) D-024 가 이미 수용-후속처리로 분류한 "call-only 동적우회" 잔여의 **좁은 하위변형**, (d) 완전폐쇄엔 지역 dataflow(변수가 callable 보유) 추적 필요 = 대규모(§2B "대규모 리팩터 강요 금지") → **비차단**. 단 §2B "명시적으로 막는다" 대로 `TASKS.md` TASK-011 에 **차기 AC 가드**(분리대입 getattr 해소 또는 catalog 문서화 수용잔여)로 이월.
**머지 판정(D-007)**: 분석 전용 신규 능력 판정 게이트(exit 0/2·blocked 불가·2층 approval 상한) + 탐지 강화형 추출기 보강 — **비민감**(TASK-005~010 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** **MVP-1 Phase C 완결**(Phase D 는 TASK-012 D-023 로 기완료). 멱등성: 1aa88d8·c3425cf 재처리 금지.
상세: `review-notes.md` TASK-011 리뷰 절.

## D-026 (2026-07-05) TASK-011 follow-up — 분리대입 getattr 능력 감지 보강 `extract-python-capabilities.py` — 리뷰 **통과** + Claude 머지
대상: impl `b6cc23d`(브랜치 `codex/2026-07-05-task011-getattr-assignment`, 헤드 `96b8715`) — **D-025 비차단 관찰(제3 변형 분리대입 getattr) 해소**. 변경: 추출기 `build_import_bindings` 의 `ast.Assign` 핸들러가 value 를 `dotted_name` 로만 보던 것을 `resolve_getattr_call_name` 우선 시도(3줄) + 회귀 픽스처(`tests/fixtures/capabilities/valid.py` +1함수, `tests/cases.yaml` golden +1호출, 하류 `tests/fixtures/new-capabilities/getattr-assignment/` + `check-new-capabilities` 케이스). 델타 소.
**AC 정합(TASKS.md TASK-011 line 138 차기 가드)**: 가드는 `<var> = getattr(<모듈>,"<리터럴>")` 를 바인딩표에 전파해 후속 `<var>(...)` 호출을 해소하거나 catalog 수용잔여 문서화를 요구 — **전자로 구현**. `command_runner = getattr(os,"system")` 뒤 `command_runner(cmd)` 가 `os.system` 으로 해소돼 call-only 모듈(os) 신규 능력 `subprocess_exec` 판정에 포함됨.
**🔴 심층·적대적 실증(fresh 격리·픽스처 밖)**:
- **[A] POSITIVE**: fresh `import os / fn=getattr(os,"system"); fn(cmd)` → `subprocess_exec level=protected signals=call:os.system` 검출 ✓ (D-025 관찰 폐쇄).
- **[음성검증·rig-and-revert]**: 3줄 `resolve_getattr_call_name` 우선분기를 되돌려 `dotted_name` 단독으로 rig → 테스트 **37/39**(추출기 golden + 하류 `new-capabilities-getattr-assignment` **2건 FAIL**) + fresh [A] MISS. 원복 39/39. → 신규 golden/케이스가 실가드(항상-PASS 아님) 실증.
- **[C] 동적 정상거부**: `fn=getattr(os,name)`(2번째 인자 변수) → 미해소 MISS(정적 판별 불가·수용 dynamic). **[D] 오탐 없음**: `getattr(os,"getcwd")`(비민감) → `subprocess_exec` 무발동.
- **하류 영향**: 추출기 출력(capabilities)은 `check-new-capabilities` 가 `head−base` 로 소비 → 신규 파일에서 이 형태가 이제 신규 능력으로 잡혀 approval 로 승격(2층 상한 유지·blocked 아님). 정합.
**⚠️ 비차단 관찰 1건(§2B 명시 → 차기 AC 가드)**: 리뷰 중 **더 좁은 잔여 하위변형** fresh 실증 — `import os as o; fn=getattr(o,"system"); fn(cmd)`(**별칭 base + getattr + 분리대입** 삼중난독)는 **여전히 미감지**. 원인: `Assign` 핸들러가 `resolve_getattr_call_name` 이 이미 `o→os` 해소해 반환한 `os.system` 을 **다시 partition** 해 root `os` 를 bindings 에서 찾는데, 바인딩된 건 별칭 `o` 뿐이라 `root not in bindings → continue`(이중 해소 결함). 직접 별칭 호출 `o.system(cmd)` 은 정상 감지([B2] 실증). **거버넌스 판단(§2B)**: (a) import-신호 모듈(주 실행벡터)은 import backstop 이 모든 난독 포착·무영향 — 이 갭은 오직 call-only os 계열 삼중난독 한정, (b) 2층 approval 상한 → 최악도 승인 프롬프트 누락(오차단·자동머지 아님), (c) TASKS.md line 138 이 이미 "완전폐쇄엔 지역 dataflow 추적 필요 → 차기 가드로 이월/catalog 문서화 수용잔여" 를 허용, (d) 명시 AC(plain 형태 + 회귀픽스처)는 충족 → **비차단**. **개선 제안(내가 짠다면)**: getattr 경로가 잡히면 이미 완전 해소된 값이므로 재-partition 없이 그대로 `target` 으로 쓰면 별칭 base 도 무료 폐쇄(3줄). §2B "대규모 리팩터 강요 금지"·명시 AC 충족이므로 보정요청 아닌 차기 가드로 이월.
**보수성(COMMON-RULES §1)**: 변경 = 추출기 3줄 + tests/fixtures + summaries/handoff 인계기록만. **Claude 소유 무접촉**(policies·docs·CLAUDE·decisions·answers·review-notes·templates — diff 확인), scope-creep 없음. 39/39 PASS·`git diff --check`·`py_compile` PASS.
**머지 판정(D-007)**: 분석 전용 추출기 탐지 강화(exit 0·판정 없음·차단 불가·2층 approval 상한) — **비민감**(TASK-005~011 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** 멱등성: b6cc23d·96b8715 재처리 금지.
상세: `review-notes.md` TASK-011 follow-up 절.

## D-027 (2026-07-05) TASK-011 follow-up — 별칭 base + getattr 삼중난독 능력 감지 보강 `extract-python-capabilities.py` — 리뷰 **통과** + Claude 머지
대상: impl `27716df`(브랜치 `codex/2026-07-05-next-task`, 헤드 `d5548eb`) — **D-026 비차단 관찰(별칭 base + getattr + 분리대입 삼중난독) 해소**. 변경: 추출기 `build_import_bindings` 의 `ast.Assign` 핸들러가 `resolve_getattr_call_name(node.value, bindings, require_bound_base=True)` 로 이미 완전 해소된 `os.system` 을 **재-partition 없이 그대로 `target`** 으로 전파(getattr 파생 함수 `require_bound_base` 파라미터 추가: base root 미바인딩이면 `None` 반환→dotted 경로로 폴백/드롭) + 회귀 픽스처(`valid.py` +1함수·`cases.yaml` golden line77·하류 `new-capabilities/getattr-assignment-alias/`). 델타 소(추출기 실질 ~5줄).
**AC 정합(TASKS.md TASK-011 line 140 D-026 잔여 가드)**: 가드는 "getattr 경로가 잡히면 값이 이미 완전 해소돼 있으므로 재-partition 없이 그대로 `target` 으로 사용" 또는 catalog 수용잔여를 요구 — **전자로 구현**(정확히 D-026 리뷰 "내가 짠다면" 제안대로). `import os as o; alias_runner = getattr(o,"system")` 뒤 `alias_runner(cmd)` 가 `os.system` 으로 해소돼 call-only os 계열 신규 능력 `subprocess_exec` 판정에 포함됨.
**🔴 심층·적대적 실증(fresh 격리·픽스처 밖, 워크트리 재현)**:
- **[A] POSITIVE**: fresh `import os as o; fn=getattr(o,"system"); fn(cmd)` → `subprocess_exec level=protected signals=call:os.system` 검출 ✓ (D-026 관찰 폐쇄). **[G] 오염 없는 고립 실증**: 형제 `import os`(bare) 없는 모듈레벨 `import os as o` 단독에서도 검출 ✓ — 폴리션 아닌 실제 해소임을 확정.
- **[B] 비-별칭 회귀**: `import os; r=getattr(os,"system"); r(cmd)` 여전히 검출 ✓(`require_bound_base=True` 가 기존 경로 무손상). **[E] 연쇄 별칭**: `p=o; getattr(p,"system")` 도 검출 ✓(요구 이상 강건).
- **[음성검증·rig-and-revert]**: `Assign` 핸들러를 D-026 이전(재-partition) 로직으로 되돌리면 하류 `new-capabilities-getattr-assignment-alias` **FAIL(39/40)**, 원복 40/40 = 신규 하류 픽스처가 실가드(항상-PASS 아님). **[중요 관찰] `valid.py` golden(line77)은 revert 후에도 PASS** — 같은 파일 형제함수의 bare `import os` 가 모듈공유 `bindings` 에 `os→os` 를 남겨(함수 스코프 없음) 별칭 경로가 우연히 해소됨. 즉 `valid.py` line77 은 **약한/중복 가드**(fix 없이도 통과)이고, 진짜 독립 가드는 하류 `getattr-assignment-alias` 픽스처(형제 오염 없음). 오탐 아님(현행 동작 정확 기록)이나 독립 증명력 없음 → 비차단 관찰.
- **[C] 동적 정상거부**: `getattr(o,name)`(2번째 인자 변수) → 미해소 MISS(정적판별 불가·수용 dynamic). **[D] 오탐 없음**: `getattr(o,"getcwd")`(비민감) → `subprocess_exec` 무발동. **결정성**: 동일입력 md5 2회 동일.
- **하류 영향**: 추출기 capabilities → `check-new-capabilities` 가 `head−base` 로 소비 → 신규파일 이 형태가 신규 능력으로 승격(2층 approval 상한·blocked 아님). 정합. 하류 케이스 `signal_names:[os.system]`·exit 2·reviewer `security-reviewer` 검증.
**⚠️ 비차단 관찰 2건(§2B)**:
1. **`valid.py` line77 약한 가드**(위 rig 관찰): 함수 스코프 없는 모듈공유 `bindings` 의 형제 `import os` 오염으로 fix 없이도 통과. 하류 픽스처가 실가드라 커버 문제 없음 → **비차단**. (개선 여지: `valid.py` 별칭함수에서 형제 bare-import 제거 시 독립 가드화 — 강요 안 함.) 부수 관찰: **함수 스코프 없는 flat bindings** 는 선재 설계 속성이며, 오염의 방향은 "더 많은 해소=더 많은 탐지"(거버넌스 안전측·오탐≤approval)라 miss 유발 아님 → 비차단.
2. **getattr-builtin 별칭 잔여**(fresh 실증 [F]): `g=getattr; g(o,"system")` 미감지 — `resolve_getattr_call_name` 이 `func.func.id != "getattr"` 로 조기반환. D-024/D-025 가 이미 문서화 수용한 "call-only 동적우회" 계열의 더 깊은 변형(무한퇴행). import-신호 모듈 backstop 무영향·2층 상한 → **비차단·catalog 수용잔여**(TASKS.md line 140 밑 신규 명시). 신규 AC escalation 아님 — 지역 dataflow 도입 시 일괄 폐쇄 대상.
**보수성(COMMON-RULES §1)**: 변경 = 추출기 ~5줄 + tests/fixtures + summaries/handoff 인계기록만. **Claude 소유 무접촉**(policies·docs·CLAUDE·decisions·answers·review-notes·templates — diff 확인), scope-creep 없음. 40/40 PASS·`git diff --check`·`py_compile`(extract·check-new-capabilities) PASS.
**머지 판정(D-007)**: 분석 전용 추출기 탐지 강화(exit 0·판정 없음·차단 불가·2층 approval 상한) — **비민감**(TASK-005~011 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** 멱등성: 27716df·d5548eb 재처리 금지.
상세: `review-notes.md` TASK-011 follow-up(D-027) 절.

## D-028 (2026-07-09) TASK-018 정책 완화/집행-우회 게이트 `check-policy-change.py` — 리뷰 **보정요청**(집행-우회 `continue-on-error` 변형 우회 + AC#7 픽스처 미비) · 겸 Q-0002 답변(자기보호 등록 완료)
대상: impl `c4621fc`(브랜치 `codex/2026-07-09-task018-policy-change`, 헤드 `933c017`) — 신규 게이트 `.harness/gates/check-policy-change.py`(491줄) + 픽스처 6종 + 러너/cases 확장.
**판정 = 보정요청, 코드 브랜치 머지 보류.** 정책 의미-diff(AC #1~5)는 강건·전부 실증(fresh 적대 입력: 존 하향·`required_approval` 제거·glob 협소화·`max_verdict` 약화·`block_levels` 공백화·capability 삭제·routing 동수 스왑 모두 approval 정확 / 키재정렬·주석 pass / 종료코드 0·2 만 / 음성검증 rig-and-revert 로 approval-기대 4케이스 FAIL·pass-기대 2케이스 유지 = 실가드 실증). 46/46 PASS·`git diff --check`·`py_compile` OK. 보수성 OK(Claude 소유 무접촉·scope-creep 없음).
**🔴 R-1(보정)**: 집행-우회 감지 `detect_enforcement_bypass` 가 `continue-on-error: true` **정확 부분문자열**(소문자·단일공백·무따옴표)만 매칭 → GHA/YAML 이 동등 수용하는 `True`·`TRUE`·`"true"`·여분공백 변형은 **집행 무력화하면서 게이트 pass**(fresh 5변형 실증: 정준형만 approval, 나머지 4종 우회). AC #7(b) "무력화 삽입 감지" 미충족 + P0 자기무력화 방지 목적에 **직접 구멍**(§2B 필수질문=그렇다 → 비차단 불가). 수정 계약: `continue-on-error` 값 truthy 를 **결정적 정규화 매칭**({true,yes,on}·따옴표/공백 무관 — 여전히 패턴 매칭, "의미 추정 금지" 위반 아님).
**🟠 R-2(보정)**: AC #7 은 (a)호출제거·(b)`||true`/`continue-on-error` 삽입·(c)required-check 제거 **픽스처 각 1건** 요구. 현재 (a)=runner-removal·(b)정준형=runner-bypass 만 존재 → **(b)`continue-on-error` 변형·(c)required-check 제거 픽스처 부재**(c 감지코드는 동작하나 회귀 미고정). R-1 변형 + (b)(c) 픽스처 추가.
**비차단 관찰(catalog·수정 강요 없음)**: O-1 넓은 존 유지 + 하위 약한 carve-out 존 **추가**는 유효보호 축소이나 pass(존 precedence 해석 필요 = 의미영역; path/level 직접 편집 축소는 이미 포착) → MVP-2. required-check 감지는 워크플로 내 부분문자열 best-effort(실 branch-protection 은 repo 설정에 상주) — AC "생기면" 한정이라 현행 허용.
**AC #6 / Q-0002 처리(Claude 소유 = 직접 반영)**: `policies/**`·`.harness/**`·`tests/run-tests.sh`·`tests/cases.yaml`·`.github/workflows/**`·`CODEOWNERS` 를 `policies/sensitive-zones.yaml` 에 **protected**(승인요구, 차단 아님) 등록 — 이번 리뷰 브랜치에서 반영. **load-bearing**: 게이트 로직 자체 무력화(항상-pass 편집)는 `check-policy-change` 스스로 못 잡고 이 등록만 `check-sensitive-zones` 로 포착(실증: `.harness/gates/*.py`·`tests/cases.yaml` 편집 → approval_required). level=protected(frozen 아님) = 하네스 진화 + 자기보호 양립·2·3층 자동차단 금지 정합. **운영부담 형 인지 필요**(harness/tests 편집 매번 승인요구 — 과하면 형이 범위축소) — A-0006 §Q-0002 명시.
**AC #8 미해결(비차단·추적)**: policy bundle digest(판정 시점 정책 파일 해시목록)를 감사카드에 기록 — 이 브랜치 미구현. `generate-change-evidence.py`(Codex)+`change-evidence.template.yaml`(Claude) 동시 개정 필요이며 TASK-019(카드 정직화·버전기록 확장)와 동일 파일 겹침 → **TASK-019 와 함께 처리**로 이관(게이트 자체 결함 아님, 별도 감사카드 산출물).
**머지 판정(D-007)**: 코드 브랜치 **보류**(R-1·R-2 보정 재제출 = 보정 델타만 재리뷰, 멱등성 `c4621fc`·`933c017` 재처리 금지). 리뷰 기록(decisions·review-notes·answers/A-0006) + 자기보호 등록(sensitive-zones) 은 **main 머지**(다음 세션·Codex 가시성). 상세: `review-notes.md` TASK-018(D-028) 절.

## D-029 (2026-07-09) TASK-018 보정 재제출(2차) 재리뷰 `check-policy-change.py` — R-1·R-2 해소 확인 · 신규 R-3 **보정요청**(인라인 주석 변형 우회)
대상: 보정 재제출 `297acac`(브랜치 `codex/2026-07-09-task018-policy-change`, 헤드 `0e28580`) — 선행 D-028/A-0006 의 R-1·R-2 보정. **R-3 델타만 재리뷰**(멱등성: `297acac`·`0e28580` 의 R-1/R-2 부는 재검증 완료·재론 금지, `c4621fc`·`933c017` 재처리 금지).
**판정 = 보정요청(2차), 코드 브랜치 머지 계속 보류.**
**R-1 해소 확인 ✓**: 신규 `is_gate_bypass_line` 이 `|| true` 는 `\|\|\s*true\b`, `continue-on-error` 는 키정규화+unquote+소문자화 후 `{true,yes,on}` 매칭. fresh 적대 8종 전부 정확 — `true`/`True`/`TRUE`/2칸/`"true"`/`'true'`/`yes`/`on` → **approval_required**, `false`(음성대조) → **pass**. A-0006 지목 4우회 폐쇄. 정규화는 결정적 패턴매칭(의미추정 아님·AC #7 준수).
**R-2 해소 확인 ✓**: (b)`runner-continue-on-error`(head `continue-on-error: True`)·(c)`required-check-removal`(head `required` 제거) 픽스처 추가. **rig-and-revert 음성검증 각각 성립**: truthy 집합 무력화 → (b) 단독 FAIL(47/48)·원복 48/48 / required-check 분기 `if False` → (c) 단독 FAIL(47/48)·원복 48/48 = 두 픽스처 실가드(교차오염 없음). 전체 48/48 PASS·`git diff --check`·`py_compile` OK.
**🔴 R-3(보정·신규)**: R-1 을 깨려 만든 fresh 적대 입력서 **동일 계열(AC #7b) 신규 미탐** 발견 — `continue-on-error: true # keep going`(인라인 주석 첨부) → **pass**(우회). YAML 플레인 스칼라의 ` #` 인라인 주석은 파서가 벗겨 값=`true` → GHA 집행 무력화하나, 게이트는 `unquote_scalar` 가 주석을 안 벗겨 `"true # keep going"` ∉ `{true,yes,on}` → 미탐(`python3` 분해 재현). 주석 첨부(`# ops-approved` 등)는 GHA 유효·**가장 자연스러운 서술형**이라 R-1 변형보다 흔함. **§2B 필수질문=그렇다**(R-1 동일계열·집행 OFF·초록불 거짓안심·P0 직접구멍) → 비차단 불가. **무한퇴행 아님**: YAML truthy 철자집합 유한·확정 → 주석-strip 추가면 계열 완결(R-1 처럼 닫힘). D-024 계열 "지역 dataflow 필요·정적판별 불가" 수용잔여와 성격 다름(이건 결정적·완결·P0 집행경로). **수정계약**: `is_gate_bypass_line` 국소 — 플레인 스칼라값 첫 ` #` 이후 절단 후 strip·소문자화(따옴표값은 unquote 후 내부 `#` 문자열 일부라 불요) + 회귀픽스처 1건(주석 변형→approval)+음성검증.
**비차단 관찰**: O-2 숫자 `continue-on-error: 1` → 미탐이나 GHA 가 정수 `1` 을 boolean true 로 수용하는지 자체 불확실(정준형 아님) → R-3 필수범위 아님·과탐추가 지양(MVP-2). O-1(넓은 존+약한 carve-out 추가) 선행 유지(MVP-2).
**공정성 메모**: R-3 은 Codex 불이행 아님 — A-0006 계약({true,yes,on}·따옴표/공백)은 정확 이행. 인라인 주석 벡터는 **내 A-0006 계약 누락**이 적대 재검증서 드러난 것. 책임귀속 무관·산출물 거버넌스-직결 결함이라 §2B 대로 머지 전 폐쇄(보정 델타 국소·유한 → 무한 보정루프 아님).
**머지 판정(D-007)**: 코드 브랜치 **계속 보류**(R-3 델타만 재리뷰). 이 재리뷰 기록(decisions D-029·answers A-0007·review-notes·handoff·summaries) → **main 머지**. 상세: `review-notes.md` TASK-018(D-029) 절 · `collab/answers/A-0007.md`.

## D-030 (2026-07-09) TASK-018 보정 재제출(3차) 재리뷰 `check-policy-change.py` — R-3 해소 확인 **통과** + Claude 머지 (MVP-1.5 TASK-018 완결)
대상: R-3 보정 재제출 `ab4447a`(브랜치 `codex/2026-07-09-task018-policy-change`, 헤드 `f966394`) — 선행 D-029/A-0007 의 R-3 보정. **R-3 델타만 재리뷰**(멱등성: `c4621fc`·`933c017`·`297acac`·`0e28580`·`ea59947`·`5691329` 재처리 금지; 5691329 는 origin/main 리뷰기록 동기화 머지·코드 무변경 확인).
**판정 = 리뷰 통과, Claude 머지.**
**R-3 해소 확인 ✓**: `unquote_scalar` → `normalize_yaml_plain_scalar`(단일 caller `is_gate_bypass_line` 국소·타 경로 무영향 확인) 로 교체. 값 정규화가 따옴표 상태를 추적하며 **따옴표 밖·앞선 공백 있는 첫 `#`** 에서 절단(YAML 플레인 스칼라 인라인 주석 규칙 정확 구현) 후 기존 unquote·소문자화·`{true,yes,on}` 매칭. 계약(A-0007 수정계약)에 **정합**.
**적대 재검증(fresh·픽스처 밖, 함수 직접 호출 19종)**: ① **R-3 핵심 폐쇄** — `true # keep going`/`True # ops-approved`/`yes # x`/`on # x`/`'true' # c`/`"true" # c`/탭+`#`/다중 `#`(`true # a # b`) 전부 **감지(approval)**. ② **YAML 의미 정확** — `true# nospace`(공백 없는 `#` = YAML 상 주석 아님, 값 literally `true# nospace`) **미감지 유지**(과탐 아님·정합), `"tr#ue" # c`(따옴표 안 `#` 은 값 일부, 실제 값 `tr#ue` 비-truthy) **미감지 유지**, 빈값 `# only comment` 미감지. ③ **R-1 무회귀** — `true`/`True`/2칸/`"true"` 여전히 감지·`false` pass. ④ `|| true`·`|| true # note` 경로 무영향. **19/19 기대 일치**.
**음성검증(rig-and-revert)**: 주석-strip 블록 제거 → 신규 픽스처 `policy-change-runner-continue-on-error-comment` **단독 FAIL(48/49)**, 원복 **49/49 PASS** = 실가드(항상-PASS 아님). 전체 `bash tests/run-tests.sh` **49/49 PASS**·`git diff --check`(0e28580..head) clean·`py_compile` OK.
**보수적 개발(§1)**: R-3 코드 델타(`ab4447a`)는 `check-policy-change.py`(14줄)+`tests/cases.yaml`(1케이스)+신규 픽스처 2파일만 = 계약 범위 국소. Claude 소유 파일 무접촉. scope-creep 없음. 범위 내 A-0006/A-0007/decisions/review-notes/sensitive-zones 는 origin/main 리뷰기록의 브랜치 동기화 머지(`5691329`)로 들어온 **내 기존 기록**(origin/main 과 동일 확인·Codex 변조 없음) — Codex 산출 아님.
**비차단(선행 유지·MVP-2 catalog)**: O-2 숫자 `continue-on-error: 1`(GHA 정수→boolean 수용 불확실·정준형 아님·과탐 지양), O-1(넓은 존+약한 carve-out 존 추가), AC #8 policy bundle digest(TASK-019 와 동일 파일 겹침 → 함께 처리). 모두 거버넌스 직접구멍 아님(§2B 필수질문=아니오).
**머지 판정(D-007)**: `check-policy-change.py` = **분석·판정 게이트**(exit 0/2·approval 상한·자동차단 불가·2층) — **비민감**(TASK-005~013 전 계열 동일 범주·D-020~027 선례; TASK-018 코드는 R-1~R-3 보정 대기로만 보류였음). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push.** **MVP-1.5 TASK-018 완결.** 상세: `review-notes.md` TASK-018(D-030) 절 · `collab/answers/A-0007.md` §R-3 해소.

## D-031 (2026-07-09) TASK-019 감사카드 정직화(coverage statement) `generate-change-evidence.py` — **보정요청**(예외 카드 정직성·스키마 드리프트)
대상: `codex/2026-07-09-task019-coverage-statement` · impl `d8ad086` · 핸드오프 헤드 `195a957`. 신규 태스크(초회 리뷰). 파일: `.harness/gates/generate-change-evidence.py`(+71) · `templates/change-evidence.template.yaml` · `tests/cases.yaml` · `tests/run-tests.sh`(+28) · 문서.
**판정 = 보정요청, 코드 브랜치 머지 보류.**
**정상 경로 통과 확인(AC #1~#4 실증)**: verdict pass 문구 `no governance violation detected` 통일·`safe`/`안전` 부재(`no_safe_text` 가드). coverage `checked` 는 **실행 술어**(`can_run_function_gov`) 기반 동적 — baseline(name-status 파일=function-gov 미실행)=2게이트 vs function 케이스(base..head ref)=3게이트로 정직히 갈림(AC #2). `python_version`(`sys.version.split()[0]`)+`tool_version`+`policy_sha`(sha256 64hex) 추가(AC #3). 정상카드 top-level 키==템플릿 17키(AC #4). **음성검증 2종 성립(직접 재현)**: ① `executed_gate_records`→`if True` 변조 시 baseline FAIL(`expected 2, got 3`)=동적성 실가드, ② pass 문구에 `(safe)` 주입 시 `no_safe_text`+`verdict_statement` 동시 FAIL=정직성 실가드. `tests/run-tests.sh` **49/49 PASS**·`git diff --check`·`py_compile` 전부 재현.
**🔴 R-1 — 예외/오류 카드가 미실행 게이트를 "검사했다"고 위조(AC #2 위반)**: `main()` 예외 핸들러(=`build_evidence` 가 `load_intent` 등서 throw)가 `coverage_statement(diff_input,"blocked")` 를 그대로 호출 → 게이트 **0개 실행인데** `verdict_statement: governance violation detected` + `checked:[check-change-intent, check-sensitive-zones, check-function-gov-level]`(3게이트) 출력. **fresh 입력 실증**: `generate-change-evidence.py HEAD~1..HEAD --change-intent /nonexistent.yaml` → 게이트 0 실행·`policy_sha:{}`·`reasons:['의도 선언 누락…']` 이면서 checked 3게이트 위조 재현. AC #2 명문("정적 문구 아니라 실행된 게이트 기반 — 빼고 돌리면 본 것이 줄어야 정직")에 정면 위배 = **이 태스크가 없애려는 안티패턴을 신규 coverage 블록이 도입한 정직성 회귀**. 내부 모순이 의도 증명: `policy_sha:{}` 는 정직히 비우면서 `checked` 만 3게이트 위조. §2B 필수질문=그렇다(카드 정직성=이 태스크의 거버넌스 기능 자체·초록불 아닌 fail-closed지만 "실행 안 한 걸 했다"는 위조는 이 태스크 목적 직접 훼손). 도달성 높음(루트 `change-intent.yaml` 부재+`--change-intent` 미지정 기본호출·정책 YAML 파손·git 오류). **수정계약(국소)**: 실행 게이트 0이면 오류 카드 `coverage_statement.checked=[]`(주변 `policy_sha:{}`·`changed_files:[]` 처럼 정직히 비움). 정상경로(진짜 frozen→blocked 의 `governance violation detected`) **무변경**. 회귀 픽스처(오류 카드→checked[])+음성검증.
**🟠 R-2 — 오류 카드 스키마 드리프트: `changed_functions` 누락(AC #4 위반)**: 오류 카드 dict = 16키(template/정상카드 17키에서 `changed_functions` 빠짐). 이 태스크가 `changed_functions` 를 템플릿에 추가하며 오류 카드엔 미반영. `schema_keys_match_template` 가드는 **정상경로 4픽스처에서만** 돌아 오류 카드 미검사 → "스키마==템플릿" 거짓확신. **수정계약**: 오류 카드에 `changed_functions:[]` 추가 + **오류경로 픽스처 1건** 추가해 `schema_keys_match_template`·R-1 `checked[]` 를 오류 카드에도 적용.
**비차단 관찰(MVP-2)**: O-1 `schema_keys_match_template` 는 top-level 키만 비교(중첩 임의키 미포착) — 현재 coverage 단언이 사실상 커버하므로 비차단. AC #8 policy bundle digest 는 `policy_sha`(sensitive-zones·approval-routing sha256)로 부분충족·전체번들 확장은 MVP-2.
**공정성 메모**: 정상 경로 구현은 견고하고 AC 정신을 잘 구현. R-1/R-2 는 **예외 카드**에 국한된 정직성/스키마 누락 — 저비용·국소 보정(무한루프 아님). 산출물이 거버넌스-직결(카드 정직화 태스크)이라 §2B 대로 비차단 방류 않고 머지 전 폐쇄.
**머지 판정(D-007)**: 코드 브랜치 **보류**(R-1·R-2 델타만 재리뷰). 이 리뷰기록(decisions D-031·answers A-0008·review-notes·handoff·summaries) → **main 머지**(다음 세션·Codex 가시성). 상세: `review-notes.md` TASK-019(D-031) 절 · `collab/answers/A-0008.md`.
