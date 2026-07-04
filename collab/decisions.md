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
