# review-notes.md — Claude 리뷰 기록 (정책 의도 대비 검수)

> 게이트가 "도는지"가 아니라 "내가 의도한 위험을 잡는지"를 본다.
> 결과 승급은 `collab/decisions.md`. 여기는 근거·검증·비차단 관찰.

---

## TASK-001 `check-change-intent` — 리뷰통과 (2026-06-29)

- 대상: commit `ff75529`, 브랜치 `codex/2026-06-29-task001-change-intent`
- 파일: `.harness/gates/check-change-intent.py` (신규 192줄)
- 결정: **D-006 리뷰통과**

### 수용기준 6/6 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | intent 누락 → 실패 + "의도 선언 누락" | ✅ blocked(1), 메시지 출력 | 없는 경로 전달 → exit 1 |
| 2 | allowed 안에만 → 통과 | ✅ pass(0) | admin 2파일 → exit 0 |
| 3 | allowed 밖 → out_of_scope, 승인(2) | ✅ approval(2) | reporting 파일 → exit 2 |
| 4 | forbidden 닿음 → 차단(1) | ✅ blocked(1) | auth 파일 → exit 1 |
| 5 | glob `**`/`*`, OS 무관 | ✅ | 아래 엣지 표 |
| 6 | 변경 0건 → 통과 | ✅ pass(0) | 빈 입력 → exit 0, "changed_files: 0" |

### glob 엣지 검증 (커스텀 매처라 별도 확인)
| 케이스 | 기대 | 결과 |
|---|---|---|
| `src/*` vs `src/a/b.py` (`*`는 `/` 안 넘음) | out_of_scope | ✅ exit 2 |
| `src/*` vs `src/a.py` | pass | ✅ exit 0 |
| `**/settlement/**` vs `backend\core\settlement\calc.py` (백슬래시) | blocked | ✅ exit 1 (정규화) |
| 리네임 `R100 old → settlement/new` (목적지 경로 판정) | blocked | ✅ exit 1 |
| forbidden + out_of_scope 동시 | blocked(우선) | ✅ exit 1 |

### 판정 우선순위 (이 게이트 한정, 확정)
`forbidden(blocked,1)` > `out_of_scope(approval_required,2)` > `pass(0)`.
한 파일이 forbidden∩allowed 면 forbidden 우선(코드 `in_forbidden` 선검사). TASK-003 최종 verdict 합성과 일관.

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 게이트 1개(신규) + `handoff-log.md`(+1줄, 허용) + `summaries/2026-06-29.md`(신규, 공동출력). **Claude 소유 파일 무수정.**
- 무관 리팩터/포맷/이름변경 없음. diff 최소. **scope-creep / over-reach 없음.**
- 결정성: 출력에 시각·난수 없음, `--json`은 `sort_keys=True`. 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — 후속 태스크에서 정합만 맞추면 됨)
1. **광범위 `except Exception → blocked(1)`**: git ref 오류·YAML 파싱오류 등 *도구 오류*도 정책 *차단*과 같은 exit 1 로 수렴(fail-closed). MVP-0 종료코드 계약(0/1/2)에 별도 에러코드가 없어 안전한 선택. 단 사람이 "정책 차단"과 "실행 실패"를 출력 메시지로 구분할 수 있어야 함 — 현재 `error` 필드/`BLOCKED: <error>` 로 구분됨. 수용.
2. **intent 파일은 있으나 내용 비정상**(`change_intent` 키 없음/빈 allowed): 모든 변경이 out_of_scope → approval(2). 누락(파일없음)=blocked 와 다른 결과인데, 의도적 fail-safe 로 수용. TASK-004 에서 별도 fixture 불필요(수용기준 미요구).
3. **리네임 source 경로**: 목적지만 판정(표준). forbidden→밖으로 나가는 리네임은 안 잡지만 MVP-0 범위상 수용.

