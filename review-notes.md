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

## TASK-008 `@gov` 주석 추출 게이트 구현 리뷰 — **보정요청** (2026-07-04, D-018 / 브랜치 codex/2026-07-04-task008-gov-annotations, 787a47d·2fa3635)

**대상**: `.harness/gates/extract-gov-annotations.py`(381줄 신규) + `tests/fixtures/gov-annotations/`(valid/module/invalid) + `tests/cases.yaml`·`run-tests.sh` 확장. A-0003(D-017) 계약 대비 검수.

### 검증한 것 (한 줄씩 + 실증)
1. **수용기준 대조(TASKS.md TASK-008 AC 6항)**: AC1 문법(일반/async/메서드/중첩/`__gov__`) ✓ AC2 stricter-wins(frozen 클래스 내 watched 메서드 → effective frozen 픽스처) ✓ AC3 고정 적대 세트(setter-만-주석 order_key 1·overload·조건부 def — 상설 픽스처) ✓ AC4 검증오류 6종 각 1케이스 ✓(단 중복 필드 경로 결함 — R-1) AC5 fail-safe(parse_error·unreadable 격리, 기존 비-UTF8 픽스처 재사용) ✓ AC6 결정성+`--json`+음성검증 가능 ✓.
2. **스위트**: 워크트리 실측 14/14 PASS·exit 0. md5 반복 동일.
3. **음성검증(항상-PASS 아님 증명)**: ① cases.yaml 의 `LedgerWriter.commit` effective frozen→watched 변조 → 13/14 FAIL ② 게이트 `effective_level = strongest_level(inherited + [own])` 을 own 단독으로 무력화 → 12/14 FAIL(valid·module 두 케이스가 승계를 실가드) ③ `next_order_key` 를 상수 0 으로 → 13/14 FAIL(setter 픽스처가 동명 부착을 실가드). 각 원복 후 14/14.
4. **fresh 적대 입력(픽스처 밖)**: bare `@gov` → invalid_syntax+unresolved+protected / `__gov__` 재할당 frozen→watched → frozen 유지+duplicate·invalid_module_gov(계약 Q5 정확) / 모듈 protected+`@harness.gov(frozen)` 클래스+watched 중첩 def → 전 계층 frozen(attribute 형 인식 포함) / `@gov(**kw)`·`level=b"..."`·`level=f"..."` → 전부 보수 처리 / fresh 비-UTF8 → unreadable 격리 / stdin 모드 정상 / `def broken(` → parse_error 격리·exit 0.
5. **하류(TASK-009) 관점**: annotations 가 상속만 있는 무주석 함수도 emit(모듈/클래스 주석 하의 전 함수에 effective 부여) — join 에 필요한 형태. `def_line`·`decorators`·`order_key` 제공 — TASK-007 `start_line`·`decorators` 와 조인 가능.

### 🔴 R-1: 동일 주석 *내부* 중복 `level` — last-wins 다운그레이드 (보정 사유)
계약 Q5 `duplicate` 행은 "@gov 2개" 케이스만 구현(그쪽은 merge_gov_annotations 가 strongest — `duplicate_gov` 픽스처 정확). 한 주석 안의 중복 필드는:
- **(a)** `@gov(level="frozen", level="watched")`: `ast.parse` 가 중복 keyword 를 통과시킴(compile 단계에서만 SyntaxError — 실측). `parse_gov_call:99-104` 대입이 덮어써 watched 채택, errors=[duplicate] 만 남음. `seen_fields`(:95-97) 는 기록 전용 — 값 채택에 무관여. **frozen=blocked → 최대 approval_required 강등.**
- **(b)** `__gov__ = {"level":"frozen","level":"watched"}`: dict 중복 키는 합법 실행 코드. `parse_module_gov_value` 의 zip 순회 last-wins, **errors=[] — 완전 무기록.** silent pass 금지 정면 위반 + TASK-009 안전망(invalid→approval_required·base∪head max) 모두 우회 가능(신규 파일).
§2B 필수 질문 → 거버넌스 직접 구멍 → 비차단 불가. 수정은 국소(중복 시 오류 기록+strongest-wins)·픽스처+음성검증. → A-0004.

### 🔴 R-2: `__gov__` 비정식 형태 silent drop — 계약 개정 포함 (보정 사유)
- **(a)** 톱레벨 `AnnAssign`(`__gov__: dict = {...}`) 완전 무시 — 실행 의미는 Assign 과 동일한 자연 표기. 선언된 frozen 이 무주석 pass, base∪head 로도 비가시. **계약이 Assign 만 명시한 내 갭**(Codex 는 계약 준수) → A-0004 로 개정: 값 있는 톱레벨 AnnAssign 정식 인정.
- **(b)** 그 외 위치 `__gov__` 바인딩(if 안·클래스 본문 등) 무기록 무시 → 개정: `invalid_module_gov`+protected 보수(선언 유실을 조용히 삼키지 않는다).

