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

## TASK-007 `classify-python-function-changes` 리뷰 — **보정요청** (2026-07-02, D-013 / impl 0502589)

> 심층·적대적 리뷰(CLAUDE.md §2B). 핵심 검증축: **🔴 AC5 동명 매칭 가드**(D-011 #5 가 신설) + 고정 적대 세트(데코레이터·동명 오버로드·조건부 def) + TASK-006 리뷰 #2 가 예고한 **status R 처리**.

### 한 줄씩 읽은 핵심 로직
- **매칭 키**(`assign_occurrence_keys`): `(정규화이름, sorted 데코레이터셋, 같은 (이름,데코셋) 그룹 내 등장순서)`. AC5 요구( 이름 단독 금지, `(이름,데코셋/라인순서)` )를 **둘 다 결합**해 충족 — property/setter 는 데코셋으로, `@overload` 다중·조건부 재정의는 순서로 분리.
- **데코레이터 resolve**(`decorator_name`): Name/Attribute/Call/Subscript 재귀 — `@requires_auth("user")`와 `("admin")` 이 같은 키 `requires_auth` 로 유지되어 **매칭은 성립**하고, 인자 차이는 `signature_dump`(전체 `ast.dump`) 가 잡아 `signature_changed=True`. 매칭키(느슨)/변경감지(엄밀) 분리가 정확한 설계.
- **시그니처 vs 본문**(AC2): 함수 = `(args, decorator_list dump, returns, type_comment)`, 클래스 = `(bases, keywords, decorators)` / 본문 = `body` dump. `include_attributes=False` 로 라인번호 이동은 무시(순수 위치이동 ≠ modified). 올바름.
- **분류**(`classify_inventory_changes`): before−after 키차 = deleted, after−before = added, 교집합 중 dump 다름 = modified. 출력 정렬 고정 + `sort_keys=True` → 결정적.
- **fallback**(AC3): 비-`.py` / status A·D / before·after parse_error → 파일 단위 `file_fallback` 레코드 + 사유 표시. `_match_key` 등 내부 필드는 `public_item` 으로 출력에서 차단(깔끔).
- **러너**: `prepare_function_mapping_fixture` 공유 헬퍼에 "head 반영 전 work_dir 클리어 + `add -u`" 추가 — 진짜 파일삭제(D) fixture 를 위해 필요. **기존 TASK-006 케이스에 영향 없음을 10/10 PASS 로 확인.**

### 적대적 검증 (픽스처 밖 fresh repo ×3 — rigged 차단)
- **① 데코레이터 인자만 변경** `@requires_auth("user"→"admin")` → `transfer` **modified `signature_changed=True`**. ✅ 권한 상향이 함수 단위로 잡힘(거버넌스 핵심).
- **② `@overload` 동명 3연속**(overload×2+구현): 2번째 overload 의 타입만 변경 → 해당 occurrence 만 modified(sig=True), 구현·1번째는 무변경으로 침묵. ✅
- **③ 조건부 동명 def**(if/else 각각 `handler`): if쪽만 변경 → modified 1건만. ✅
- **④ property/setter**(픽스처): setter 본문만 변경 → `Account.balance` modified 1건(setter)만 + 둘러싼 class modified. getter 오판 없음. ✅
- **⑤ 결정성**: 2회 실행 md5 byte-identical. ✅
- **⑥ 음성 검증**: `cases.yaml` 의 `signature_change` 기대 `signature_changed: true→false` 변조 → `FAIL function-classification` + `Summary: 9/10` + 러너 exit 1, 원복 10/10. ✅ 항상-PASS 아님.
- **⑦ 불량 ref** → exit 0 + `error`+`files:[]` (TASK-006 과 동일 Phase A 설계, TASK-012 fail-closed 가드 대상). ✅
- **⑧ 🔴 리네임(R)** — **깨짐. 아래 R-1.**

### 🔴 R-1 (보정요청 사유): 리네임 1건 → 전체 리포트 소실 + 환경 의존
fresh repo: `payments.py`→`settlement.py` 리네임+수정(`* 1.0`→`* 0.99` — 정산 로직!) + 무관한 `other.py` M 수정(`charge_fee` 도입). `git diff --name-status` = `M other.py` + `R066 payments.py settlement.py`.
→ 게이트 출력: **`{"error": "fatal: path 'settlement.py' exists on disk, but not in '<base>'", "files": []}`** — R 레코드가 새 경로만 남긴 채 `git show base:<새경로>` 를 시도해 top-level 예외 → **`other.py` 의 분류까지 통째 소실**.
- AC1·AC2 위반(분석 가능한 형제 M 파일 미보고), AC3 취지 위반(파일 단위 안전 스킵이 아닌 전역 붕괴), **AC4 결정성 위반**(`diff.renames` host config 에 따라 같은 입력이 정상(A+D fallback)/전체 error 로 갈림 — git 2.9+ 기본 on 이라 대부분 환경에서 발병).
- fail-open 은 아님(top-level `error` 는 TASK-012 가드로 fail-closed) — 그러나 리네임은 흔한 입력이라 매번 감사카드가 빈손 = 게이트 목적 무력화. TASK-006 리뷰 #2 에서 "TASK-007 에서 R 별도 처리 권장" 예고까지 있었음. → **비차단으로 흘리지 않고 보정요청**(`collab/answers/A-0001.md`): `--no-renames` 명시 또는 R/C 파일 단위 fallback + 형제 파일 보존 + 회귀 픽스처.

### 비차단 관찰
1. **모듈레벨 변경 비가시**: `ADMIN_ROLE = "user"→"admin"` 만 바뀐 파일 → `function_changes: []` (fallback 아님·표식 없음). 함수 분류기의 설계상 범위 밖이고 TASK-006 이 `<module>` 매핑으로 잡는 구조 — 단 **TASK-012 가 TASK-007 출력 단독으로 "함수변경 0 = clean" 으로 읽으면 fail-open** → 거버넌스 직접영향이므로 비차단으로 흘리지 않고 **TASK-012 AC 가드 보강**(TASKS.md): 함수분류 단독 판정 금지, TASK-006 `<module>` 매핑과 병합 필수 + `fallback:true` 파일은 함수 불가시니 보수 취급.
2. **데코레이터 전면 교체**(`@public`→`@requires_admin`) → 매칭키가 달라져 modified 아닌 **deleted+added 쌍**으로 보고. 가시성 유지(added 에 새 데코레이터 노출) → fail-open 아님. TASK-009 는 added 함수도 modified 와 동일 강도로 판정하면 자연 해소 — 관찰만.
3. **동명 중복 첫 정의 삭제 시 귀속 모호**(occurrence-shift): before `dup#0(v1)`+`dup#1(v2)` → after `dup(v2)` 만 남으면 "`#1` deleted + `#0` modified" 로 귀속(실제는 #0 삭제·#1 생존). 위치 매칭의 본질적 모호성 — **변경 사실 자체는 절대 안 놓침(보수 방향)**. 관찰만.
4. **`type_comment`**: `ast.parse` 가 `type_comments=True` 없이 호출되어 항상 None — signature_dump 의 dead field. 무해. 관찰만.
5. **three-dot(`a...b`) 입력** → `split("..")` 이 `.b` 를 만들어 error(fail-closed). usage 안내 개선 여지 — 관찰만.

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 `.harness/gates/classify-python-function-changes.py`(신규 363) + `tests/*`(케이스·fixture·러너 분기 **추가만**, 공유 헬퍼 수정은 D-fixture 에 필요·기존 케이스 green) + Codex 소유 README 2곳(+3줄 목록/사용법) + 허용된 `handoff-log`·`summaries`. **Claude 소유 policy/docs/templates 무수정.**
- 무관 리팩터·포맷 노이즈 없음. **scope-creep / over-reach 없음.**

### 판정
AC2·AC5(🔴)·결정성·fallback·음성검증 모두 실증 통과 — 구현 품질은 높다. 그러나 **R-1 이 AC1/AC3/AC4 를 흔한 입력(리네임)에서 위반**하고 형제 파일 증거까지 소실시키므로 "능동적으로 깨보려 했더니 깨졌다" = **보정요청, 머지 보류**. 국소 수정(+회귀 픽스처) 후 재제출 시 신속 재리뷰.

---

## TASK-007 재리뷰 — **리뷰통과** (2026-07-02, D-014 / impl 2243173, 브랜치 codex/2026-07-02-task007-rename-fix)

> A-0001(R-1) 보정 재제출 심층·적대적 재리뷰. Codex 는 "같은 브랜치에 커밋 추가" 대신 **최신 main(e673412) 기준 새 브랜치로 재제출** — 리뷰 기록이 이미 main 에 머지된 상태라 rebase 성격의 합리적 이탈로 **수용**. 대신 이전 리뷰본(0502589)과의 **전체 트리 diff 로 델타 동일성을 검증**했다(아래).

### 이전 리뷰본(0502589) 대비 델타 검증
`git diff <구 브랜치>..<신 브랜치>` — 게이트 본체 **+7줄**(① `git diff --name-status --no-renames` 명시, ② R/C status → `fallback_reason: "renamed_or_copied"` 파일 단위 fallback 분기), cases.yaml 기대값 +33줄, 회귀 픽스처 4파일(`renamed_source.py`→`renamed_target.py` 쌍 + 동반 M `companion.py`), summaries/handoff. **그 외 게이트·러너·기존 픽스처는 D-013 에서 실증 검증한 코드와 byte-identical** → A-0001 요구에 정확히 국소, scope-creep 없음.

### 코드 정독 (델타)
- `--no-renames`(L310): git 이 R/C 를 아예 안 만들므로 host `diff.renames` config 의존 제거 — R-1 의 근본 원인(환경 의존 + 새 경로로 `git show base:` 시도) 제거. A-0001 요구 1의 1안 채택.
- R/C fallback 분기(L273-274): `--no-renames` 하에선 도달 불가한 **방어 코드**. 이제 `parse_name_status` 의 "R/C 는 새 경로 보존"(L44-45)과 정합 — R 레코드가 들어와도 `git show` 를 시도하지 않고 새 경로를 파일 단위 fallback 표시. A-0001 요구 1의 2안까지 이중 방어. 정합성 OK.

### 적대적 재검증 (전부 실증)
- **① R-1 재현→수정 확인 (fresh repo, 픽스처 밖)**: `payments.py`→`settlement.py` `git mv`+수정(R091) + 형제 `other.py` M(`charge_fee_stub` 도입). **구 게이트(0502589)**: `error: fatal: path 'settlement.py' ...` + `files: []` — 붕괴 재현. **신 게이트**: 전역 error 없음, `other.py` → `charge_fee_stub added`·`helper modified` **형제 분류 보존**, 리네임 쌍은 D/A `file_added_or_deleted` fallback. ✅ A-0001 요구 2 충족.
- **② 환경 의존성 제거**: 같은 fresh repo 에서 `diff.renames=true` vs `false` 출력 **md5 동일**. + 2회 실행 md5 동일(AC4 결정성). ✅
- **③ 스위트**: `bash tests/run-tests.sh` → **10/10 PASS, exit 0** (기존 9케이스 무영향).
- **④ 음성 검증**: cases.yaml 의 `companion` 기대 `signature_changed: false→true` 변조 → `FAIL function-classification`·9/10·exit 1, 원복 후 10/10. ✅ 항상-PASS 아님.
- **⑤ 고정 적대 세트 재실행 (CLAUDE.md §2B 상설 — fresh repo)**: `@requires_auth("user"→"admin")` 데코레이터 인자만 변경 → `secure modified signature_changed=True`(🔴 핵심), property/setter → 변경된 getter 만 modified, `@overload`×3 → 2번째 overload 시그니처 변경만 포착, if/else 조건부 동명 `dup` → 변경된 쪽만 modified. **전부 정확.** ✅
- **⑥ 비-ASCII 파일명 `.py`**(`정산.py` M): git `core.quotePath` 인용 경로가 `.py` suffix 매치 실패 → `unsupported_language` **파일 단위 fallback**(전역 붕괴 없음, 형제 `ok.py` 분류 보존). 보수 방향 — 관찰 #7.

### 🔍 재리뷰 발견 (신규 2건 — 비차단, TASK-013 AC 가드로 명시적 차단)
- **#6 회귀 픽스처 무력(vacuous)**: 픽스처 리네임 쌍(2줄, 내용 1자 수정)은 파일이 너무 작아 **git 유사도 휴리스틱에 안 걸림** — `diff.renames=true`·`-M` 에서도 R 아닌 D+A 로 나옴(실증). 그 결과 **① 구 게이트(0502589)도 이 픽스처를 통과**(error 없음·8파일)하고, **② 신 게이트에서 `--no-renames` 를 제거해도 스위트 10/10 PASS**(실증) = 픽스처가 자신이 막아야 할 회귀를 못 잡는다. 단, A-0001 요구 3의 **문면**("base→head 파일명 변경으로 충분, A+D 기대값")은 충족 — 내 요구서가 유사도 감지 조건을 명시하지 못한 탓이 크므로 보정 재요청이 아닌 **TASK-013 AC 가드**로 강화: **순수 리네임(내용 동일) 쌍**은 크기 무관 exact-match 로 **항상 R100 감지됨을 실증**했으므로 이를 추가하면 `--no-renames` 제거 시 스위트가 확실히 FAIL 한다.
- **#7 비-UTF8 소스 → 전역 붕괴 (R-1 동류)**: `# -*- coding: latin-1 -*-` 등 UTF-8 디코드 불가 `.py` M 파일 1건 → `run_git`(text=True) 의 `UnicodeDecodeError` → top-level except → **`error`+`files:[]` — 형제 M 파일 분류 소실**(실증). R-1 과 같은 "파일 1건 → 전역 붕괴" 클래스. **비차단 사유**: ⓐ PEP 3120 이후 비-UTF8 소스는 희귀(리네임과 빈도 차원이 다름), ⓑ top-level `error` 는 TASK-012 fail-closed 가드로 pass 로 안 흘러감(fail-open 아님), ⓒ A-0001 범위 밖 신규 발견. 단 거버넌스 시야 상실이므로 비차단으로 흘리지 않고 **TASK-013 AC 가드**: 게이트는 파일별 예외를 해당 파일 fallback 으로 격리(형제 보존)하고 픽스처로 고정.
- **#8 (관찰만)** 비-ASCII 파일명은 인용 경로 그대로 보고돼 경로 표기가 mangled(`"\354..."`) — 파일 단위 fallback 으로 보수 처리되므로 무해하나, 차후 `-c core.quotePath=false` 고려.

### 보수적 개발 평가축 (COMMON-RULES §1)
델타가 A-0001 요구 1·2·3에 정확히 국소(+7줄 게이트, 픽스처 4파일, 기대값). Claude 소유 무수정, 무관 리팩터·포맷 노이즈 없음. **scope-creep / over-reach 없음.** 새 브랜치 재제출은 최신 main 반영 목적으로 합리적(델타 동일성 검증으로 리스크 상쇄).

### 판정
R-1 수정을 **구 게이트 붕괴 재현 → 신 게이트 형제 보존 + 환경 무관(md5 동일)** 으로 실증했고, 고정 적대 세트·음성검증·결정성 전부 통과. 신규 발견 #6·#7 은 "민감 변경 포착에 직접 구멍인가" 질문 적용 결과 **현행 동작은 정확·보수 방향(fail-closed)** 이므로 비차단 — 단 흘리지 않고 **TASK-013 AC 가드 2건으로 명시적 차단**(TASKS.md). = **리뷰통과 (D-014), 비민감(분석 전용 게이트·테스트 하네스) → Claude 머지.**

---

## TASK-013 리뷰 (2026-07-02) — 분류 회귀 가드 · **보정요청**(map 격리 미달) · 머지 보류
대상: `codex/2026-07-02-task013-classification-regressions` / impl `fb7a098`(헤드 `824502d`). D-014 신설 AC 가드 2건(pure-rename 회귀 픽스처 + 파일 단위 오류 격리) 구현. 판정 상세는 `collab/answers/A-0002.md`, `collab/decisions.md` D-015.

### 적대적 검증 (전부 브랜치 게이트 직접 실행)
- **스위트 10/10 PASS**·exit 0 (워크트리 실측).
- **NV1 — AC 가드 #1 실효성**: `pure_rename_source↔target` 내용 byte-identical(`def renamed_only`) 확인. classify 게이트에서 `--no-renames` 제거 → 이 쌍이 `R100` 단일 레코드(`pure_rename_target`)로 붕괴(source 소멸), host `diff.renames` unset=git 기본 on → **스위트 9/10 FAIL**. 동시에 구 `renamed_source→target` 픽스처는 --no-renames 제거해도 D+A 유지(=git 유사도 감지 안 걸림) → **새 pure-rename 픽스처만이 실효 회귀 가드**임 실증(D-014 발견 #1 확인).
- **NV3 — 픽스처 밖 fresh 비-UTF8 형제 보존**: fresh repo(`sibling.py` 정상 M `transfer` 본문 수정 + `bad.py` latin-1 `0xe9` M):
  - classify **구 게이트(main)** = `error`+`files:[]` **전역 붕괴 재현**(`'utf-8' codec can't decode byte 0xe9`).
  - classify **신 게이트(브랜치)** = `sibling transfer:modified` 보존 + `bad fallback:unreadable`, 전역 error 없음(`files=2`). → **classify 격리 유효**.
  - map **신 게이트(브랜치)** = `error`+`files:[]` **여전히 붕괴**(`files=0`) — 구 게이트와 동일. ⚠️ 결함.

### 🔴 결함 (R-1, 보정요청 사유) — map 게이트 비-UTF8 격리 미달
- 근원: `map-diff-to-functions.py:238` `parse_diff_hunks(run_git(["diff","--unified=0",rev_range]))` — 전범위 unified 패치에 `bad.py` 의 `0xe9` 가 섞여 `run_git`(text=True strict) 이 **per-file 루프 진입 전** `UnicodeDecodeError` → `main()` top-level except → 전역 붕괴. 브랜치가 감싼 `:260` `source_at_ref(head,...)` 는 도달조차 못 함 = **死코드**(M 파일 디코드 실패엔 무력).
- **근원 확정 실증**: `:238` 읽기만 `errors="surrogateescape"` 로 바꾼 사본 재실행 → 붕괴 해소, `sibling→transfer` 보존 + `bad→parse_error`+`<module>`(`:260` wrap 이 그제야 파일 단위 격리) = `files=2`. → 결함이 `:238` 임 확정, 수정 방향도 확인.
- 왜 비차단 아님(§2B 필수 질문): 단일 비-UTF8 `.py` 1건이 map 리포트 전체 소실 → 형제 파일(인증/정산 함수 포함 가능) 함수 매핑 전량 유실 = D-013 R-1 동류 = **거버넌스 직접 구멍**.
- 왜 스위트가 못 잡았나: `function-mapping` 픽스처는 `sample.py`(UTF-8) 하나뿐 → **map 가드 미실행**(비-UTF8 케이스는 `function-classification` 픽스처에만 존재). 10/10 은 map 가드 위양성.

### 요구 수정(최소, A-0002)
1. `:238`(필요 시 `:237`) 전범위 diff 읽기 바이트-관용화(surrogateescape/replace) **또는** 파일 단위 `diff -- <path>`+파일별 try/except → 형제 매핑 보존·실패 파일만 `<module>` 격리.
2. `function-mapping` 픽스처에 비-UTF8+동반 정상 M 회귀 케이스 추가 + "격리 제거→FAIL" 음성검증.

### 비차단 관찰 (수정 불요)
- classify 신규 try/except 가 `Exception` 광범위 포착 → git 일시 실패(RuntimeError)도 `unreadable` fallback 흡수. 격리·보수 방향(fallback=민감 취급)이라 거버넌스 약화 아님 → OK.
- (참고, 강제 아님) classify/map 의 소스 읽기 격리를 **공유 헬퍼**로 통일하면 위치 불일치 재발 방지. MVP 범위 밖.

### 보수적 개발 평가축 (COMMON-RULES §1)
델타는 AC 가드 요구에 국소(게이트 각 +몇 줄, 픽스처 4파일, cases.yaml 기대값). Claude 소유 무수정, 무관 리팩터·포맷 노이즈 없음. scope-creep/over-reach 없음. — 품질 자체는 양호하나 **map 한 곳 국소 결함**으로 반려.

### 판정
classify 측(수정·pure-rename 회귀 가드·비-UTF8 격리)은 실증 통과. **map 게이트가 AC 가드 #2("classify·map 공통 격리")를 미달**하고 이는 거버넌스 직접 구멍이라 비차단 불가 → **보정요청(A-0002), 머지 보류.** 국소 수정이라 재제출 시 신속 재리뷰.

## TASK-013 재리뷰 — **리뷰통과** (2026-07-04, D-016 / impl 0aaadcc, 브랜치 codex/2026-07-04-task013-map-nonutf8-fix)

**대상**: D-015/A-0002 보정 재제출 — 새 브랜치(main `fbc2490` 기준, 헤드 `bfbc1e8`). 대상 커밋 `0aaadcc` + 인계 `bfbc1e8`.

### 재제출 형식 · 델타 검증 (구 리뷰본 824502d 대비 직접 diff)
- **map**: A-0002 요구 그대로 — `:238`(신 `:240`) `git diff --unified=0` 읽기를 `run_git(..., errors="surrogateescape")` 로 바이트-관용화(파라미터화, 기본은 strict 유지). 구 브랜치의 死코드 wrap(`:260` source 실패 시 수동 `<module>` 조립)은 제거하고 `extract_inventory(source_at_ref(...))` 전체를 try 로 감싸 실패 시 빈 인벤토리+`parse_error:"unreadable source: ..."` — 이후 기존 `touched_functions()` 가 헝크당 `<module>` 반환(코드 단순화, 동작 동등 이상).
- **classify**: `extract_inventory` 를 try 안으로 이동 + except 를 `(RuntimeError, UnicodeDecodeError, UnicodeEncodeError)` 로 협소화(기능 동등). `run_git` 은 stdout strict / stderr replace 디코드로 분리.
- **픽스처**: 구 `unreadable.py` → `non_utf8.py` 개명(classification), **function-mapping 에 `non_utf8.py`(0xe9 실바이트, xxd 확인) + `sibling.py` 신설** — A-0002 요구 ② 충족. `pure_rename_source/target` 은 base/head **blob 동일(`f7a18b4`) = byte-identical → R100 항상 감지**.
- 델타는 A-0002 요구에 정확히 국소. Codex 소유 파일만 수정 — scope-creep/over-reach 없음.

### 실증 (워크트리 직접 실행, 픽스처 밖 fresh 포함)
1. **스위트**: 10/10 PASS·exit 0. 실패 시 exit 1 확인(변조 상태에서 무파이프 실행).
2. **음성검증 5종** (각각 원복 후 10/10 재확인):
   - NEG-1 map 기대값 변조(`transfer`→`transfer_x`) → 9/10 FAIL — 항상-PASS 아님.
   - NEG-2 `surrogateescape` 제거 → function-mapping FAIL — **A-0002 요구 "격리 제거→FAIL" 성립**.
   - NEG-3 classify `--no-renames` 제거 → function-classification FAIL — **AC 가드#1(pure-rename) 실효**.
   - NEG-4 classify 격리 except 무력화 → function-classification FAIL.
   - NEG-5 map 격리 except 무력화 → function-mapping FAIL — **map 픽스처가 surrogateescape 층과 파일별 격리 층 양쪽을 모두 가드**.
3. **fresh 독립검증** (`sibling.py` 정상 M + `bad.py` latin-1 0xe9 M): 구 게이트(main) `error`+`files=0` 붕괴 재현 ↔ 신 map `files=2`·`sibling→transfer` 보존·`bad→<module>`+`parse_error:unreadable source` / 신 classify `sibling transfer:modified` 보존·`bad→fallback:unreadable`. **R-1 해소.**
4. **적대 입력 추가** (§2B):
   - **NUL 바이트 `.py`**(+정상 형제 M): host Python 3.11.4 에서 `ast.parse` → `SyntaxError` → `parse_error` 격리, 전역 붕괴 없음, 형제 보존(양 게이트). 단 map 은 git 이 바이너리 취급해 헝크 없음 → `touched_functions:[]` (관찰 #1).
   - **base 쪽만 비-UTF8**(head 는 정상 UTF-8): map — 삭제 라인의 0xe9 를 surrogateescape 로 통과, head 기준 `pay` 정확 매핑. classify — before unreadable → 보수 폴백(방향 안전).
   - **비-ASCII 파일명**: APFS 가 비-UTF8 파일명 생성 자체를 거부 — 이 호스트에서 재현 불가(관찰 #3).
5. **결정성**: 두 입력 각각 반복 실행 md5 동일.

### 비차단 관찰 3건 (비차단 판정 전 필수 질문 적용 — 직접 구멍 아님 근거 포함)
1. **map: `parse_error` + 헝크 부재 → `touched_functions:[]`** (NUL 실증): `<module>` 도 아닌 빈 리스트라, 하류가 "touched 없음 = clean" 으로 읽으면 fail-open. **단 TASK-012 AC 가드(D-012 #1)가 파일별 `parse_error` fail-closed 를 이미 강제 → 구멍 아님.** 이번 커밋에서 해당 AC 문구에 "빈 `touched_functions` ≠ clean" 을 명시 보강(TASKS.md).
2. **격리 except 에 `ValueError` 미포함**: Python ≤3.10 은 NUL 바이트가 `ValueError` 로 떨어져 전역 붕괴 가능. 호스트 3.11.4 는 `SyntaxError` 로 안전함을 실증 — 게이트 실행 환경이 이 호스트로 고정돼 있어 현행 구멍 아님. 차기 강건화 시 튜플에 `ValueError` 추가 권고(보정요청 사안 아님).
3. **비-UTF8 파일명 경로**: git `core.quotepath` 인용 경로는 `git show` 실패 → `RuntimeError` → 보수 폴백으로 흡수될 구조이나 이 호스트(APFS)에선 입력 자체 생성 불가로 미실증. 기록만.

### 머지 판정 (D-007)
분석 전용 게이트(보고용 exit 0)·테스트 픽스처·러너 — 정산·인증/인가·암호화·DB migration·infra 미접촉 → **비민감**(TASK-005/006/007 동일 범주). 구현자(Codex)≠머지자(Claude) → **Claude 가 main 머지·push.** MVP-1 Phase A 회귀 가드(TASK-013) 완결.

## TASK-008 설계질문(Q-0001) 인계 리뷰 — **통과·머지 + 설계답변** (2026-07-04, D-017 / 브랜치 codex/2026-07-04-task008-design-question, 5ea0b79·775e145)

**성격**: 코드 없는 문서 인계(blocking 질문). 적대적 검증 대상이 게이트 코드가 아니므로 이번 리뷰의 실증 축은 ① 주장 검증 ② 보수성 ③ 질문의 완전성(설계에 필요한 결정이 빠졌는가) ④ 하류 영향.

**검증한 것**
1. **보수성**: `git diff origin/main...브랜치` = 3파일 41줄 전부 추가(Q-0001·handoff 1줄·summary 1절). 구현 코드·픽스처·Claude 소유 파일 무접촉. `collab/questions/` 는 COMMON-RULES §1 이 명시한 질문 경로(신설 디렉토리 아님 — README 기존재). scope-creep 없음.
2. **주장 실증**: 인계문 "tests green" → 스위트 직접 실행 10/10 PASS·exit 0. Q-0001 의 TASKS.md 인용(`:95` 한 줄 정의) 원문 대조 일치. 커밋 2건(§3 상세 형식 — 왜/무엇/영향/관련) 준수.
3. **질문 완전성(적대적 관점)**: 7항(문법·필드·값/심각도·scope·검증실패·스키마·테스트 AC)이 파서 계약의 결정 지점을 커버. **질문이 놓친 설계 구멍 1건을 리뷰에서 발견** — *주석 제거 우회*(같은 PR 에서 `@gov(frozen)` 삭제+본문 수정 → head 만 보면 무주석 = 게이트 무력). 질문 범위(파서) 밖이지만 §2B 필수 질문("거버넌스 목적에 직접 구멍?") → **그렇다** → 비차단으로 흘리지 않고 **TASK-009 AC 가드로 명문화**(base ∪ head max 판정, A-0003 §하류 가드·TASKS.md).
4. **역할 경계**: Codex 가 정책 의미(레벨 어휘·차단 의미·scope 규칙)를 임의 구현하지 않고 차단 질문으로 멈춤 — CLAUDE.md 상호견제 구도의 모범 동작. 기록해 둘 선례.

**설계 답변**: `collab/answers/A-0003.md` (계약 전문). 핵심 결정과 근거 — 데코레이터+`__gov__` 리터럴만(AST 결정성·TASK-005 데코 추출/TASK-006 AC5 데코줄 매핑 인프라 재사용, 주석 마커는 부착 모호로 거부) / 엄격 승계 stricter-wins(레벨 하향 우회 차단) / invalid→protected 보수 기본(silent pass 금지) / 별도 게이트(TASK-005 출력은 TASK-006/007 하류 계약이라 스키마 동결) / 고정 적대 세트(setter-만-주석·overload·조건부 def)를 상설 픽스처로 요구.

**층 분류 결정(D-017)**: `@gov` = 선언적 1층 → TASK-009 frozen 차단은 D-004 와 모순 없음. 근거·override 여지는 D-017 참조.

**머지(D-007)**: 협업 문서 전용 — 비민감 → Claude 머지. 비차단 관찰: Q-0001 이 영어로 작성됨(규칙 위반 아님 — 기록만).