→ 위 3건은 **차단 사유 아님**. TASK-002/003/004 진행 시 정합(특히 #1 의 verdict 합성, #2 의 fixture 기대)만 유지하면 됨.

---

## TASK-002 `check-sensitive-zones` — 리뷰통과 (2026-06-30)

- 대상: commit `704f7a0`, 브랜치 `codex/2026-06-30-task002-sensitive-zones`
- 파일: `.harness/gates/check-sensitive-zones.py` (신규 245줄)
- 결정: **D-008 리뷰통과 + Claude 머지(비민감)**

### 수용기준 6/6 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | frozen 닿음 → 차단(1), 사유에 path+reason | ✅ blocked(1) | `src/settlement/calc.py` → exit 1, `frozen: <path> (<reason>)` |
| 2 | protected 닿음 → 승인요구(2), required_approval 포함 | ✅ approval(2) | `src/auth/login.py` → exit 2, `required_approval=security-reviewer` |
| 3 | watched 닿음 → 통과+경고(0) | ✅ pass(0) | `src/common/util.py` → exit 0, "PASS: watched ..." |
| 4 | zones 미매칭만 → 통과 | ✅ pass(0) | `src/ui/button.tsx` → exit 0, 경고 없음 |
| 5 | block/approve/warn_levels 를 policy 에서 읽음(하드코딩 금지) | ✅ | protected→block_levels 로 옮긴 policy 에서 auth 가 blocked(1) 로 변함 |
| 6 | 다중 level 매칭 → 가장 강한 것 채택 | ✅ | `src/settlement/common/x.py` (frozen∩watched) → blocked(1) |

### 엣지 검증
| 케이스 | 기대 | 결과 |
|---|---|---|
| 리네임 `R100 old → auth/new` (목적지 경로 판정) | approval | ✅ exit 2 (`parts[2]` 사용) |
| `**/*.k8s.yaml` vs `deploy/app.k8s.yaml` | approval | ✅ exit 2 |
| `db/migrations/**` vs `db/migrations/001_add.sql` | approval | ✅ exit 2 |
| mixed frozen+protected+watched 한 diff | blocked + 세 목록 전부 증거 보존 | ✅ exit 1, frozen/protected/watched_touched 각각 채워짐 |
| 빈 diff | pass | ✅ exit 0, "changed_files: 0" |
| policy 파일 없음 | blocked(fail-closed) | ✅ exit 1, `BLOCKED: <error>` |

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 게이트 1개(신규) + `handoff-log.md`(+1줄) + `summaries/2026-06-30.md`(신규). **Claude 소유 policy 무수정.**
- 무관 리팩터/포맷/이름변경 없음. TASK-001 의 glob 매처·종료코드 계약·`sort_keys=True`·fail-closed 패턴을 일관되게 재사용. **scope-creep / over-reach 없음.**
- 결정성: 출력에 시각·난수 없음, 목록 `sorted`, `--json` `sort_keys=True`. 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — 후속 태스크에서 정합만)
1. **분류되지 않은 level 은 조용히 무시**: zone 의 `level` 이 block/approve/warn 어디에도 없으면 `level_strength=0` → 어떤 touched 목록에도 안 들어가 통과 처리됨. 현 policy 는 모든 level 이 frozen/protected/watched 라 무해. 단 정책 작성자가 오타(예: `protcted`)를 내면 *조용히 통과*될 수 있음 — MVP-1 에서 "미분류 level 경고" 고려. 수용.
2. **같은 path 가 동급 protected 여러 zone 매칭 시 중복 레코드**(예: `infra/**` ∩ `*.k8s.yaml`): 둘 다 출력됨(둘 다 platform-reviewer). 차단 판정엔 무영향, TASK-003 의 `reviewer_required` 중복제거에서 정리 예정. 수용.
3. **fail-closed 광범위 except → blocked(1)**: TASK-001 #1 과 동일 설계. 도구오류와 정책차단을 `error` 필드/`BLOCKED: <error>` 메시지로 구분. 수용.

→ 위 3건은 **차단 사유 아님**. TASK-003(`generate-change-evidence`) 에서 #2 의 reviewer 중복제거, verdict 합성(frozen/forbidden→blocked) 정합만 유지하면 됨.

---

## TASK-003 `generate-change-evidence` — 리뷰통과 (2026-06-30)

- 대상: commit `f2ecb50`, 브랜치 `codex/2026-06-30-task003-evidence`
- 파일: `.harness/gates/generate-change-evidence.py` (신규 476줄)
- 결정: **D-009 리뷰통과 + Claude 머지(비민감)**