### 비차단 관찰 (직접 구멍 아님 근거 포함)
1. bare `@gov` 조기 return 으로 missing_reason 미기록 — 이미 protected+unresolved 보수라 판정 영향 없음.
2. stdin 비-UTF8 시 path `"-"` vs 정상 `"stdin"` 표기 불일치 — 표기만.
3. 누락 파일 → traceback — "사용법 오류 제외" 범주(Phase A 게이트 동급).
4. annotation `type` 필드(계약 예시 밖) — 자기 스키마 추가 정보, 하류 무해 → 수용·소급 인정.
5. **order_key ≠ TASK-007 occurrence**: TASK-008 은 per-이름(무주석 def 포함 카운트), TASK-007 은 per-(이름,데코셋). setter 실측 — TASK-008 `order_key=1` vs TASK-007 `(balance,{setter,gov},0)`. order_key 끼리 join 하면 오판 → **TASK-009 join 키는 `(path, name, def_line↔after start_line)`** 로 TASKS.md 보강(비차단 — TASK-008 출력 자체는 계약 Q6 문면대로).

### 머지 판정 (D-007)
**보류** — 보정요청(A-0004). 변경 자체는 분석 전용 게이트·픽스처(비민감 범주)라 보정 통과 시 Claude 머지 예정. 리뷰 기록은 main 머지(다음 세션 가시성).

## TASK-008 보정 재리뷰 — **통과** (2026-07-05, D-019 / 보정 2272a47, 헤드 bc03b5e)

**범위**: D-018 멱등성 — 보정 델타만(게이트 +97/-19, 픽스처 module_annassign/module_duplicate/module_invalid_binding/valid 확장, cases 3건+1항목). 787a47d 기수용분 재검증 생략(A-0004 §통과 실증).

### 델타 한 줄씩 검토 (의도 대비)
1. **R-1**: `level` 대입 → `level_values` 수집 + `strongest_level()` 채택 (`extract-gov-annotations.py:101-115`, 모듈 `:200-214`). `seen_fields` 중복 → `duplicate`(데코)/`invalid_module_gov`(모듈) 기록. `reason`/`owner` 는 first-wins(결정적 — A-0004 "어느 쪽이든 무방·기록 필수" 충족). `missing_level` 은 `level_field_seen` 게이트로 분리 — level 필드가 있었는데 전부 invalid/unresolved 인 경우 missing_level 이중 기록 없이 protected 보수(정합). 비리터럴 값은 duplicate 판정 *전에* `unresolved` 로 continue — 값 미상 필드는 중복 카운트 대신 unresolved 기록(보수·기록 유지, 정합).
2. **R-2**: `is_formal_module_gov_statement` — 톱레벨 단일 Name Assign + 값 있는 AnnAssign(주석 타입 불문 — `: Final` 포함, 개정 계약 문면대로). 비정식은 `ast.walk` 전수(Assign 다중 타겟 포함·Tuple/List 언패킹·AnnAssign·AugAssign·NamedExpr) → `invalid_module_gov`+protected 주석으로 합류, 정식 문장은 `id()` set 으로 제외(중복 계상 없음). 머지는 stricter-wins 라 비정식 protected 가 정식 frozen 을 하향 못 함.
3. **하류 정합**: 스키마 무변경(필드 추가 없음) — TASK-009 join 계약(`(path,name,def_line↔start_line)`, TASKS.md 보강분) 영향 없음. module errors 로 invalid 신호 노출 — TASK-009 "errors 비어있지 않으면 최소 approval_required" 로 연결.

### 실증
- 스위트 17/17 PASS·exit 0, md5 결정성 2회 동일.
- **음성검증 4종**: 기대 변조(frozen→watched) 16/17 / strongest-wins→last-wins 원복 **15/17**(valid 데코 dup + module dup 양쪽 픽스처가 각각 가드 — AC 7 요구 문면 재현) / walk 탐지 제거 16/17 / AnnAssign 인정 제거 16/17. 전부 원복 후 17/17 — 항상-PASS 아님.
- **fresh 적대 12종**(픽스처 밖): 역순 dup→frozen+duplicate / invalid+valid dup→watched+invalid_level+duplicate / frozen+비리터럴 dup→frozen+unresolved / 모듈 3중 dup→frozen / `: Final` AnnAssign→frozen 정식 / **정식 frozen+함수내 watched 바인딩→frozen 유지**+기록 / 다중 타겟·클래스 본문·AugAssign·walrus·값 없는 AnnAssign→protected+invalid_module_gov / dict 스프레드 `{**base,...}`→invalid_module_gov+unresolved 기록. 하향 성공 경로 0건.
- 위생: `git diff --check`·`py_compile` PASS(직접 재확인).