### 수용기준 5/5 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | `changed_files[].zone_level`·`in_allowed_paths` 정확 | ✅ | admin=free/allowed=true, common=watched, auth=protected, settlement∩common=frozen |
| 2 | verdict = (frozen/forbidden→blocked) > (protected/out_of_scope→approval) > pass | ✅ | settlement→blocked(1), auth(forbidden)→blocked(1), crypto(protected+oos)→approval(2), allowed-only→pass(0) |
| 3 | `reviewer_required` 중복제거 | ✅ | auth×2+security+crypto → `security-reviewer` 단일. multi-route 파일 둘 다 보존+전체 dedup |
| 4 | `base_commit` 기록(멱등성)·`summary` 파일/라인 수 정확 | ✅ | git ref: base_commit=실제 rev-parse(=main), files=3·lines+482 (numstat 일치) |
| 5 | 출력 yaml 템플릿 스키마 키 일치(임의 키 추가 금지) | ✅ | 재귀 키셋 비교: 최상위/중첩 전부 일치, 누락 0, 임의 최상위 키 0 |

### 엣지/추가 검증
| 케이스 | 기대 | 결과 |
|---|---|---|
| 다중 zone(settlement∩common) zone_level | 가장 강한 frozen | ✅ frozen 채택 (TASK-002 strongest 일관) |
| 빈 diff | pass, files_changed=0, reviewer_required=[] | ✅ exit 0 |
| change-intent 누락 | fail-closed blocked(1), reasons 에 "의도 선언 누락" | ✅ verdict blocked, exit 1 |
| sensitive-zones policy 누락 | fail-closed blocked(1) | ✅ exit 1 |
| 결정성(2회 실행) | 동일 출력 | ✅ byte-identical (sort_keys=False+내부 sorted, 시각/난수 없음) |
| git ref 입력 base_commit | 실제 커밋 해시 | ✅ `main...branch` → base=main 해시 |

### verdict 합성 정합 (TASK-001/002 와 일관)
`forbidden∪frozen → blocked(1)` > `out_of_scope∪protected → approval_required(2)` > `pass(0)`.
TASK-001 #1·TASK-002 의 종료코드 계약과 fail-closed(except→blocked) 설계를 동일하게 재사용.

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 게이트 1개(신규 476줄) + `handoff-log.md`(+1줄) + `summaries/2026-06-30.md`(+5줄). **Claude 소유 파일(`templates/`·`policies/`) 무수정.**
- 무관 리팩터/포맷/이름변경 없음. TASK-001/002 의 glob 매처·종료코드 계약·`normalize_path`·fail-closed 패턴을 일관 재사용. **scope-creep / over-reach 없음.**
- 결정성: 출력에 시각·난수 없음, 목록 `sorted`, generated_on 은 base 커밋의 commit date(%cs) 또는 override(`--generated-on`) — `Date.now` 류 비결정 없음. 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — TASK-004 fixture/MVP-1 에서 정합만)
1. **`*_touched` 리스트 항목 enrich**: frozen/protected/watched_touched 가 빈 문자열이 아닌 {path,zone,level,reason,(required_approval)} 레코드를 담음. 템플릿은 해당 항목 스키마를 빈 리스트로 두었고, 이 enrich 는 TASK-002 출력 계약(path+reason 보존)과 동일 — **최상위 키 추가 아님**. 사람 리뷰어 증거성↑. 수용.
2. **name-status 파일 단독 입력 시 base_commit="unknown"·라인 0**: git 컨텍스트가 없는 파일 입력 경로에서는 base_commit 을 알 수 없어 "unknown", `--numstat-input` 없으면 라인수 0. 생산 경로(git ref 입력)에서는 둘 다 정확. TASK-004 fixture 는 numstat 파일 동반 또는 ref 입력으로 작성하면 됨. 수용.
3. **generated_on 기본값**: 파일 입력+override 없음 → "1970-01-01" 플레이스홀더(결정성 우선). git ref 입력 시 base 커밋 날짜(%cs). 비결정적 "오늘 날짜" 미사용 — 게이트 결정성 원칙(TASKS §공통) 준수. 수용.
4. **미분류 level 조용히 무시**: TASK-002 #1 과 동일(zone level 이 block/approve/warn 어디에도 없으면 strength 0 → free 취급). 현 policy 무해. MVP-1 경고 고려. 수용.

→ 위 4건은 **차단 사유 아님**. TASK-004(테스트 fixtures/러너) 에서 #2(numstat 동반)·verdict 기대만 정합 유지하면 됨.

---

## TASK-004 테스트 fixtures + 러너 — 리뷰통과 (2026-07-01)

- 대상: commit `93e2c40`, 브랜치 `codex/2026-06-30-task004-tests`
- 파일: `tests/run-tests.sh`(신규 173줄)·`tests/cases.yaml`(신규)·`tests/fixtures/{good,out-of-scope,forbidden,frozen,protected,watched}/*`·`tests/fixtures/README.md`·`README.md`(실행절)
- 결정: **D-010 리뷰통과 + Claude 머지**

### 수용기준 4/4 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | 6 fixture (good/oos/forbidden/frozen/protected/watched) | ✅ | 6개 디렉터리 전부 존재. fixture↔policy 정합 확인(아래) |
| 2 | cases.yaml 에 gate·input·expect | ✅ | 6 케이스 각 `gate`/`input`/`expect` 선언, 게이트별 호출 분기 |
| 3 | run-tests.sh 일괄 실행 + PASS/FAIL 요약 | ✅ | `Summary: 6/6 PASS`, exit 0. 음성검증으로 FAIL 검출 확인 |
| 4 | 6개 전부 기대대로 | ✅ | `bash tests/run-tests.sh` → 6/6 PASS |

### fixture 진정성 (rigged 아님 — 정책이 실제로 그 판정을 내는지)
| 케이스 | 입력 경로 | 정책 근거 | 게이트 결과 |
|---|---|---|---|
| good | `app/features/search.py` | zones 미매칭=free, `app/features/**` allowed | evidence pass(0), zone_level=free·in_allowed_paths=true |
| out-of-scope | `docs/release-notes.md` | allowed=`app/features/**` 밖 | check-intent approval_required(2) |
| forbidden | `secrets/prod.key` | `secrets/**` forbidden | check-intent blocked(1) |
| frozen | `services/settlement/calculate.py` | `**/settlement/**`=frozen | sensitive blocked(1) |
| protected | `services/auth/login.py` | `**/auth/**`=protected, security-reviewer | sensitive approval_required(2) |
| watched | `lib/common/helpers.py` | `**/common/**`=watched | sensitive pass(0)+경고 |

### 음성 검증 (러너가 항상-PASS 가 아님)
- `cases.yaml` 의 frozen 기대를 pass/exit0 으로 변조 → `FAIL frozen (check-sensitive-zones)`, 사유 `verdict: expected 'pass', got 'blocked'` + `Summary: 5/6 PASS` + `EXIT=1`. 변조 후 원복 → 워킹트리 clean 확인.
- exit code: `sys.exit(main())` → python 종료코드가 bash 종료코드로 그대로 전파(CI 게이트로 사용 가능).

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 `tests/*`(신규 fixtures+러너+cases) + `tests/fixtures/README.md`(채움) + `README.md` 실행절 갱신 + 허용된 `handoff-log`·`summaries`. **Claude 소유 policy/templates 무수정.**
- `README.md` 실행절: "게이트 구현 후 채울 절" 플레이스홀더를 실제 시그니처(`--change-intent` 등)+`bash tests/run-tests.sh` 로 갱신 — TASK-004(러너 실행법) 직접 관련. 무관 리팩터/이름변경/포맷 노이즈 아님. **scope-creep / over-reach 없음.**
- 결정성: 러너가 `--generated-on 2026-06-30` 고정 주입 → evidence 생성 비결정 요소 제거. fixture 는 정적 텍스트(name-status/numstat). 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — MVP-1 고려)
1. **generate-change-evidence 케이스가 pass 경로만 1건**: good(pass) 만 evidence 게이트를 경유. blocked/approval_required 의 *evidence 합성*(verdict 우선순위·reviewer_required dedup)은 cases.yaml 에서 직접 검증 안 됨 — 단, 그 합성 로직은 TASK-003(D-009)에서 8종 시나리오로 이미 경험검증·머지됨. AC4("6개 케이스") 충족. MVP-1 에서 frozen/forbidden 을 evidence 게이트로도 거는 케이스 추가 권장.
2. **러너가 evidence 의 일부 키만 단언**: verdict·summary 3수치·changed_files 만 비교(reviewer_required·base_commit·전체 스키마는 미단언). 템플릿 키 일치는 TASK-003 에서 검증됨. AC 범위 내 — 수용.
3. **`set -u` 만(no `set -e`)**: 본체가 단일 python 호출이라 무해(python 종료코드가 곧 결과). 수용.