### 비차단 관찰 (구멍 아님 근거)
1. **비선언적 `__gov__` 바인딩 미탐지**: `for __gov__ in ...`/`import x as __gov__`/`*__gov__, r = ...` → module None(실측). AC 8 열거(if 안·클래스 본문·AugAssign·다중 타겟)는 전부 충족+walrus 는 초과 달성. 이 형태들은 ⑴ 하향 불가(정식 선언은 여전히 파싱·stricter-wins) ⑵ 기존 파일 변조는 TASK-009 base∪head max 가 포착 ⑶ 신규 파일에서 이 형태로 "선언" 하는 것은 비현실적(dict 리터럴이 선언 위치에 없음). 차기 강건화 옵션: 정식 문장 밖 `__gov__` **이름 등장 자체**를 플래그(catch-all) — TASK-009 이후 여유 시.
2. **유효+invalid 혼재 dup 는 유효값 채택**(protected 승격 아님): A-0004 명세 문면("유효값 중 가장 엄한 것") 그대로. 오류·unresolved 가 항상 기록되므로 TASK-009 errors 조항이 최종 보수 방어선 — **TASK-009 리뷰 시 그 조항 구현을 반드시 확인**(이미 TASKS.md:114 에 명시).
3. 정식+비정식 공존 시 `duplicate` 오류 부가(merge 경유) — 표기 과잉이나 보수 방향·결정적.
4. module 출력에 `unresolved` 미노출 — errors 배열이 신호를 대체(표기만).

### 머지 (D-007)
분석 전용 보고 게이트+픽스처 — 비민감 → Claude 머지·push (구현자≠머지자). TASK-008 완료, TASK-009 진행 가능.

## TASK-009 `check-function-gov-level` 리뷰 — **보정요청** (2026-07-05, D-020 / 브랜치 codex/2026-07-05-task009-function-gov-level, impl 2a41a7e·헤드 e42c87f)

**대상**: 변경 함수(TASK-006 map ∪ TASK-007 classify) × TASK-008 `@gov` effective level → frozen=blocked(1)/protected=approval(2)/watched=pass(0) 판정 게이트 + 픽스처 6종·러너 확장 (+800줄, 전부 추가).