→ 위 3건은 **차단 사유 아님**. 모두 TASK-003 에서 이미 검증된 영역이거나 MVP-1 확장 대상.

---

## TASK-005 — `extract-python-inventory.py` 리뷰 (D-011, 2026-07-01)
대상: `1115a22`(impl `86c9a75`, `codex/2026-07-01-task005-function-inventory`). **MVP-1 Phase A 첫 게이트.** 결과 **리뷰통과 + Claude 머지(비민감)**.

### 수용기준 경험검증 (8/8 PASS + 픽스처 밖 독립검증)
| AC | 기준 | 검증 |
|---|---|---|
| 1 | 정규화 이름·라인범위·데코레이터 | `decorator.wrapper`·`outer.inner`·`Service.load`·`Service.Nested.method`·`decorated` 모두 정확. 픽스처 밖 fresh 입력(`functools.lru_cache`·`property`·`staticmethod`·메서드내 중첩 async)에서 `cached`/`A.x`/`A.x.helper`/`A.s` 정확 — rigged 아님 |
| 2 | async·메서드·중첩·데코레이터 함수 포함 | `async_function` 타입 부여, 중첩(`outer.inner`/`A.x.helper`)·메서드·데코정의(`decorator`)·피데코(`decorated`) 전부 캡처 |
| 3 | 파싱실패 fail-safe(예외없이 빈 인벤토리+오류표시) | `invalid.py` → 예외 없음, `items: []` + `parse_error` 채움, **exit 0** |
| 4 | 결정적 + `--json` | 2회 byte-identical, `sort_keys=True`, AST 전위순 방문 결정적 |

### 구현 정확성 메모
- **데코레이터 resolve**(`decorator_name`): `Name`→id, `Attribute`→`parent.attr` 재귀, `Call`→func, `Subscript`→value, fallback `ast.unparse`. `@functools.lru_cache(maxsize=None)` → `"functools.lru_cache"` 로 정확 추출(Call·Attribute 조합).
- **이름 정규화**: `InventoryVisitor.parents` 를 자식 방문 전 push/후 pop → 중첩 경로 정확. 클래스·함수·async 동일 경로 누적(`Service.Nested.method`).
- **end_line**: `getattr(node,"end_lineno",node.lineno)` — py3.8+ 정상, fallback 안전.

### 음성 검증 (러너가 항상-PASS 아님)
- `cases.yaml` 의 `Service.load` `start_line: 13`→`99` 변조 → `FAIL python-inventory` + `items` 불일치 사유 출력 + `Summary: 7/8 PASS` + `EXIT=1`. 원복 → 8/8 + 워킹트리 clean.

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 `.harness/gates/extract-python-inventory.py`(신규), `tests/fixtures/python-inventory/*`(신규), `tests/cases.yaml`(+2 케이스 **추가만**, 기존 6 무변경), `tests/run-tests.sh`(`extract-python-inventory` 분기 **추가만** — 기존 게이트 case_command/validate 무수정) + 허용된 `handoff-log`·`summaries`. **Claude 소유 policy/templates 무수정.**
- 무관 리팩터·이름변경·포맷 노이즈 없음. blast radius = 신규 게이트 1 + 러너 가산 분기. **scope-creep / over-reach 없음.**

### 비차단 관찰사항 (보정요청 아님 — Phase B/후속 고려)
1. **`parse_error` 메시지에 `column None` 가능**: 일부 `SyntaxError` 는 `offset=None` → `"... column None"`. 결정적·fail-safe 불변, 표시 문구만 미세. Phase B 에서 메시지 포맷 다듬을 때 정리 권장.
2. **파일 I/O 예외는 fail-safe 범위 밖**: AC3 의 fail-safe 는 *문법오류* 한정. 파일 없음/비-utf8 은 `open()`에서 예외(추출기 본연 책임 아님) — TASK-006/007 에서 git refs 입력으로 바뀌면 호출측이 처리. 수용.
3. **비-`.py`·바이너리 입력 미정의**: 본 태스크 입력 계약은 `.py` 파일. 파일단위 fallback(비-py 안전스킵)은 **TASK-007 AC3** 의 책임 — 여기 범위 아님. 수용.

→ 위 3건은 **차단 사유 아님**. 모두 후속 태스크(006/007/Phase B)의 책임 영역이거나 미세 표시 이슈. MVP-1 공통(D-004) "2층 자동차단 금지"는 본 게이트가 판정 자체를 안 내므로 무관.

#### ⚠️ 추가 관찰 (2026-07-01, 2차 적대적 리뷰 — 거버넌스 직접영향, TASK-006/007 가드 필수)
> 형 지적("다 통과시키는 것 아니냐")을 받고 2차로 적대적 검증(데코레이터·동명 함수)을 돌려 발견. **TASK-005 AC 위반은 아님**(추출은 정확) → 머지 유지. 단 후속 태스크가 이 출력을 그대로 쓰면 **민감 변경을 놓침** → 006/007 수용기준에 가드 추가(아래).
4. **데코레이터가 함수 라인범위 밖** (실증): `@requires_auth`(1)·`@app.route`(2) 위 `def transfer_funds`(3) → 인벤토리 `start_line=3`, 범위 `3-4`. AST 정의상 `node.lineno`=def 줄이라 데코레이터 줄 미포함. **위험**: 데코레이터만 수정(`@app.route` 메서드 추가, `@requires_auth` 추가/제거, `@gov` level 변경)하면 그 diff 헝크 줄이 함수 범위 밖 → **TASK-006(헝크∩함수범위) 에서 함수에 안 닿은 것으로 오판 → 가장 민감한 인증·라우팅·권한 데코레이터 변경을 `<module>` 로 흘려버림.** decorators 리스트로 캡처는 되지만 *라인 매핑*이 끊김. → **TASK-006 AC 보강**: 함수 라인범위 시작을 `decorator_list[0].lineno`(데코레이터 포함)로 잡거나, 데코레이터 줄을 해당 함수에 별도 매핑.
5. **정규화 이름 중복 가능** (실증): `@property def balance` 와 `@balance.setter def balance` → 둘 다 `Account.balance`(라인만 다름). 오버로드(`@overload`)·조건부 재정의(if/else)·setter 동일. **위험**: TASK-007(before/after **이름 키 매칭**)에서 동명 함수가 모호 매칭 → added/deleted/modified 오판. → **TASK-007 AC 보강**: 매칭 키를 이름 단독이 아니라 `(정규화이름, 데코레이터셋 또는 라인순서)` 로. 이름 단독 매칭 금지.

→ #4·#5 는 **TASK-005 차단 사유는 아니나**(추출 정확·AC 충족), 하네스 핵심 목적(민감 변경 포착)에 직결 → TASK-006/007 진행 전 **수용기준에 반영**(TASKS.md 갱신). 1차 리뷰에서 누락했던 항목 — 2차 적대 리뷰로 보강.

---

## TASK-006 `map-diff-to-functions` 리뷰 (2026-07-01, D-012 / commit e5b4c2d·impl 32ac41c)

> 심층·적대적 리뷰(CLAUDE.md §2B). 핵심 검증축: **D-011 #4 가 신설한 AC5(데코레이터 줄 포함)가 실제 헝크매핑에서 막히는가** — fresh 입력으로 직접 깨보려 시도.

### 한 줄씩 읽은 핵심 로직
- **헝크 파싱**(`parse_diff_hunks`): `diff --git ... b/<path>` 로 current_path 확정 → `@@ -a,b +c,d @@` 정규식. `new_count` 생략 시 1 기본(`or "1"`). `changed_lines = range(new_start, new_start+new_count)`. **삭제 헝크**(new_count=0)는 `anchor_lines = [new_start-1, new_start]`(>0) 폴백으로 인접 라인에 앵커.
- **매핑 범위**(`mapping_start_line`): 데코레이터 있으면 `min(decorator.lineno)`, 없으면 `node.lineno`. → 인벤토리의 `start_line`(=def 줄)과 별도로 `decorator_start_line` 을 둬서 **매핑은 데코레이터 첫 줄부터** 시작. = D-011 #4 보정의 정확한 실현.
- **교집합**(`line_touches_item`): `decorator_start_line <= line <= end_line`. 헝크 anchor_lines 중 하나라도 함수범위에 들면 touched. 없으면 `<module>`.
- **fallback 분기**: 비-`.py` or status `D` → head 파싱 시도하지 않고(크래시 회피) 모든 헝크·파일 touched=`<module>`.
- **dedup**(`unique_functions`): `(name,type,start,end,decorator_start)` 키 — 동명이라도 라인범위 다르면 별도 유지(getter/setter 구분 보존), 같은 함수 여러 헝크는 1회로.