**한 줄씩 검토한 핵심 설계 판단**:
- 상류 게이트를 `importlib` 로 로드해 함수 직접 호출(`map_diff_to_functions`·`classify_python_function_changes`·`gov_gate.parse_source`) — 서브프로세스 JSON 왕복 없이 결정적. `__main__` 가드 있어 임포트 부작용 없음. 타당.
- **조인 키**: annotation index `(name, def_line)` ↔ 후보의 before/after 라인 — TASKS.md 가드(D-018 #5) 그대로. 세 게이트 모두 `node.lineno`(def 줄, 데코레이터 제외)라 의미 일치함을 소스에서 확인. setter fresh 실증으로 order_key 함정 회피 증명.
- **base∪head max**: 후보마다 양측 lookup 후 레코드 합산, `classify_records` 가 최강 레벨로 verdict. 데코 세트가 바뀌는 제거/하향은 classify 가 deleted+added 로 쪼개므로 deleted 후보의 base-라인 lookup 이 base 항을 복원 — frozen-removal 이 이 경로로 잡힘(음성검증 ②로 실가드 확인).
- **승계 연동**: TASK-008 이 미주석 함수에도 effective_level 레코드를 방출(모듈/클래스 gov 를 level_stack 으로 시딩)함을 확인 — 모듈 protected 아래 미주석 함수 수정 → approval fresh 실증. invalid 모듈 gov 도 protected 시딩이라 승계 사각 없음.
- errors/unresolved 주석 → protected 레코드(별건으로 level 레코드도 병기) — AC "errors 비면 아님 → 최소 approval" 충족(음성검증 ④).

**실증 요약**: 23/23 PASS·md5 결정성 / 음성검증 4종 성립(기대 변조·base-lookup 제거·fail-closed 제거·errors→protected 제거 → 각 FAIL, 원복 23/23) / 고정 적대 세트(setter·overload·조건부 def) + fresh 하향·우회 8종 전부 차단 — 상세는 D-020·A-0005.

**🔴 보정 사유 (fail-open 세탁 2종 — A-0005)**:
1. **R-1**: head 존재·분석-불능 `.py`(비-UTF8/문법오류) 가 **watched 레코드 1건 동반이면 verdict pass** — 전역 fail-closed 조건 `errors and not records` 가 레코드 존재로 꺼지고, per-path fail-closed 는 base-민감 전제라 신규 파일에 무력. 단독 제출 approval ↔ 동반 제출 pass 의 순서 의존 = 세탁 경로.
2. **R-2**: base 불능(주석 은닉) → head 재인코딩·주석 제거 → pass. base∪head 의 base 항 증발. AC 가 head 측만 명시한 설계 누락 → A-0005 로 AC 개정.

**비차단 관찰**:
1. `"protected"` 리터럴 하드코딩(evaluate_candidate·fail_closed_record) — approve_levels 확장 시 policy 참조로.
2. classify added/deleted 후보가 `start_line` 을 양측 키로 재사용 — 반대편 우연 일치 오매칭은 동명 한정이라 위험 미미.
3. `<unknown>` fail-closed 레코드 path 소실 — R-1 per-path 화로 자연 해소.
4. frozen 신규 도입 자체 blocked — base∪head max 의 귀결이자 정책 의도 부합(선언 도입 = 인간 확인 후 반입). 정책 확정으로 기록.
5. 무주석 `.py` 삭제 단독 → 현행 approval(전역 fail-closed 부산물) — R-1 존재/부재 구분과 함께 pass 로 정정 예정(과차단 방지, A-0005 픽스처 3).

**하류 영향(TASK-012 관점)**: 이 게이트의 `errors` 필드는 판정과 별개로 항상 채워짐 — TASK-012 통합 시 "TASK-009 errors 비면 아님 → 최소 approval" 을 중복 방어선으로 두면 R-1 류 재발 시에도 이중 안전망. 보정 재리뷰 때 TASK-012 AC 에 반영 여부 재확인.

## TASK-009 보정 재리뷰 — **통과** (2026-07-05, D-021 / 보정 aacdfe9, 헤드 d8a777c)

**멱등성 준수**: `2a41a7e`·`e42c87f` 재처리 안 함 — **보정 델타만 재리뷰**(게이트 diff +78/-10 + 픽스처 3세트 9파일 + cases 3건 한 줄씩 검토).

**R-1 해소 검증 (head 존재·분석-불능 세탁)**:
- `path_exists_at_ref` 신설 — `git cat-file -e <ref>:<path>` returncode 판별. **에러 메시지 문자열 파싱 아님**(A-0005 계약 준수), 결정적.
- head 존재+`parse_error`/`unreadable` → **다른 레코드 유무와 무관하게** per-path fail-closed 레코드(base 민감 시 그 최강 레벨, 아니면 protected). 구 `if sensitive_levels_in_result(base)` 전제 제거 확인.
- 전역 `if errors and not records:` → **`upstream_errors` 사전 스냅샷**(map/classify top-level error 만) 무조건 발동으로 교체 — AC ④(records 유무 무관 최소 approval) 구현. per-path 오류는 이제 항상 자체 레코드 동반이라 "error 있고 record 없는" 조합 자체가 소멸(코드 전수 확인: 오류 append 3곳 전부 레코드 쌍).
**R-2 해소 검증 (base 존재·불능 은닉 세탁)**: base 존재+불능 → head 가독 여부 무관 per-path protected fail-closed(`side=base`). base 불능+head 삭제 조합도 이 블록이 잡음(존재 분기 검토 + F3 fresh 실증).
**삭제 분기 검증**: head 부재 + base 가독·민감 → base 최강 fail-closed(deleted-frozen 픽스처 유지) / base 가독·비민감 → pass(`plain-delete-pass` — A-0005 §요구 3 의 과차단 정상화, 동작 변경 명시대로) / base 불능 → protected(base측 블록).

**실증(워크트리·26/26)**: 26/26 PASS·exit 0 + md5 결정성(2회) + **음성검증 4종 전부 성립**: ① head 무조건 레코드 → 구 base-민감 조건 원복 = `unreadable-head-laundering` FAIL(25/26) ② base측 fail-closed 제거 = `unreadable-base-laundering` FAIL ③ **존재판별 무력화(head_exists=True 고정) = `plain-delete-pass` FAIL** — 존재판별이 과차단 방지의 실체임도 증명 ④ 기대 변조(approval→pass) FAIL. 각 원복 26/26.
**fresh 적대 6종 (픽스처 밖, 전부 계약대로)**: F1 head **문법오류**(unreadable 아닌 parse_error 경로)+watched 동반 → approval — 세탁 불가가 두 불능 유형 모두에 성립 / F2 같은 파일 base·head 양측 불능 M+동반 → approval·per-path 레코드 2건(양측) / F3 base-불능 파일을 head 에서 **삭제**+동반 → approval / F4 불능 파일 **순수 리네임**(host renames ON)+동반 → approval — 구경로 base-불능·신경로 head-불능 양쪽 fail-closed, 리네임 세탁 없음 / F5 가독·무주석 순수 리네임 단독 → pass(과차단 없음) / F6 신규 불능 `.py` **단독** → approval — 전역 조건 교체(`upstream_errors`)로 인한 회귀 없음.

**보수성(COMMON-RULES §1)**: 델타가 R-1·R-2·§요구 3 에 정확히 국소(게이트 1파일+픽스처+cases+인계·요약), 무관 리팩터 없음, Claude 소유 무접촉. 커밋 2건 §3 상세 형식·`git diff --check`·`py_compile` 준수.

**비차단 관찰**:
1. AC ④(top-level upstream error → 무조건 approval)는 회귀 픽스처 없음 — 상류 top-level error 시 후보 목록도 대체로 함께 소실돼 "records 동반+top-level error" 를 결정적 픽스처로 재현하기 곤란. 코드 검토(`upstream_errors` 스냅샷 시점)로 확인, F6 으로 무회귀 확인. TASK-012 통합 시 상류 error 주입 픽스처 옵션.
2. 양측 불능 시 per-path 레코드 2건(base·head side 각각) — 중복 표기지만 보수 방향·결정적(F2).
3. `absent_annotation_result` 의 `absent: True` 필드는 현재 소비처 없음 — 정보성 표기.
4. D-020 관찰 1·2·4(protected 리터럴·반대편 라인 재사용·frozen 신규 도입 blocked=정책 확정)는 유지, 관찰 3(`<unknown>` path 소실)·5(무주석 삭제 과차단)는 이번 보정으로 해소 확인.

**하류 반영(TASK-012)**: D-020 하류 메모대로 — TASK-009 출력의 `errors` 비어있지 않으면 통합측도 최소 approval 을 중복 방어선으로. TASKS.md TASK-012 AC 가드에 한 줄 보강.

## TASK-012 `generate-change-evidence` 감사카드 통합 리뷰 — **통과** (2026-07-05, D-023 / 브랜치 codex/2026-07-05-task012-evidence-integration, impl 81147f5·헤드 20067e8)

**대상**: 감사카드 생성기에 함수 단위 `@gov` 판정(TASK-009) 통합 — `changed_functions` 수록 + 최종 verdict 승격. 변경 = 게이트 1파일 +102/-13, tests(cases +88·run-tests +34·evidence-integration change-intent 픽스처).

**한 줄씩 검토한 핵심 설계 판단**:
- `check-function-gov-level`(TASK-009) 를 `importlib` 로 로드해 함수 직접 호출(`can_run_function_gov` 가 git-ref `..` 입력에서만 실행) — 서브프로세스 왕복 없이 결정적. 파일 입력(MVP-0)은 스킵.
- `combine_verdicts`: 경로판정(intent∪zone `verdict_and_exit`)과 함수판정을 합성 — **blocked = 경로 blocked ∨ 함수 blocked / approval = 경로 approval ∨ 함수 approval ∨ 함수 errors 비어있지않음 / else pass**. 최댓값 합성이라 어느 층이든 승격시키면 최종 승격 = fail-closed 정합.
- TASK-009 가 내부에서 TASK-006 map(`<module>` 포함) ∪ TASK-007 classify 를 이미 병합 → **D-013 가드(TASK-007 단독 판정 금지·모듈레벨 병합) 자연 충족**(module-protected 픽스처 `app/settings.py::<module>` 로 실증).
- 상류 게이트 error 는 TASK-009 `errors`+fail-closed 레코드로 흘러 approval — **D-012/D-021 가드("빈 결과 ≠ clean") 정합**. evidence 도 `function_gov.errors` 를 중복 확인.
- 최상위 `main()` try/except 가 어떤 예외(bad ref 등)든 **blocked fail-closed**(기존 MVP-0 핸들러 — 회귀 아님).

**실증 요약**: 29/29 PASS·md5 결정성 / 음성검증 3종(통합 무력화 → 3 픽스처 FAIL·기대 변조 FAIL·errors 분기 제거 → 무변화[관찰 1]) / **fresh 적대 격리**:
- **경로-clean + frozen 함수 변경 → blocked**(신규 repo, intent=pass·sensitive=pass 인데 `@gov(frozen)` 본문 수정 → 최종 blocked. 경로판정은 frozen zone 이 아니면 최대 approval 이므로 blocked 는 함수-gov 단독 기여 — MVP-1 핵심 갭 폐색 실증).
- **parse_error 신규 `.py`(경로-clean) → approval**(`function_analysis_error` reason — 빈 결과 ≠ clean 실증).
- **무주석 함수 변경 → pass**(함수 reason 없음, 과차단 없음) / **name-status 파일 입력 → 함수분석 스킵**(`changed_functions:[]`, MVP-0 호환).

**보수성(COMMON-RULES §1)**: 변경이 TASK-012 에 국소, Claude 소유 무접촉, scope-creep 없음. `git diff --check`·`py_compile` PASS, 커밋 §3 준수.

**비차단 관찰**:
1. **`or function_gov.get("errors")` 중복 방어선 — 독립 테스트 부재**: 음성검증 M2(이 분기 제거)가 29/29 무변화. 이유 — post-D-021 TASK-009 는 errors 가 있으면 **항상 fail-closed 레코드도 방출**해 verdict≥approval 이므로, evidence 의 errors-분기는 verdict 로 이미 approval 이 된 케이스와 겹쳐 **단독 발화가 현재 불가**. 死코드는 아님(TASK-009 가 R-1 류로 회귀해 pass+errors 를 내면 이 분기가 잡는 최후 방어선 — 의도된 defense-in-depth, TASKS.md AC 명시 "중복 방어선"). 권고: TASK-009 pass+errors 를 강제하는 stub 픽스처로 이 분기 발화를 고정하거나(옵션), 현행 중복 방어로 수용.
2. **name-status 파일 입력 = 함수분석 조용히 스킵**: `can_run_function_gov` 가 `..` ref 만 허용. canonical 호출은 git-ref(`<base>..<head>`, 루트 README §실행 확인)라 **운영 경로는 완전 커버** — 파일 입력은 MVP-0 레거시 호환. 다만 누군가 파일 입력 모드로 MVP-1 diff 를 넣으면 함수-frozen 을 조용히 놓침 → **git-ref 필수를 README/AC 에 명시 권고**(비차단 — 회귀 아님·설계된 경로 안전).
3. **일반 예외 → blocked**: AC 문면 "최소 approval(파괴적이면 blocked)" 보다 강한 일괄 blocked. 안전 방향(fail-closed)이자 기존 MVP-0 핸들러 — 수용.
4. **`changed_functions` base·head 후보 중복 표기**: TASK-009 `changed_functions`(candidates) 를 그대로 수록 — 같은 함수가 base/head 라인 메타로 2행. 감사용 무해·결정적.

**하류(향후)**: MVP-1 통합 완료. capability(2층, TASK-010/011)도 완성 시 이 게이트가 `new_capabilities[]` 를 같은 방식으로 병합하면 됨(설계 `docs/capability-catalog-design.md` §하류 계약과 정합).

---

## TASK-010 `extract-python-capabilities` 능력 추출기 리뷰 — **통과** (2026-07-05, D-024 / 브랜치 codex/2026-07-05-task010-capabilities, impl 1ed4222·헤드 cb58354)

**대상**: 2층(능력 추론) 첫 게이트 — 단일 `.py` → 카탈로그(`policies/sensitive-capabilities.yaml`) `imports`/`calls`/`builtins` 신호로 민감 능력 집합 추출. **보고 전용·exit 0·판정 없음**(TASK-008 대응, 판정은 TASK-011). 변경 = 신규 게이트 296줄 + 픽스처 3파일 + tests(cases +142·run-tests +49) + README 1줄.

**한 줄씩 검토한 핵심 설계 판단**:
- **import 바인딩 표를 `ast.walk` 전수로 구축**(파일/함수/클래스 내 import 포함) → 별칭·from-별칭·submodule root 바인딩(`import urllib.request` → `urllib`, alias 있으면 full target). `resolve_call_name` 이 `Call.func` attribute 체인을 바인딩으로 풀어 점표기 전체이름 산출 → `calls` 대조. `Name` 호출은 `builtins` 대조.
- **star import 처리**: `from X import *` → `unresolved_dynamic` 기록 + `caps_for_catalog_module(X)` 로 X 가 catalog 모듈이면 `star_import` 신호(우회 backstop). `caps_for_catalog_module` 은 imports·calls-파생 모듈 프리픽스 모두 매칭.
- **import backstop = 핵심 방어**: 호출 해석이 별칭·getattr·재대입으로 실패해도 `imports` 목록 모듈(subprocess/pickle/requests…)의 import 자체가 신호 → 능력 포착. `caps_for_import` 이 `module_matches`(정확 일치 or `<mod>.` 프리픽스)로 매칭(프리픽스 오탐 없음 — `socketserver`≠`socket`).
- **level clamp**: catalog level ∉ {protected,watched} → `invalid_capability_level` 기록 + protected clamp(2층 blocked 승격 금지, D-004). unknown 신호종 → `unknown_signal_kind` 기록.
- **fail-safe**: 문법오류→`parse_error`, 비-UTF8→`unreadable`, caps=[], exit 0(TASK-013 계보). 카탈로그 오류는 격리 경로에서도 방출(일관).

**실증 요약**: 33/33 PASS·md5 결정성(fresh 입력 2회 동일).
- **fresh 적대 격리(픽스처 밖 독립검증)**: 신규 파일로 계약 Q4 7종 전부 감지 확인 — 별칭·from-별칭·star·getattr(import backstop)·`__import__`·무-import `exec`/`eval`/`compile`·**중첩-중첩 def 내부 `import pickle`**(walk 전수). 재대입 `x=subprocess; x.run()` 도 import backstop 으로 포착.
- **음성검증(rigged 차단, 3종 mutation)**: ① star_import 핸들링 제거 → `python-capabilities`/`-invalid-policy` FAIL ② Import 노드 backstop 신호 제거 → FAIL ③ `build_import_bindings` walk→`tree.body`(톱레벨만) → FAIL(중첩 import 미감지). 원복 시 33/33 — 단일 golden 의 capabilities/signals exact-match 가 각 감지경로의 실가드.
- **clamp/검증오류**: `frozen-policy.yaml`(frozen+mystery 신호) → `invalid_capability_level`+protected clamp·`unknown_signal_kind` 기록 확인.
- **fail-safe(fresh)**: 문법오류 → parse_error·caps=[]·exit 0 / 비-UTF8 → unreadable·caps=[]·exit 0 / stdin path="stdin".

**보수성(COMMON-RULES §1)**: TASK-010 에 국소, **Claude 소유(`policies/sensitive-capabilities.yaml` 포함) 무접촉**, scope-creep 없음. `git diff --check`·`py_compile` PASS, 커밋 §3 준수.

**비차단 관찰**:
1. **🟠 call-only 모듈 동적 우회 갭 (거버넌스 관련·비차단→TASK-011 AC 가드 신설)**: `os` 는 잡음 이유로 `imports` 무신호(설계 Q1) → import backstop 이 없다. 따라서 `getattr(os,"system")(cmd)`·재대입 `z=os; z.system(cmd)` 는 **미감지**(실증: `caps=[]` 아닌 subprocess_exec 이 direct 호출만 1건). 반면 직접 `os.system(cmd)`·`import os as o; o.system()` 은 정확 감지. **계약 Q4 적대 세트는 subprocess 기반(전부 import-backstop) + 내장이라 100% 통과**하므로 계약 미달 아님, 주 실행벡터(subprocess)는 완전 커버 → **비차단**. 단 os.system-계열 동적 은닉은 능력 도입 은닉 경로이므로 **TASKS.md TASK-011 AC 가드로 명시**: 추출기가 `getattr(<바인딩된-모듈>, "<문자열 리터럴>")(...)` 를 점표기 호출로 해소하면 call-only 모듈 동적우회를 닫음(내가 짠다면의 개선안) — 또는 catalog 문서화된 수용 잔여로 명시. 2층 approval-max 라 최악도 승인 프롬프트 누락(오차단 아님).
2. **parse_error/unreadable = 문자열 메시지(Q7 예시는 bool)**: 구현이 `False` 또는 진단 메시지 문자열 방출. truthy 라 하류 TASK-011 의 `if parse_error` fail-closed 판별 정상 동작, 감사 정보 enrich. 수용(비회귀).
3. **star_import 과매칭(안전 방향)**: `caps_for_catalog_module` 이 call-파생 모듈 프리픽스까지 매칭 → `from urllib import *`·`from os import *` 가 outbound_network·subprocess_exec 를 star_import 신호로 표기. 과경고(2층·안전 방향) — 수용.

**하류(TASK-011)**: 이 추출기의 `unreadable`/`parse_error` truthy 를 **head 측 per-path fail-closed approval** 로 반드시 처리(TASKS.md TASK-011 AC 이미 명시). 능력 판정은 `head − base`(base∪head 아님) — TASK-009 와 정반대, never-blocked 상한. call-only 동적우회(관찰 1)는 TASK-011 AC 가드로 이월.

---

## TASK-011 리뷰 — 신규 능력 diff 게이트 `check-new-capabilities.py` (D-025, 통과·머지)

대상: `codex/2026-07-05-task011-new-capabilities`(impl `1aa88d8`·헤드 `c3425cf`). 신규 게이트 304줄 + TASK-010 추출기 D-024 보강(+34) + 픽스처 5종 + tests + README 1줄. 계약 `docs/capability-catalog-design.md` Q2·Q5·Q6.

**심층 검증 방식**: 게이트 소스를 한 줄씩 정독 + **픽스처 밖 fresh git repo** 다수를 직접 만들어 구동(적대 입력) + **rig-and-revert 음성검증**으로 핵심 로직이 실가드임을 실증. 무발견≠통과 원칙.

**🔴 AC 실증(3종)**:
1. **head−base 신규만(Q5)** — fresh repo: base·head 양쪽 `subprocess_exec`(base `subprocess.run`, head `+Popen` 같은 id) 파일은 **미검출**, 신규 파일 능력만 `approval`. **음성검증(rigged)**: `sorted(set(head_caps) - set(base_caps))` → `sorted(set(head_caps))` 로 변조 시 이미-있던 파일 오검출(pass→approval) = head−base 로직이 실가드(base∪head 아님 고정). 원본 pass 복귀 확인. 신규파일=전부신규·삭제파일=신규없음 픽스처 존재.
2. **never-blocked(Q2)** — fresh frozen-level catalog → `invalid_capability_level`+protected clamp → `approval_required`·exit 2. **구조적 불변식**: 소스에 exit-1/blocked 경로 자체가 없음(상수 PASS=0/APPROVAL_REQUIRED=2 뿐, grep 확인). 이중 안전: clamp 제거해도 level `frozen`≠`watched`→new_capabilities(approval)→blocked 승격 불가.
3. **fail-closed per-path(Q6·A-0005)** — fresh: 문법오류 head 파일 + 비-UTF8 head 파일이 **각각** per-path `fail_closed`, **동시에** 무관한 신규 `requests` 캡도 `new_capabilities` 에 생존 = **D-020 세탁 없음**(전역 "errors and not records" 아니라 파일별 무조건 `continue`). base 불능→base_caps 빈집합+errors→approval. 최상위 예외→approval fail_closed(blocked 아님).

**D-024 추출기 보강(AC 인가) 검증**: fresh 로 매핑 확인 — 인라인 `getattr(os,"system")(c)` ✓ / 재대입 `r=os; r.system(c)` ✓ / 재대입연쇄 `r=os; s=r; s.system(c)` ✓ / import-신호 getattr(subprocess) ✓ / 직접 os.system ✓. 회귀 픽스처 `valid.py`(중첩 def 내 `import os` + 두 형태) + golden 확장으로 고정. Assign 바인딩은 walk 전수라 중첩 def 도 커버.

**보수성(§1)**: TASK-011 범위 국소, **Claude 소유(policies/docs/CLAUDE/decisions/answers/review-notes/templates) 무접촉**(diff 확인), scope-creep 없음. README +1(실행 예시)만. `git diff --check`·`py_compile` PASS.

**⚠️ 비차단 관찰 1건 (거버넌스 관련·§2B 명시 → 차기 AC 가드)**:
1. **분리대입 getattr 미감지 (call-only 모듈)**: D-024 🟠 가드의 **두 명시 형태(인라인 getattr·재대입)는 둘 다 폐쇄·회귀픽스처화 = AC 충족**. 그러나 리뷰 중 fresh 로 **제3 변형** 발견 — `fn = getattr(os,"system"); fn(c)` (getattr 결과를 변수에 담아 별도 호출)는 call-only 모듈(os 계열)에서 **여전히 미감지**(`caps=[]`, `unresolved_dynamic` 마커도 없음 — 실증). 원인: `build_import_bindings` 의 `ast.Assign` 핸들러가 value=`getattr(...)`(ast.Call)을 `dotted_name` 로 해소 못 해 `fn` 을 바인딩 못 함. **비차단 근거**: (a) import-신호 모듈(subprocess/pickle/socket 등 주 실행벡터)은 import backstop 이 어떤 난독이든 포착 — 이 갭은 오직 의도적 call-only 인 os 계열 한정, (b) 2층 approval 상한 → 최악도 승인 프롬프트 누락(오차단·자동머지 아님), (c) D-024 가 이미 "call-only 동적우회" 를 수용-후속처리로 분류한 **좁은 하위변형**, (d) 완전폐쇄엔 지역 dataflow(`fn` 이 callable 보유) 추적 필요 = 대규모 리팩터(§2B 강요 금지). → **TASKS.md TASK-011 차기 AC 가드로 이월**(분리대입 getattr 해소 또는 catalog 문서화 수용잔여).

**참고(비회귀·안전 방향)**: catalog 검증오류(invalid_capability_level 등)가 변경 파일 수만큼 base/head 양측에 중복 append 됨 — verdict 는 여전히 approval(무해), 감사 출력만 다소 중복. 결정적·비차단.