### 적대적 검증 (픽스처 밖 fresh repo — rigged 차단)
fresh git repo 에 ① **멀티라인 데코레이터** `@functools.lru_cache`+`@requires_auth("user"→"admin")` 위 `def secure` ② `@property`/`@val.setter` 동명 `C.val` ③ if/else 조건부 동명 `def conditional` 구성 후 **각각 한 줄만** 변경:
- **데코레이터 인자만 변경(라인6)** → `secure`(decorator_start 4, def 9, end 10) 에 매핑. **`<module>` 로 새지 않음.** ✅ AC5 실증 — 인증/라우팅/권한 데코레이터만 바꿔도 함수에 잡힘(거버넌스 핵심).
- **setter 본문만 변경(라인20)** → getter(13-16) 제외, setter `C.val`(18-20) + 둘러싼 class `C` 에만 매핑. 동명 함수 라인범위로 정확 분리. ✅
- **else-branch def 본문만 변경(라인28)** → else쪽 `conditional`(27-28)에만 매핑(if쪽 24-25 제외). ✅
- **결정성**: 동일 입력 2회 → md5 byte-identical. ✅
- **fail-safe**(별도 fresh repo): 비-py(`conf.yaml`)→`unsupported`+`<module>`, 삭제파일(D)→`<module>`(head show 안 함, 예외 없음), **head 문법오류→`parse_error`+`<module>`+exit 0**, 신규파일(A)→정상 매핑. ✅
- **음성 검증**: `cases.yaml` 의 기대 `secure_view`→`WRONG_NAME` 변조 → `FAIL function-mapping` + `Summary: 8/9` + 러너 exit 1. 원복 9/9. → 러너가 항상-PASS 아님. ✅

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 `.harness/gates/map-diff-to-functions.py`(신규 315), `tests/fixtures/function-mapping/{base,head}/*`(신규), `tests/cases.yaml`(+1 **추가만**, 기존 8 무변경), `tests/run-tests.sh`(임시-repo 준비 함수 + 검증 분기 **추가만** — 기존 게이트 호출/검증 무수정) + 허용된 `handoff-log`·`summaries`. **Claude 소유 policy/docs/templates 무수정.**
- 무관 리팩터·이름변경·포맷 노이즈 없음. blast radius = 신규 게이트 1 + 러너 가산 분기 + fixture. **scope-creep / over-reach 없음.**

### 비차단 관찰 + 차기 AC 가드
1. **🔴→차기 AC 가드: 하드 에러 시 exit 0 + `error`+`files:[]`** — 잘못된 git ref/git 실패가 `main()` 의 top-level except 로 잡혀 exit 0 + `error` 필드로 보고됨. Phase A 설계상 판정을 안 하므로(TASK-007 AC4: 종료코드 보고용) **이 게이트 자체 결함은 아님**(에러를 정직히 노출). 그러나 후속 통합 **TASK-012** 가 `files` 만 보고 `error`/`parse_error` 를 무시하면 git 실패가 *clean diff(함수 변경 0)* 로 읽혀 **fail-open** — 거버넌스 직접 구멍. → **비차단으로 흘리지 않고 TASK-012 AC 에 명시 가드 신설**(아래 TASKS.md): `error`/`parse_error` 존재 → fail-closed(approval_required/blocked), "함수 변경 없음" 으로 간주 금지.
2. **순수 리네임(내용 무변경)** → 헝크 0 → 파일 `touched_functions: []`(빈 리스트). 비-py/삭제 파일이 `[<module>]` 을 강제하는 것과 미세 비일관. **거버넌스 구멍 아님**(실제 변경 라인 0). TASK-007/012 에서 파일 status(R) 별도 처리 권장 — 비차단.
3. **삭제 헝크 anchor 폴백**(`[new_start-1, new_start]`) 은 모듈레벨 삭제를 인접 함수에 **과대 귀속**할 수 있음 → 거버넌스상 **안전 방향(더 플래그)**. 삭제 함수의 added/deleted 분류는 TASK-007 책임 — 비차단.

→ #1 만 거버넌스 직접영향 → **TASK-012 AC 가드로 전환**(명시). #2·#3 은 후속 책임/안전방향 → 비차단. 본 태스크 AC 5/5 충족·논리 정합 → **머지 유지**.
