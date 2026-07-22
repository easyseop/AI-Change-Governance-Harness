# decisions.md — 확정 결정 (대화 ≠ 결정. 여기 적힌 것만 확정)

> Q/A 에서 합의된 것을 결정으로 승격한다. 번호·날짜·근거를 남긴다.

---

## D-055 (2026-07-16) TASK-023 R-3 보정 재제출 재리뷰 — R-3 해소 확인 · **통과 · Claude main 머지** (MVP-2 TASK-023 콜그래프 빌더 완결)
**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` (헤드 `456a965`, R-3 보정 impl `5c58b2c`). 선행 D-054/A-0020(R-3 보정요청). **재리뷰 범위 = R-3 보정 델타(`5c58b2c`의 코드 부분)만** — R-2 bare 해소·엔진 본체·getattr·조건부 union·결정성·kit 는 D-052~D-054 에서 통과 확정, 재론 없음. **판정 = 리뷰 통과, Claude `main` 머지·push. 더 할 일 없음.**
**R-3 해소 확인 ✓ (A-0020 권장 ①+③ 문자 그대로 채택)**: ① `build_module_locals`(285–286)에 `if "." in node["name"]: continue` 2줄 추가 → 클래스메서드 `C.sink`·중첩 def(scoped name 에 `.` 포함) 를 `module.<basename>` 후보에서 제외. `module_locals["app.overloads.sink"] = ["app.overloads.sink"]`(모듈함수 단독). ③ 상설 픽스처 `overloads.py` 에 `from app import overloads as overloads_module` + module-qualified caller `qualified_bar(): return overloads_module.sink()` 추가, `cases.yaml` 에 노드 `app.overloads.qualified_bar`·엣지 `qualified_bar -> app.overloads.sink` 단언 → §2B 동명 오버로드 상설 커버리지 **3변형 완성**(bare-module-caller R-1 · bare-method-caller R-2 · module-qualified R-3).
**적대 재검증(fresh·픽스처 밖·격리 worktree `wt-task023`)**: module-qualified 동명 오버로드 4종 전부 **정답** — ① repoB(`from app import mod; mod.sink()`, `class C` 를 `def sink` **앞**에 배치해 순서운 배제) → `run -> app.mod.sink`(모듈함수, `C.sink` 아님) ② **repoD(거버넌스)** `import app.reports as reports; reports.export()`, governed 모듈 `export` vs `class Report.export` → `run -> app.reports.export`(**settlement export 엣지 보존** = TASK-024 역도달 민감 포착 복구) ③ repoE(대상이 **메서드만** 존재 `only.onlym()`) → **`unresolved`**(거짓엣지 주입 없음·조용한 오염 폐쇄) ④ repoF(깊은중첩 `Outer.Inner.deep` vs 모듈 `deep`, `d.deep()`) → `run -> app.deep.deep`. **rig-and-revert 음성검증**: 2줄 가드 제거 → 동일 4종이 각각 `C.sink`/`Report.export`/`C.onlym`/`Outer.Inner.deep` 로 **오염 재현**(픽스처 fresh 입력 비-rigged 확인) + `callgraph-repo-static` **단독 FAIL(0/1)**; 원복 **81/81 PASS** = 수정+픽스처 load-bearing(항상-PASS 아님). Python 의미(`mod.sink` = 모듈 속성 = 최상위 함수만) 상 메서드 제외는 항상 안전 — 메서드는 여전히 `definitions` 직접경로(220–221)로 `mod.C.sink` 해소되므로 손실 없음(repoA/기존 fixture 무회귀 실증).
**보수적 개발(§1)**: R-3 코드 델타 = `extract-callgraph.py` **2줄** + `overloads.py` 픽스처 **7줄**(자기-import + qualified_bar) + `cases.yaml` **4줄**(노드1·엣지2·정렬) = 수정계약 범위 정확 준수. bare 경로(`visible_local_names`)·getattr·조건부 union·`resolve_repo_function` 판정로직 **무변경**. `policies/*`·`docs/*`·`CLAUDE.md`·`templates/*` **무접촉**(name-only diff 확인). scope-creep·over-reach 없음. 함께 들여온 A-0018/19/20·D-052~054·review-notes 는 **재제출 전 `origin/main` merge**(collab-protocol §5.1 · D-050 함정을 **이번엔 회피** — Codex 가 지침대로 병합 후 재제출)로 유입된 내 기존 기록(origin/main 과 동일·Codex 변조 없음).
**비차단 이월**: O-1(중첩 데코레이터/기본인자 조용한 유실 — 틀린 엣지 없이 누락만) TASK-025 고정 적대세트로 이월 유지(§2B 필수질문=아니오).
**머지 판정(D-007)**: `extract-callgraph.py` = **정적 콜그래프 분석 게이트**(MVP-2 intra-repo·정산·인증/인가·암호화·DB migration·infra 해당 없음·자동차단 권한 없음) → CLAUDE.md §3 기준 **비민감**. TASK-005~013·018·019·022 동일 범주(D-020~D-032·D-050 선례). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push. MVP-2 TASK-023 완결.**
**멱등성**: `5c58b2c`·`456a965` **재처리 금지**. 상세·실증: `collab/answers/A-0020.md` §R-3 해소 · `review-notes.md` TASK-023 R-3 재재재리뷰(D-055) 절.

## D-054 (2026-07-15) TASK-023 R-2 보정 재제출 재리뷰 = R-2 해소·R-3 신규 보정요청 (module-qualified 동명 오해소)
**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` (헤드 `a6756c1`, R-2 보정 impl `25f9b32`). 선행 D-053/A-0019. **재리뷰 범위 = R-2 보정 델타(`25f9b32`)+method-caller 픽스처만**. **판정**: R-2(bare method-caller)는 **정확·load-bearing 해소 확인**(4종 fresh 적대입력·음성검증 통과), 그러나 §2B "동명 오버로드 고정 적대세트" 를 **module-qualified 변형**으로 돌리자 **동일 결함 클래스의 세 번째 인스턴스(R-3·🟠 블로킹)** 노출 → **코드 머지 보류·리뷰기록만 main.**
**R-3 요지**: `build_module_locals`(283–289)가 클래스메서드 `C.sink` 를 basename 으로 잘라 `module.sink` 키에 등록 → module-qualified 호출 `mod.sink()` 이 `sorted()[0]` 로 대문자 `C.sink`(클래스메서드) 먼저 pick → **모듈-레벨 governed sink 엣지 유실 + 형제 메서드 거짓엣지 주입**(조용한 오염, unresolved 미표기). fresh 실증 repoB/repoD(governed `reports.export` 시나리오)로 재현 = 민감 변경 미포착(§2B 필수질문=예 → 비차단 불가). Python 의미상 `mod.sink` 는 모듈 속성=최상위 함수만 가리키므로 메서드 등록은 항상 틀림.
**보정 ①권장(소델타)**: `build_module_locals` 에서 scoped name 에 `.` 있는 노드(메서드/중첩 def) 제외 — `module.<name>` 로 도달 불가. Claude 사본 실증: 2줄로 81/81 유지 + repoB/repoD 교정, repoA 무회귀(메서드는 `definitions` 직접경로로 여전히 해소). ② module_locals 충돌 시 모듈-레벨 우선. ③ 상설 픽스처를 module-qualified 변형으로 확장(동명 오버로드 3변형 완성).
**비차단 유지**: O-1(중첩 데코레이터/기본인자 유실) TASK-025 이월.
**멱등성**: `25f9b32`·`a6756c1` 재처리 금지. 재제출은 R-3 델타+module-qualified 픽스처만. ⚠️ **재제출 전 `origin/main` merge 필수** — 이번 R-2 재제출도 미병합이라 브랜치가 main 대비 리뷰기록 삭제 형태(D-050 함정 **3회째**); 이번 라운드 A-0020·D-054 추가로 격차 확대. 상세: `collab/answers/A-0020.md` · `review-notes.md` TASK-023 R-2 재재리뷰(D-054) 절.

## D-053 (2026-07-15) TASK-023 R-1 보정 재제출 재리뷰 = R-1 부분해소·R-2 잔여 보정요청 (method-caller 동명 오해소)
**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` (헤드 `86eef67`, 보정 impl `df7e54c`). 선행 D-052/A-0018. **재리뷰 범위 = R-1 보정 델타(`df7e54c`)+신설 픽스처만**. **판정**: R-1 **모듈-caller 케이스 해소 확인**, 그러나 **동일 결함 클래스의 method-caller 변형 잔존(R-2·🟠 블로킹)** → **코드 머지 보류·리뷰기록만 main.**
**보정 델타(A-0018 권장 ①+③ 정확 채택)**: `visible_local_names` 클래스 확장 루프 2줄 제거 + 상설 픽스처 `app/overloads.py`(모듈 `foo`+`C.foo`+`bar()`) + cases 엣지 `bar->foo` 단언. O-1 은 A-0018 허용대로 TASK-025 이월. 보수적 개발 OK(게이트 2줄 삭제+픽스처1+cases6·`policies/*`·Claude소유 무접촉).
**✅ R-1 모듈-caller 해소**: `run-tests.sh` **81/81**. 비교=`assert_equal` 정렬 리스트 완전일치(spurious 엣지 즉시 FAIL, 강함). 음성검증: 제거 루프 재삽입→callgraph 케이스 **단독 FAIL(0/1)**·원복 81/81=load-bearing. fresh(모듈 `foo`+`C.foo`+`Zebra.foo`+`bar:foo()`, Zebra 로 순서독립)→엣지 `[bar->foo]`·spurious 0.
**🟠 R-2(블로킹·잔여)**: `visible_local_names` 의 **parents-prefix 확장이 클래스명을 여전히 포함**(`visit_ClassDef` 가 `self.parents` 에 클래스명 push). caller 가 **메서드**면 bare 호출이 `{Class}.{name}` 후보를 만들고 `sorted()[0]` 이 대문자 클래스명을 먼저 pick → 형제 메서드 오해소. Python 의미상 메서드 본문 bare 이름은 **클래스 스코프 건너뜀**(LEGB)이라 **항상 틀림**. fresh 실증: `def sink()`(모듈)+`class C{def sink; def caller: return sink()}` → 산출 **`C.caller->C.sink`(틀린 엣지 주입)**·정답 `C.caller->모듈 sink` 부재·`unresolved` 에도 없음(R-1 보다 나쁜 *조용한 오염*). 이는 A-0018 R-1 이 없애려던 실패모드("진짜 caller→sink 엣지 유실")를 method-caller 경로에서 그대로 재현 = 민감 변경 미포착(§2B 필수질문=예·비차단 불가). **거짓 커버리지**: 신설 `overloads.py` 는 모듈-caller `bar` 만 단언, method-caller 변형 미커버 → §2B 동명 오버로드 커버리지 절반만 채우고 전체를 채운 듯한 확신.
**보정(①권장·소델타)**: ① `visible_local_names` 에서 **클래스 스코프 skip parents-prefix만** 후보화(prefix ∈ `class_names` → skip). **Claude 사본 실증**: 3줄로 `run-tests.sh` **81/81 유지**+method-caller `C.caller->모듈 sink` 교정. ② 동명 충돌 시 모듈/전역 우선(또는 union). ③ **상설 회귀 픽스처를 method-caller 변형으로 확장**(모듈 sink vs `C.sink`+`C.caller:sink()`→엣지 모듈 sink·`C.caller->C.sink` 부재 단언).
**🟡 O-1(비차단·유지)**: 중첩 데코레이터/기본인자 유실. Codex 가 TASK-025 이월 선언(handoff `86eef67`)=수용. 틀린 엣지 없이 누락만.
**멱등성**: `df7e54c`·`86eef67` 재처리 금지. 재제출은 R-2 델타+method-caller 픽스처만. ⚠️ **재제출 전 `origin/main` merge 필수** — 이번 재제출도 `origin/main`(D-052/A-0018) 미병합이라 브랜치가 main 대비 리뷰기록을 삭제하는 형태(D-050 함정 2회째). 상세: `collab/answers/A-0019.md` · `review-notes.md` TASK-023 재리뷰(D-053) 절.

## D-052 (2026-07-15) TASK-023 콜그래프 빌더 리뷰 = 보정요청 (동명 클래스메서드 오해소 → caller→sink 엣지 유실)
**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` (헤드 `92b2955`, 구현 `2a6cd09`). **판정**: **보정요청 1건(🟠 블로킹) + 비차단 관찰 1건** — 코드 머지 보류, 리뷰기록만 `main`.
**통과분(실증·재현)**: `tests/run-tests.sh` 81/81 · `kit/tests/run-entrypoint-tests.sh` 9/9 · `mutation-check` 131 전부 재현. fresh 적대입력으로 AC #1(별칭/from-import/동일모듈 해소)·#2(getattr 미해소 → `unresolved_calls`+`coverage.unevaluated` 노출)·#3(결정론 3회 md5 동일)·#4(조건부 def 동일-id union) 통과. 음성검증(기대 엣지 변조→callgraph 케이스 단독 FAIL 80/81)=테스트 load-bearing. 동반작업 **G-sink-1**(extract-sinks 라이브 정책 결합을 fixture-local zones 로 절단·settlement frozen auto-sink 로 구동 확인)·**A-0017**(러너 `⚠` 안내 2건 echo 전용·판정 무영향·진입점 3케이스 load-bearing) 정합. 보수적 개발 OK(`policies/*`·Claude 소유 무접촉·scope-creep 없음).
**🟠 R-1(블로킹)**: `extract-callgraph.py` `CallVisitor.visible_local_names()` 가 **모듈 내 모든 클래스**에 `{class}.{name}` 후보를 무조건 추가 + `resolve_repo_function` 이 `sorted()[0]`(사전순 최소) pick → 대문자 클래스명이 소문자 함수명보다 먼저 정렬돼, 같은 모듈에 모듈함수 `foo`+클래스메서드 `C.foo` 공존 시 bare `foo()` 가 **`C.foo` 로 오해소**. fresh 실증(`adv1`): `bar->app.m.foo`(정답) **부재**, `bar->app.m.C.foo`(오답) 발화. Python 에서 bare 이름은 클래스멤버에 바인딩 불가 → 이 확장 루프는 **정답 엣지 0개 생성(공식 fixture 7엣지 루프 제거해도 바이트 동일)**하면서 **진짜 caller→sink 엣지만 유실**. 모듈함수가 sink 면 TASK-024 역도달 상류에서 호출자 누락 = **민감 변경 포착 실패(거버넌스 하류 직접 구멍)**. §2B 필수 "동명 오버로드" 적대세트 케이스가 제출 픽스처에 **없고**, 넣으면 실패. AC #1(틀린 함수로 해소)·#4(union 아닌 pick-one-wrong) 불충족 → 비차단 불가.
**보정(①권장)**: ① `visible_local_names` 클래스 확장 루프 제거(2줄·fixture 보존 실증) ② 또는 스코프조건+동명 union ③ **상설 회귀 픽스처 신설**(모듈함수 vs 동명 클래스메서드 → 엣지가 모듈함수로).
**🟡 O-1(비차단)**: `visit_function` 이 `node.body` 만 방문 → **중첩** 데코레이터/기본인자 호출(함수 caller 명확)이 조용히 유실(`adv4`: `outer->make_wrapper` 부재·unresolved 에도 없음). 틀린 엣지는 안 만들고 누락만 → R-1 과 함께 고치거나 **TASK-025 고정 적대세트(데코레이터/기본인자)로 이월**(본 관찰이 AC 근거).
**멱등성**: `2a6cd09`·`92b2955` 재처리 금지. 재제출은 보정 델타+신설 픽스처만 재리뷰. **재제출 전 `origin/main` merge**(D-050 충돌 재발 방지). 상세: `collab/answers/A-0018.md` · `review-notes.md` TASK-023(D-052) 절.

## D-051 (2026-07-15) 킷 외부 오픈소스 E2E 검증 + 실사용 함정 2건 안내 보강 (형 지시)
**맥락**: 형 지시("오픈소스 들고와서 변경 여러 군데 해보고 kit 테스트")로 실제 외부 저장소 4종에 킷을 소급 적용 — click·requests·flask(Python)·gorilla-mux(Go), 각각 얕은 클론 후 통제된 변경 시나리오 주입.
**결과(실측)**:
- **Python 3종 × 4시나리오 = 12/12 기대 일치**: S1 무해(in-scope 주석)→PASS · S2 신규능력(subprocess.run 주입)→APPROVAL(`subprocess_exec` 정확 표기) · S3 선언범위 밖(README)→APPROVAL(out_of_scope) · S4 frozen 존 접촉→BLOCKED. 판정 게이트 4층이 외부 코드에서 정확히 분리 동작.
- **Go 한계 실측(정직)**: 경로층(frozen 차단) 언어 무관 작동 ✓ / **능력층은 `os/exec`·`exec.Command` 미탐(PASS)** — "능력·함수층 Python 전용" 알려진 갭의 외부 실증. 비-Python repo 의 방어선 = 경로층만.
**발견된 실사용 함정 2건(킷 버그 아님 — 도입자 혼동 지점)**:
1. `change-intent.yaml` 스키마 오기: `allowed_paths` 를 top-level 에 두면(정식은 `change_intent:` 아래 중첩) 게이트가 빈 선언으로 읽어 **전 변경 out_of_scope(승인요구)**. fail-safe 라 구멍은 아니나 "왜 다 승인요구?" 혼란 — 테스트 중 검증자(Claude 본인)도 두 번 헛짚음.
2. 감사카드 기본 출력이 대상 repo 안(`change-evidence.yaml`) → `git add -A` 시 커밋에 섞여 **다음 diff 오염**(실측 재현).
**처리(상호견제 준수 — 분류기 차단 수용)**: Claude 가 러너 `⚠` 안내 2건을 직접 구현·실증(경고 3케이스·selftest 무회귀)까지 했으나, `run.sh` 는 **D-050 에서 Codex 저자로 확정된 파일** — 커밋 시점에 거버넌스 분류기가 자기작성·자기머지로 차단(정당). **우회하지 않고 코드는 원복**, 스펙을 `collab/answers/A-0017.md` 로 Codex 에 이월(비차단·TASK-023 세션 동반 권장·~10분). 이번 머지는 **문서·표시정합만**: `kit/README.md` 함정 2건("Codex 구현 대기" 명시)·E2E 결과 절 + `TASKS.md` TASK-022b ☐→☑(D-048~050) + 본 결정 + A-0017.
**교훈 기록**: 같은 세션에서 같은 파일로 두 번째 차단 — "안내 echo 정도는 괜찮겠지"도 게이트-인접 파일이면 예외 없음이 이 하네스의 규칙이고, 분류기가 그걸 정확히 집행했다(dogfooding 실증).

## D-050 (2026-07-15) TASK-022b R-1 보정 재제출 재리뷰 — **통과 · Claude main 머지 (TASK-022b 완결 · 배포용 킷 v0 수용)**
**대상**: 브랜치 `claude/2026-07-15-kit-draft` — 보정 델타 `f1bf533`(fix) + `39c2285`(docs). 통과분 `00bde19`·`88a7d4e` 는 D-049(A-0016) 멱등성대로 재론 없음 — 델타만 재리뷰.
**판정: 통과 — 비민감 → Claude `main` 머지·push 완료. TASK-022b 완결, 킷 v0(kit/) main 수용.**
**R-1(D-049) 해소 확인**: A-0016 처방 ①②** 모두 문자 그대로 채택**.
- **① watcher fd 분리 ✓**: `kit/run.sh` L87 `) >/dev/null 2>&1 & watcher=$!` — 고아 `sleep` 의 호출자 파이프 write-end 점유 제거. 타임아웃 감지(마커파일·TERM/KILL)는 fd 무관이라 보존(`gate-timeout` 케이스 PASS 로 실증).
- **② 파이프-지연 회귀가드 ✓**: `run_pipe_latency_case`/`pipe-capture-no-timeout-delay` — 파이프 캡처 + **`ACGH_GATE_TIMEOUT_SECONDS=30` 명시**(timeout=1 가림 우회 차단) + `rc=0` + 벽시계 `<10s` 단언, 집계 게이팅 정상 편입.
**심층·적대 재검증**: 진입점 **6/6 PASS**(전체 4.2s)·selftest **PASS**(77+mutation127). **fresh(픽스처 밖)**: 합성 repo·기본 60s 타임아웃 파이프 캡처 → **elapsed 0s·pass·exit 0**(D-049 실측 60s 대비 회귀 소멸). **음성검증(rig-and-revert)**: fd 분리 원복 → 신규 가드 **단독 FAIL(5/6, `exit=0 elapsed=31s expected=<10s`)**·기존 5케이스는 여전히 PASS(기존 스위트의 사각 재확인) → 가드 load-bearing 실증. elapsed 31s≈timeout 30s = 타임아웃값 종속성 재확인.
**보수적 개발(§1) OK**: 델타 = run.sh 1줄·진입점 테스트 +21줄·공동소유만. 판정 조립·우선순위·`--policies`·게이트 Python·정책·dev 트리 무접촉(A-0016 "손대지 마라" 준수). scope-creep 없음.
**잔여(비차단)**: O-a(문구)·O-b(bash3.2 관용구)·O-c(실패 시 비-YAML 카드)는 차기 킷 정비 권장 유지, O-d(sync 체크섬)는 **MVP-2 킷 재생성 AC 채택**(D-049). A-0016 의 "재제출 전 origin/main merge" 미이행은 머지자 충돌해소로 흡수(내용 결함 아님).
**머지(D-007)**: 비민감(신규 kit/ 폴더·기존 게이트/정책/dev 무변경 — D-047 판정 유지·정산/인증·인가/암호화/migration/infra 무관) → 구현자(Codex 델타)≠머지자(Claude)로 Claude 머지. 병합 충돌 3건(decisions/handoff/summaries)은 양측 보존·시간역순 재배열로 해소.
**상세**: `review-notes.md` TASK-022b R-1 재리뷰(D-050) 절 · `collab/answers/A-0016.md` §해소. **멱등성**: `f1bf533`·`39c2285` 재처리 금지. **다음**: MVP-2 본선(TASK-023 콜그래프 빌더) 재개.

## D-049 (2026-07-15) TASK-022b 킷 최종리뷰 — **보정요청(1건 🟡 블로킹) · 코드 머지 보류**
**대상**: 브랜치 `claude/2026-07-15-kit-draft`(헤드 `88a7d4e`) — 킷 초안 `8269dda`(Claude, D-047) + main 병합 `f39d6cf` + **Codex 교차감사·보강 `00bde19`**(D-048·A-0015 — D-048 은 미머지 브랜치의 decisions.md 에 존재). 역할역전 계약(D-047): verdict-affecting 셸 델타를 Codex 가 저자 → Claude 가 최종리뷰.
**판정: 보정요청(R-1) — 코드 브랜치 머지 보류, 리뷰기록만 main 머지.**
**통과 확인(실증)**: ①스냅샷 충실성 — kit 게이트 13종=manifest 명시 13종, 12/13 dev 동일·`extract-gov-annotations` 구버전+`extract-sinks` 부재는 manifest 선언 범위(`0.1-mvp1.5`, TASK-022=MVP-2 제외) 그대로라 결함 아님. 정책 5종·템플릿 dev 동일. selftest 는 심볼릭 링크로 **킷 게이트를** 검증(dev 오지시 없음). ②판정 조립 — 차단>승인>통과, L2·메타 게이트는 exit {0,2}만 방출이라 allowed="0 2" 로 정당한 차단의 강등 구멍 없음, **불변원칙("2·3층 자동차단 금지")을 구조적으로 보장**. ③분석실패 정직성 — fresh 적대입력으로 게이트부재·Traceback·타임아웃·비정상 exit1 위장·비-range 전부 `tool_owner` 포함 승인요구 실증(ADV1~3), **차단+분석실패 동시 → 차단 우선(exit 1)** 실증(ADV4). ④intent 부재 → 증거게이트 catch-all 이 fail-closed **차단 카드(exit 1)** 방출 = manifest 계약 일치 실증(ADV6). ⑤선언 수치 전부 재현 — selftest 77/77·진입점 5/5·mutation 127·dev 스위트 80/80(브랜치). ⑥음성검증 — 정규화 제거→gate-timeout FAIL·우선순위 뒤집기→target-policy-frozen FAIL = 테스트 load-bearing.
**🟡 R-1 블로킹**: `run_gate()` watcher 서브셸의 자식 `sleep` 이 kill 후에도 생존하며 상속 stdout(호출자 파이프)을 점유 → **파이프 캡처 호출(CI 스텝·spine `$(…)`)마다 EOF 가 GATE_TIMEOUT(기본 60s) 전액 지연**. 실측: 기본값 60s 소요(게이트 실행은 1~2s)·타임아웃 3s 시 4s 로 비례. `00bde19` 가 도입한 운영 회귀이며 기존 진입점 테스트는 전 케이스 `ACGH_GATE_TIMEOUT_SECONDS=1` 이라 가려짐(회귀가드 부재). 판정·exit 는 전부 정확(거버넌스 구멍 아님)하나 킷의 1차 사용경로(CI) 실측 열화 + 가드 부재라 보정요청. **보정 = ① watcher fd 분리 1줄**(`) >/dev/null 2>&1 & watcher=$!` — 사본 실증: 지연 소멸·타임아웃 감지 보존) **② 파이프-지연 회귀가드 테스트 1건**(큰 타임아웃값 명시로 가림 방지).
**비차단**: O-a run.sh "의도이탈 층은 생략" 문구가 실동작(fail-closed 차단)과 불일치 — 정정 권장. O-b bash 3.2+intent 부재 = 빈배열 `set -u` 즉사(방향은 fail-closed·카드 없음) — 관용구 or bash≥4 명시 권장. O-c 분석실패 시 카드가 비-YAML. O-d(=A-0015 O-1 승인) sync 체크섬 검증은 **MVP-2 킷 재생성 AC 채택**.
**보수적 개발(§1) OK**: 델타 = kit 진입점·selftest·진입점테스트·README 만. 기존 게이트 Python·정책값·dev 트리 무접촉. scope-creep 없음.
**상세**: `collab/answers/A-0016.md`. **멱등성**: `00bde19`·`88a7d4e` 재처리 금지 — 재제출은 보정 델타만 재리뷰.

## D-048 (2026-07-15) TASK-022b 킷 교차감사·보강 완료 — Claude 최종리뷰 대기

Codex가 D-047의 역할 역전 계약에 따라 `kit/run.sh` 판정 조립을 감사하고 보강했다(구현 `00bde19`, 상세 A-0015). 기존 `blocked > approval_required > pass` 우선순위는 게이트별 exit 계약과 일치함을 확인했다. 게이트 부재·Traceback·타임아웃·비정상 종료를 분석 실패로 분리해 `tool_owner` 포함 승인요구로 fail-closed 처리하고, 비-range 입력의 조용한 누락도 승인요구로 바꿨다. `--policies <dir>`로 대상 저장소의 민감존·라우팅·능력 정책을 일관 적용한다. fresh 적대입력 5/5와 전체 selftest(77/77 + mutation 127건) 통과. **상태: Codex 교차감사 완료, Claude 최종리뷰·main 머지 대기.** sync의 내용 드리프트 검증은 O-1 차기 권장으로 기록하며 이번 2갭 보강 범위에는 포함하지 않는다.

## D-047 (2026-07-15) 배포용 킷(kit/) 초안 — 브랜치 `claude/2026-07-15-kit-draft` · Codex 교차리뷰 대기(TASK-022b)
**맥락**: 형 계획("MVP 달성마다 키트 반영")대로 완료 MVP-0/1/1.5 를 배포 가능한 자립형 킷으로 스냅샷. 핵심 요구 = **검사기능(게이트) 누락 금지**. 인벤토리로 확인한 결정적 사실: `generate-change-evidence` 는 3축(의도·경로·@gov함수)만 조립하고 **`check-new-capabilities`(2층)·`check-policy-change`(메타)는 누락**(missing_orchestrator) → 킷 `run.sh` 가 이 둘을 명시 추가 조립해 메움.
**산출**: 브랜치 `claude/2026-07-15-kit-draft`(kit/ 만 최신 main 위·충돌 없음) — `run.sh`·`manifest.yaml`(게이트 13종 명시)·`sync-from-dev.sh`(MVP마다 재생성+dev수==kit수 누락검증)·`bootstrap.sh`·`selftest.sh`·gates13(co-located)·policies·templates·tests·schemas·README.
**적대 검증(D-046 시절 워크플로 5/5·rig-and-revert)**: 누락0(dev13==kit13)·능력게이트 load-bearing·정책게이트 load-bearing·frozen차단/clean통과·selftest 77/77+co-location 필수성. 전부 실증.
**🔴 상호견제 후속 = TASK-022b**: `run.sh` verdict-combine 은 **Claude 작성** → main 머지 직전 거버넌스 분류기가 자기작성·자기머지를 실제 차단(2026-07-15). 정식 절차로 **Codex 가 교차리뷰 + 아래 2갭 보강 구현**(TASK-022b): ①분석실패 정직성(게이트 크래시≠판정 구분·ADR-001 D4) ②`--policies` 대상 repo 정책 오버라이드. 이 2개는 D-046 시절 구현했으나(7e1bfe8) 브랜치 재작성 중 미푸시로 **유실** → 재구현을 Codex 몫으로(verdict-affecting 셸을 Codex 가 저자 = 상호견제 정합).
**상태**: 킷 Draft·브랜치 대기(원본 run.sh 상태). TASK-022b 통과·보강 후 Claude 가 main 머지. **비민감**(신규 폴더·기존 게이트/정책 무변경). 이전 D-045/D-046 번호가 TASK-022 sink 리뷰에 배정돼 이 결정은 D-047(이전 세션이 임시로 킷을 D-045/046 으로 적었던 건 유실됨).

## D-046 (2026-07-15) TASK-022 R-1 보정 재제출 재리뷰 — **통과 · Claude main 머지 (TASK-022 완결)**
**대상**: 브랜치 `codex/2026-07-15-task022-sink-registry` — 보정 델타 `f18cc32`(+ docs `95b4399`). 원 구현 `4651ea6`·헤드 `44380c0` 는 D-045(A-0013)에서 재론 불필요.
**판정: 통과 — 비민감 → Claude `main` 머지·push 완료. TASK-022 완결.**
**R-1(D-045) 해소 확인**: A-0013 요청 보정 ①②(제어흐름 분리 + 상설 회귀 픽스처) **모두 채택**.
- **① 제어흐름 분리 ✓**: `merge_gov_annotations` 의 sink 누적(`if annotation.get("sink"): merged["sink"]=True`)을 강도병합 `if annotation_is_stronger: … else:` **밖 top-level if 로 분리** → `else` backfill 이 `annotation_is_stronger` 에만 재결합. 약한 `sink=true` annotation 의 reason/owner 유실 폐쇄, sink 멤버십 정확성은 유지.
- **② 상설 회귀 픽스처 ✓**: `tests/fixtures/gov-annotations/multi_sink.py`(다중 @gov: 강한 frozen 무-reason + 약한 protected `sink=true`+reason/owner) + 케이스 `gov-annotations-multi-sink-metadata`(신규 harness 단언 `annotation_metadata`)가 병합 후 `sink:true`·`reason:PII bulk export`·`owner:security-reviewer` 동시 단언. §2B 데코레이터 적대세트 상설화.
**심층·적대 재검증**: `run-tests.sh` **80/80 PASS**. **음성검증(rig-and-revert)**: 픽스를 버그형태로 원복 시 신규 케이스 **단독 FAIL(79/80)**·게이트 출력 `reason=None owner=None`(R-1 정확 재현) = 회귀 픽스처 load-bearing 실증. **fresh 적대입력 3종(픽스처 밖)**: ADV1(3중@gov·최약에만 sink+메타)→전부 보존 / ADV2(최강 sink 무reason·약한쪽 메타)→backfill 보존 / ADV3(sink 전무)→하위호환 무회귀. **하류(TASK-024 라우팅)**: 유실되던 owner(§5 라우팅)·reason(감사카드) 보존 확인 → fail-safe 강등 구멍 폐쇄.
**보수적 개발(§1) OK**: 델타 = `extract-gov-annotations.py`(2줄 이동)·`cases.yaml`(+14)·`run-tests.sh`(+11)·신규 픽스처·공동소유. `policies/*`·Claude 소유·`extract-sinks.py`·sinks 픽스처 무접촉. scope-creep 없음.
**잔여(비차단)**: R-2(frozen-auto-sink 테스트의 라이브 `policies/sensitive-zones.yaml` 결합)는 Codex 가 **TASK-023 fixture 가드 G-sink-1 이월**(A-0013 허용) — loud-fail 이라 구멍 아님·**TASK-023 착수 시 G-sink-1 결정적 고정 처리**. O-1(이중 sink)·O-2(`normalize_hops` bool)는 TASK-024 AC 고려/인지.
**상세**: `collab/answers/A-0014.md`. 근거·실증 전문: `review-notes.md` TASK-022 R-1 재리뷰(D-046) 절. **멱등성**: `f18cc32`·`95b4399` 재처리 금지. **머지(D-007)**: 비민감(하네스 sink 추출·판정 무변경 D-044·게이트 계열 Claude 머지 선례 D-034·039·040·042·043) → 구현자≠머지자로 Claude 머지.

---

## D-045 (2026-07-15) TASK-022 sink 등록 스키마 리뷰 — **보정요청**(@gov 병합 else 오결합 · 코드 머지 보류)
**대상**: 브랜치 `codex/2026-07-15-task022-sink-registry`(헤드 `44380c0`, 구현 `4651ea6`) — 신규 게이트 `.harness/gates/extract-sinks.py`(403줄) + `extract-gov-annotations.py` sink 파싱 확장(+18줄) + fixtures `tests/fixtures/sinks/` + tests(cases +71·run-tests +50). **MVP-2 첫 게이트(sink 등록·판정 무변경)** — 설계 `docs/mvp2-impact-tracing-design.md` §3.1(D-044).
**판정: 보정요청(1건 블로킹) — 코드 브랜치 머지 보류, 리뷰기록만 main 머지.**
**심층·적대 리뷰 결과**:
- **통과(실증)**: `run-tests.sh` 79/79. AC #1 파싱·**하위호환 무회귀**(비-sink 경로 행동보존 실증), #2 frozen 자동 sink(settlement 발화·auth 비발화), #3 registry 스키마(§3.1 — missing/unresolved/invalid-maturity 오류처리·조용한무시 없음·enforcing 보수), #4 일반@gov·protected 비-sink, #5 결정성 — fresh 적대입력으로 직접 실증. 보수적 개발 OK(`policies/*`·Claude 소유 무접촉; gov-gate 확장은 AC #1 인가 범위).
- **🟠 R-1 블로킹**: `merge_gov_annotations` 에 sink 블록이 `if annotation_is_stronger: … else:` **사이에 삽입**돼 `else` 가 `if annotation.get("sink")` 에 **오결합**. 결과 = sink=True 인 (약한) annotation 의 **reason/owner backfill 스킵** → sink `owner`(§5 라우팅 대상)·`reason`(감사카드) **조용히 유실**. **적대 실증**: 다중 @gov 데코레이터(약한 쪽 `sink=true`+owner) → 헤드 출력 `owner=None`. **음성검증**: else 를 `annotation_is_stronger` 로 원복 시 owner 복원 = 오결합 load-bearing. sink **멤버십은 항상 정확**(top-level if)이라 누락/오탐은 없으나 라우팅 메타 손실 = **거버넌스 영향 논리결함** → 비차단 불가(CLAUDE §2B). 이 결함은 §2B 상설 적대세트("데코레이터/오버로드") 범주인데 **회귀 픽스처 부재** → 보정 시 다중-@gov 회귀 케이스 신설 요구.
- **🟡 R-2 비차단(권장)**: `sink-registration-defaults` 테스트가 `--sensitive-zones` 기본값(라이브 `policies/sensitive-zones.yaml`)에 결합 → frozen 자동 sink 기대값이 라이브 정책의 settlement frozen 유지에 의존. **실증**: 대체 zones(auth=frozen) 주입 시 frozen sink 뒤바뀜. **TASK-021 G-broad-1(D-042/D-043)** 이 닫은 라이브결합 부류 — loud-fail 이라 비차단이나 fixture-local zones 로 결합 끊기 권장(또는 TASK-023 fixture 가드 G-sink-1 이월).
- **비차단 관찰**: O-1 frozen+@gov(sink) 동시 = `gov:`·`frozen:` 이중 sink(maturity 상이) → TASK-024 강한 maturity 채택 고려. O-2 `normalize_hops` bool 통과.
**보정요청 상세**: `collab/answers/A-0013.md`. 근거·실증 전문: `review-notes.md` TASK-022(D-045) 절. **멱등성**: `4651ea6`·`44380c0` 재처리 금지 — 재제출은 보정 델타만 재리뷰. **머지 판정(D-007)**: 리뷰기록(A-0013·decisions·review-notes·handoff)만 main 머지, **코드 브랜치는 보정까지 보류**.

---

## D-044 (2026-07-13) MVP-2 영향추적(sink 역도달성) 설계 착수 — 방향 확정 (형 승인) · 설계문서 Draft
**맥락**: MVP-1.5 코드·서류 완결 후 로드맵 갈림길에서 형이 **정공법(MVP-2)** 선택. MVP-2 = 간접 영향 추적층(sink 이 의존하는 상류 함수 수정을 현행이 완전 무탐지하는 구멍을 메움 — "다운로드에 @gov 달아도 `check_permission()` 수정은 못 잡는다"의 답을 "예, 승인요구로"로 전환).
**형 확정 결정(2026-07-13)**:
- **D-044a @gov↔sink = 레벨 차등 하이브리드**(TASKS.md L256 🔴 미결 항목 해소): frozen 존 함수 = **자동 sink**, protected/@gov = `@gov(sink=true)` **옵트인**, 일반 @gov·protected 는 **sink 아님**(직접수정 게이트가 커버). 근거: 비싸고 과탐 잦은 콜그래프를 소수 고가치에만 걸어 신호대잡음 보존. ①안(@gov 전부 자동 sink)은 공통유틸 과탐 폭발로 기각.
- **D-044b 최소 스코프부터 래칫**: 단일 diff · N=1홉 시작 · **shadow 성숙도로 시작** · 차단 절대 금지(승인요구 상한). cross-commit 누적·비-Python artifact·동적 완전복원은 **명시 비범위**(설계 §7).
**산출**: `docs/mvp2-impact-tracing-design.md` + `TASKS.md` TASK-022~025(sink 등록→콜그래프 빌더→역도달성 게이트→과탐통제·고정적대세트) AC.
**2026-07-13 형 §10 4항 전부 승인 → 설계 Accepted.** sink-registry 스키마(§3.1) Claude 확정분 추가. **다음 = Codex TASK-022 착수**(sink 등록 스키마 구현·판정 무변경). 이후 023→024→025 순차.
**정직 리스크 기록**: 파이썬 콜그래프는 원리적으로 sound+precise 불가(동적 디스패치·getattr) → 근사만 가능. 설계는 "정적 해석호출은 잡고 못 푸는 건 coverage 갭으로 노출"(ADR-001 D4) + shadow 시작 + N 통제로 과탐 방어. 이 층은 하네스 최대 과탐 리스크 지점임을 명시.

## D-043 (2026-07-13) TASK-021 G-broad-1 follow-up — broad-intent 픽스처 라이브-repo 결합 제거 — **통과 · Claude main 머지**
대상: 브랜치 `codex/2026-07-13-task021-broad-fixture` — `2395c6e`(test) · 헤드 `82d598b`(docs). **멱등성**: `2395c6e`·`82d598b` 재처리 금지. **범위 = 테스트 하네스만**(D-042 에서 비차단 차기 AC 가드로 남긴 G-broad-1: `broad-intent-*` 회귀 픽스처가 라이브 repo 최상위 디렉토리 수에 결합돼 디렉토리 추가 시 87%→77% 로 뒤집혀 깨지던 불안정성 제거).
**판정 = 통과, `main` 머지·push 완료. 더 할 일 없음.**
**무엇을 바꿨나**: `run-tests.sh` 의 `check-change-intent` 케이스가 `fixture_dir` 를 받으면 기존 `prepare_function_mapping_fixture` 헬퍼(재사용·재발명 없음)로 **격리 git repo** 를 만들어 그 `base..head` 에서 게이트를 실행. `broad-intent-root/coverage/normal-wide` 를 고정 8개 최상위 디렉토리(`.harness app collab docs policies scripts summaries templates`) 픽스처로 전환하고 `scope_top_level_dir_count`·`scope_coverage_percent`·`scope_covered_top_level_dirs` 기대값을 100/87/75% 로 명시 고정. **게이트 판정 로직(`check-change-intent.py`)·`policies/*`·Claude 소유 전부 0-diff 확인**(구현자가 판단 로직 동결).
**설계 정합(왜 이게 결합을 끊나)**: 게이트의 `repo_top_level_dirs()` 가 `git ls-tree -d <base_ref>` 를 **cwd 에서** 실행 → 격리 repo 안(`cd work_dir`)에서 돌리면 **분모(top_level_dir_count)가 픽스처 base 트리에서 나온다**. 라이브 repo 가 9번째 최상위 디렉토리를 얻어도 이 회귀는 불변. 부가효과: 실 CI 경로(git diff ref)를 그대로 재현 = 예전 name-status 파일(파일존재→HEAD 폴백으로 라이브트리 참조)보다 프로덕션 충실도↑.
**적대 검증(fresh·픽스처 밖·격리 worktree)**: coverage 픽스처 repo 를 손으로 빌드해 게이트 실행 → `top_level_dir_count:8`(픽스처 셋에 **`app` 포함** — 라이브 repo 엔 `app` 없고 `tests` 존재) `coverage_percent:87`·`threshold:80`·exit 2·`changed_files:['docs/release-notes.md']`. **분모의 dir 셋이 라이브 repo(`tests` 포함)가 아니라 픽스처(`app` 포함)에서 나옴을 실증 = 결합 소멸(R-2/G-broad-1 폐쇄).** coverage 픽스처는 R-1 공격값 `broad_scope_threshold_percent:101`+중첩 `scope_policy` 보존 → 상설 R-1 회귀도 유지(threshold 여전히 고정 80, 101 무시).
**음성검증(rig-and-revert)**: ① `scope_coverage_percent` 87→88 변조 → `broad-intent-coverage` **단독 FAIL**(got 87), ② `scope_covered_top_level_dirs` 의 `templates`→`BOGUS` 변조 → `broad-intent-root` **단독 FAIL**, 원복 후 PASS = 신규 단언이 load-bearing(항상-green 아님). 신규 단언은 분자(covered dirs)+분모(count)+percent 를 함께 고정해 예전보다 **더 엄격**(더 많은 회귀 포착).
**보수적 개발(§1)**: 델타 = `run-tests.sh`(fixture_dir 분기 +12줄·검증 단언 +21줄) + `cases.yaml`(fixture_dir 전환·단언) + 신규 픽스처 트리 + 공동소유(handoff·summaries). 무관 리팩터·포맷·이름변경 없음·scope-creep 없음·헬퍼 재사용. `run-tests.sh` **77/77 PASS**·`git diff --check` clean·`py_compile`·`bash -n` OK(격리 worktree 재현).
**비차단(O-1·신규)**: 기존 `tests/fixtures/broad-intent-*/name-status.txt` 3파일이 이제 **미참조(dead)** — 무해(어떤 케이스도 안 봄)·거버넌스 구멍 아님. 차기 정리 시 삭제 권장(보정 필수 아님).
**머지 판정(D-007)**: 순수 **CI 테스트-하네스 안정화**(게이트 판단 로직·정책 무접촉·verdict 파이프라인 미연결·자동차단/채택 없음·정산·인증/인가·암호화·DB migration·infra 전부 무관) → CLAUDE.md §3 **비민감**. TASK-014~021 게이트/픽스처 계열 Claude 머지 선례(D-035~D-042). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push. G-broad-1 마감.** 상세: `review-notes.md` TASK-021 G-broad-1(D-043) 절.

## D-042 (2026-07-13) TASK-021 R-1 보정 재제출 재리뷰 — **R-1 해소 확인 · 통과 · Claude main 머지 (TASK-021 완결)**
대상: 브랜치 `codex/2026-07-11-task021-broad-intent` — 보정 `1c08afa`(fix) · 헤드 `c4655ad`(handoff). **멱등성**: `616ff43`·`1b954c3`·`1c08afa`·`c4655ad` 재처리 금지. **재제출은 R-1 보정 델타만 재리뷰**(D-041/A-0012 계약대로 검출 엔진은 재론 없음).

**판정: 통과 · Claude main 머지.** D-041 R-1(🔴 자기-무력화)이 **권장 보정(change-intent 오버라이드 제거)** 으로 정확히 닫혔다.

- **R-1 해소 ✓**: `load_intent()` 가 이제 `broad_scope_threshold_percent` 를 **change-intent 에서 읽지 않고** 고정 `DEFAULT_BROAD_SCOPE_THRESHOLD_PERCENT = 80` 만 쓴다(gate line 61). 임계값을 읽던 두 조회 키(`intent.get(...)` · `scope_policy.get(...)`) 전부 제거 → **author 통제 경로 부재**(grep 확인: threshold 세팅점 line 61 유일, 소비점 164·180·190 은 전부 이 상수 참조). AC "기본 80" 그대로 충족.
- **적대 재검증(fresh·픽스처 밖·합성 repo 로 라이브트리 결합 차단)**: ADV1 재현 — 합성 8-디렉토리 repo 에서 `broad_scope_threshold_percent: 101`(+`scope_policy` 중첩) 선언 + 최상위 8개 개별 나열 → **threshold 80(공격값 101 무시)·coverage 100%·`top_level_coverage`·approval_required/exit 2**. 자기-무력화 스위치 소멸.
- **음성검증(rig-and-revert, load-bearing 실증)**: line 61 을 예전 author-통제 코드로 되돌린 rigged 사본에 동일 공격 → **threshold 101·`pass`/exit 0 으로 회귀**(구멍 재개방). 즉 이 한 줄 델타가 R-1 을 닫는 load-bearing 변경임이 실증됨(항상-green 아님).
- **회귀 고정**: `broad-intent-coverage` 픽스처에 공격자 선언값 101(+중첩)을 심어, 이 태스크의 상설 회귀가 R-1 공격입력을 그대로 재현(threshold 무시·`approval_required` 기대). `run-tests.sh` **77/77 PASS** · `py_compile` OK · `git diff --check` OK.
- **보수적 개발 ✓**: 보정 델타 = 게이트 1줄(±6/1) + 픽스처 3줄 + 공동소유(handoff·summaries)뿐. **`policies/*`·Claude 소유(docs·TASKS·decisions·answers·templates) 무접촉**·scope-creep 없음.
- **R-2 (🟡 비차단) 잔존 → 차기 AC 가드**: 회귀 픽스처가 여전히 라이브 repo 트리(현재 8 top-level dir, 7개 나열=87%)에 결합. 최상위 디렉토리 추가 시 7/9=77%<80 로 테스트가 뒤집힘. 프로덕션(실 diff ref)은 결정적이라 거버넌스 구멍 아님·비차단이나, 픽스처가 top-level 집합을 결정적으로 고정하도록 **차기 AC 가드(G-broad-1)** 로 명시(§2B 대로 비차단으로 안 흘림). — 보정 필수 아님, TASK-021 완결에 지장 없음.

**민감도**: 거버넌스 메타-게이트(change-intent 범위). 격상은 **approval_required(2층)** 뿐 — **1층 자동차단 권한 없음**(불변원칙 §4 준수). 정산/인증·인가/암호화/DB migration/infra 무관. → **비민감**(TASK-018·019·020[D-034]·016[D-039]·017[D-040] 동일 게이트 계열 Claude 머지 선례). **D-007**: 리뷰 통과+비민감 → 구현자(Codex)≠머지자(Claude)로 **Claude 가 코드 브랜치를 `main` 머지·push**. 상세: `review-notes.md` TASK-021 R-1 재리뷰(D-042) 절 · `collab/answers/A-0012.md` §해소.

## D-041 (2026-07-13) TASK-021 광역 의도선언 격상 `check-change-intent` — **보정요청 (1건 · 🔴) · 코드 머지 보류**
대상: 브랜치 `codex/2026-07-11-task021-broad-intent` (헤드 `1b954c3` · 구현 `616ff43`). `check-change-intent.py` +109줄(루트 glob 정규화·top-level 커버리지·`scope_too_broad`→approval_required 격상) + `tests/cases.yaml` 3케이스 + 러너 assert + 픽스처 3종. **멱등성**: `616ff43`·`1b954c3` 재처리 금지. 재제출은 **R-1 보정 델타만** 재리뷰.

**판정: 보정요청.** 검출 엔진은 fresh 적대입력·음성검증으로 실증 통과했으나, **임계값 N 의 신뢰경계** 1건이 거버넌스 구멍을 낸다.

- **통과(재론 불필요)**: AC#1(a) 루트 glob 검출(`*`·`**`·`./**` 정규화 동치, **임계값 독립** — ADV3 실증) / AC#1(b) 커버리지 검출은 **기본 임계값 하에서** 정상(ADV2: 8개 나열 → 100%·approval_required) / AC#2 오탐 억제(normal-wide 75%<80 → pass) / AC#3 하위호환(TASK-001 로직 무변경·빈 diff pass 유지·forbidden 우선·too_broad 는 approval_required 로만 격상, blocked 승격 없음) / `run-tests.sh` **77/77 PASS** / 보수적 개발(policies·Claude 소유 무접촉·scope-creep 없음).

- **R-1 (🔴 · 보정 필수) — 자기-무력화**: AC#1(b) 는 "N 은 정책값"인데, 구현은 N 을 **피검자 자신의 change-intent.yaml**(`load_intent`: `intent.get("broad_scope_threshold_percent")` — `change_intent` 블록 하위)에서만 읽는다. 정책파일 경로 부재·클램프 부재. → 작성자가 같은 파일에 `broad_scope_threshold_percent: 101` 을 넣고 최상위 디렉토리를 개별 나열(리터럴 `*`/`**` 회피)하면 **커버리지 100%인데도 `pass`/exit 0**(ADV1 실증). TASK-021 이 막으려는 "선언을 무의미하게 만들기"를 한 단계 위로 옮겨 재현 = 거버넌스 목적에 **직접 구멍**(§2B 필수질문 → 비차단 금지). 보정: change-intent 오버라이드 제거(고정 기본 80 유지=AC "기본 80" 충족) 또는 Claude 소유 정책파일에서 N 읽기. **클램프 ≤100 만으론 불충분**(threshold=100+7/8 나열=87%<100 통과) — author 통제 자체를 끊어야 함.

- **R-2 (🟡 · 비차단 → 차기 AC / 보정 시 동봉 권장)**: 회귀 픽스처가 라이브 repo 트리에 결합. name-status 파일 입력 → `diff_base_ref` HEAD 폴백 → `repo_top_level_dirs` 가 실 repo 최상위 디렉토리를 셈. `broad-intent-coverage`(7개 나열)는 현재 7/8=87% 통과지만 최상위 디렉토리 추가 시 7/9=77%<80 → verdict pass 로 뒤집혀 **무관한 repo 성장에 회귀 테스트가 깨짐**. 프로덕션(실 diff ref)은 결정적이라 구멍은 아님 → 비차단. 픽스처가 top-level dir 집합을 결정적으로 고정하도록 권장.

**D-007 흐름**: 코드 브랜치 **머지 보류**. 리뷰기록(D-041·`A-0012`·`review-notes.md`)은 `main` 머지(다음 세션·Codex 가 봄). `handoff-log.md` 맨 위에 `Claude → Codex … (보정요청)` 신호 남김(새 태스크 오인 방지). 상세: `collab/answers/A-0012.md`·`review-notes.md` TASK-021(D-041) 절.

## D-040 (2026-07-11) TASK-017 뮤테이션(음성검증) 자동화 `tests/mutation-check.sh` — **통과 · Claude main 머지**
대상: 브랜치 `codex/2026-07-11-task017-mutation-check` (impl `459a519` · 핸드오프 `4bd00c0`). 신규 `tests/mutation-check.sh`(194줄) + `tests/run-tests.sh` 선택실행/그룹요약/capability_ids·levels 검증(+34) + metamorphic·negative-corpus 케이스 6종 + 픽스처 8파일 + README 1줄. **멱등성**: `459a519`·`4bd00c0` 재처리 금지.

**수용기준 실증 (전부 직접 실행·적대 검증)**:
- **AC#1·#2 (기대값 변조→반드시 FAIL / 죽은 테스트 목록·exit≠0)**: `bash tests/mutation-check.sh` → 121건 변조 전부 감지·dead 0·PASS. **음성검증(rig-and-revert, load-bearing 증명)**: ① `mutate_verdict` 를 no-op(identity)로 변조 → verdict 보유 48케이스 전부 dead 로 보고·`FAIL mutation-check` / ② `mutate_exit_code` 를 no-op 로 변조 → **exit 1**·`good:exit` 등 dead 보고. 원복 후 재-PASS. ⇒ 검출 루프가 실제로 죽은 테스트를 잡는다(항상-green 아님).
- **AC#3 (verdict·exit_code 변조 지원·결정적·원본 무변경)**: 두 필드 mutator 존재(121 변조). 결정론(파일순 순회·`sort_keys=False`·무작위 없음). **원본 무변경**: 모든 변조를 `tempfile` repo 복사본에서 수행 → 실제 repo 파일 구조적으로 미접촉(복원 성패와 무관하게 안전) = AC 요구의 *강한* 충족.
- **AC#4 (단일 진입점)**: `bash tests/mutation-check.sh` 하나.
- **AC#5 (정책 변조)**: maturity fixture `app/enforcing/**` protected→watched 하향 → `maturity-zone-enforcing-approval` FAIL 확인·원본 복원. 실행서 "failed after protected->watched policy mutation" 확인 = 정책이 판정을 지배함 실증.
- **AC#6 (metamorphic 3종)**: (a)import 별칭 `subprocess as sp` (b)공백·주석 삽입 (c)함수 정의 순서 이동 — 3케이스 모두 `subprocess_exec/protected`·`errors:[]` 동일 판정 pin. 요구 (a)(b)(c) 정확 대응. 실제 정책 대비 3/3 PASS.
- **AC#7 (negative corpus 별도 그룹)**: `negative-corpus` 그룹 3종(무신호 source·무해 python 변경·docs-only) 무경고 검증 + 러너가 `Group negative-corpus: 3/3 PASS` 별도 표기·`TEST_CASE_GROUP=negative-corpus` 선택 실행. alert-fatigue 방어 체계 증거.

**적대·하류 검증**: 케이스명 74/74 유니크 → mutation-check 의 index-변조 vs name-선택 정렬 안전(중복명이면 오분류 가능하나 부재). metamorphic 케이스의 `capability_ids`/`capability_levels` 는 mutation-check 변조 대상 아님(AC#3 "최소 verdict·exit_code")이나 정상 러너 assert_equal 로 load-bearing·비어있지 않은 값 pin(비공허). 전체 스위트 74/74 PASS(default 68·metamorphic 3·negative 3), `bash -n` OK.

**보수적 개발(§1)**: 순수 테스트 하네스·픽스처·README 실행예시 1줄만 변경. **정책파일(`policies/*`)·게이트 판정로직(`.harness/gates/*`)·Claude 소유(docs·TASKS·decisions·answers·templates) 전부 무접촉**. `run-tests.sh` 선택실행은 env 없으면 기존 전체스위트(하위호환). scope-creep 없음.

**머지 판정(D-007)**: mutation-check = **CI 테스트-품질 도구**(verdict 파이프라인 미연결·자동차단/자동채택 없음·정산/인증·인가/암호화/DB migration/infra 무관·1층 자동차단 권한 없음) → CLAUDE.md §3 **비민감**. TASK-005~016·018~020 테스트·게이트 계열 Claude 머지 선례(D-020~D-039). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push**.

**비차단 관찰(O-1, MVP-2 / 차기 AC 가드 후보)**: `main()` 의 "Original files unchanged" 해시 검사는 `ROOT`(실제 repo) 파일을 대상으로 하나 모든 변조는 `tempfile` 복사본에서만 일어나 ROOT 는 구조적으로 절대 쓰이지 않는다 → **이 라인은 공허(vacuous)**·in-repo 복원 실패를 검출할 수 없다. 다만 실제 repo 안전은 copy 설계로 *더 강하게* 보장되므로 **거버넌스 구멍 아님**(비차단 정당). 차기: 복원검증을 원하면 temp-copy 파일 해시를 검사하거나 오해 소지 라인 제거. (in-repo 복원 실패 시엔 후속 metamorphic/negative 그룹이 스퓨리어스 FAIL 로 간접 노출되어 false-pass 위험도 없음.)

상세: `review-notes.md` TASK-017(D-040) 절.

## D-039 (2026-07-11) TASK-016 R-1 보정 재제출 재리뷰 — 하류 회귀 해소 확인 · **통과 · Claude main 머지** (TASK-016 완결)
대상: `codex/2026-07-11-task016-dynamic-capabilities` · 보정 fix `e839fe9` · 헤드 `dec42e9` (선행 D-038/A-0011). 재리뷰 범위 = **R-1 보정 델타만**. 추출기 계층 AC #1~7 은 D-038 에서 실증 통과·재론 없음. 멱등성: `6aeb513`·`47db5c5`·`e839fe9`·`dec42e9` 재처리 금지.
**판정 = 통과, `main` 머지·push 완료. 더 할 일 없음.**
**R-1 해소 ✓**: `check-new-capabilities.py` 가 추출기의 `LEVEL_STRENGTH` 를 재사용해 **base∩head 공유 능력 id 의 level 강화**(watched→protected)를 감지 — `escalated_capability_record`(base_level·`change: level_escalation` 부착) 후 protected 는 `new_capabilities`→`approval_required`/exit 2. 수정계약(A-0011) 정확 정합. **설계 정합**: 파일 내 동일 id 는 추출기 `strongest_level`(defaultdict 병합, line 131~141)로 **단일 record·최강 level** 로 집계되므로, head 에 watched `getattr`+protected `os.system` 공존 시 `head_caps[subprocess_exec].level=protected` 로 확정 → 에스컬레이션 루프가 정확히 포착(집계가 load-bearing).
**적대 재검증(fresh·픽스처 밖·실제 `policies/sensitive-capabilities.yaml`)**: ① **R-1 핵심 폐쇄** — 신규 repo base `getattr(os,name)`(watched) + head `os.system(cmd)` 추가 → 브랜치 게이트 `approval_required`/**exit 2**·record `base_level:watched`·`change:level_escalation`·두 신호(dynamic_access line5 + call os.system line9) 병합 표면화. ② **de-escalation 무과탐** — base protected `os.system` → head 동적 watched `getattr` 단독(protected 소멸) → `head_level(0)≤base_level(1)` skip → **pass/exit 0**(완화 아님·신규능력 없음 정합). ③ 정합 상수: `LEVEL_STRENGTH={watched:0,protected:1}` 추출기와 공유(불일치 없음).
**음성검증(rig-and-revert)**: 에스컬레이션 루프(`set(head_caps)&set(base_caps)` 블록) 제거한 게이트 사본을 **동일 fresh R-1 입력**에 실행 → `pass`/**exit 0**·`new:[]`·`warned:[]` 로 뒤집힘 = 가드 load-bearing 실증이자 R-1 회귀 정확 재현. 원복 시 exit 2. 전체 `bash tests/run-tests.sh` **68/68 PASS**(신규 `new-capabilities-dynamic-level-escalation` 포함)·기존 `new-capabilities-dynamic-watched-pass`(base clean→head 동적 watched 단독=pass+warning) 유지·`git diff --check`(47db5c5..dec42e9) clean·`py_compile` OK.
**보수적 개발(§1)**: 보정 델타(`e839fe9`) = `check-new-capabilities.py` **+22줄**(소비자 분류 1곳)·`tests/cases.yaml` 1케이스·신규 픽스처 2파일 = 계약 범위 정확 준수. **추출기(`extract-python-capabilities.py`)·`policies/*` 무접촉**(A-0011 명시요구)·무관 리팩터/scope-creep 없음. Claude 소유 파일 무접촉. `dec42e9` 동반 docs 는 공동소유 handoff/summaries.
**비차단 관찰(O-1, 차기 정리·반려 아님)**: 에스컬레이션 record 는 head level 이 base 보다 강한 경우만 만들어지고 현재 level 은 watched(0)/protected(1) 뿐이라 `elif record["level"]=="watched"` 분기는 사실상 **도달 불가**(에스컬레이션 head level 은 항상 protected). 방어적·무해하며 3단계 level 도입 시 전방호환 → §2B 필수질문=**아니오**(구멍 아님). 비차단.
**머지 판정(D-007)**: `check-new-capabilities.py` = **신규 능력 diff 분석·판정 게이트**(exit 0/2·approval 상한·1층 자동차단 권한 없음·정산/인증·인가/암호화/migration/infra 무관) → CLAUDE.md §3 기준 **비민감**. TASK-005~015·018~020 게이트 전 계열 동일 범주 Claude 머지 선례(D-020~D-038). **머지가 브랜치 전체(원 TASK-016 추출기 `6aeb513`+보정 `e839fe9`)를 반입** — 추출기는 D-038 에서 AC#1~7 통과 확정분이라 정합. 테스트 머지로 코드 클린 확인(doc append 충돌만·`policies/sensitive-capabilities.yaml` 의 AC#8 source/owner 보존 확인). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push. TASK-016 완결.** 상세: `collab/answers/A-0011.md` §해소 · `review-notes.md` TASK-016 R-1 재리뷰(D-039) 절.

## D-038 (2026-07-11) TASK-016 동적 위험접근 감지 보강 `extract-python-capabilities.py` — **보정요청**(하류 통합 회귀: 동적 watched 가 신규 protected 은닉) + AC#8 Claude 완료
대상: 브랜치 `codex/2026-07-11-task016-dynamic-capabilities` (헤드 `47db5c5`·구현 `6aeb513`). 판정: **보정요청 1건(🔴)** → 코드 브랜치 **머지 보류**. 리뷰기록만 `main` 머지. 상세: `collab/answers/A-0011.md`·`review-notes.md` TASK-016 절. **멱등성**: `6aeb513`·`47db5c5` 재처리 금지. 재제출은 R-1 보정 델타만.
- **추출기 계층 AC #1~7 통과(재론 불필요)**: fresh 픽스처밖 입력으로 실증 — `getattr(os,name)`→watched / `getattr(self,name)`·미바인딩→무신호(오탐억제) / `getattr(os,"sy"+"stem")`·`__import__("sub"+"process")`→상수접기 protected 정확 / `__import__(name)`·`importlib.import_module(name)`→dynamic_code_exec watched / `base64.b64decode` 인접→base64_dynamic / `globals()[name]()`→namespace_access watched. 별칭 해소·결정성·음성검증(기대 변조→단독 FAIL 66/67·원복 67/67) OK. `strongest_level` 로 동적 watched 는 protected 로 승격 불가(AC#3 상한 준수).
- **R-1 (🔴 보정사유) — 하류 회귀**: TASK-016 이 protected 능력을 watched 로도 표면화 → "id 1개 ⇒ level 1개" 전제 붕괴. `check-new-capabilities` 신규탐지는 **id 집합 차분만**(level 무시) → base 에 동적 watched 로 능력 id 가 이미 있으면 head 의 **신규 protected 정적호출을 은닉**. **실증(실제 정책)**: base `getattr(os,name)`+head `os.system(cmd)` 추가 → **main=approval_required/exit2(포착) ↔ 본 브랜치=pass/exit0(무경고 은닉)** = 기존 게이트 순수 퇴행. CLAUDE.md §2B 필수질문상 거버넌스 직접구멍 → 비차단 금지.
- **보정 계약**: `check-new-capabilities.py` 에 **level 에스컬레이션 탐지**(base∩head 공유 id 에서 watched→protected 승격 시 approval_required) + 상설 회귀 픽스처(위 실증세트, 기대 exit2) + 음성검증. 추출기·정책파일 무접촉. base=clean→head 동적 watched 단독은 기존대로 pass+warning 재확인.
- **AC #8 (Q-0003) — Claude 완료**: 정책 소유자로서 `policies/sensitive-capabilities.yaml` 5종에 `source`(builtin: cwe/owasp/bandit | org:팀)·`owner` 필드 + 헤더 스키마 주석 추가. 게이트 미독해 필드라 무해(64/64 PASS). Codex 재구현 불요.
- **보수적 개발 평가**: 브랜치 델타 = Codex 소유 `extract-python-capabilities.py`(+143)·`tests/*`·fixtures·공동 summaries/handoff, Claude 소유 무접촉·scope-creep 없음(추출기 자체는 깨끗). 반려는 순전히 하류 정합 1건.

## D-037 (2026-07-11) TASK-015 함수 후보 랭킹 스캐너 `bootstrap-sensitive-functions.py` — **통과·머지완료**
대상: 브랜치 `codex/2026-07-11-task015-bootstrap-functions` (impl `c174ae6`·핸드오프 `1895c1f`). 판정: **통과** → 코드 브랜치 `main` 머지·push(구현자 Codex ≠ 머지자 Claude). 상세: `review-notes.md` TASK-015(D-037) 절. **멱등성**: `c174ae6`·`1895c1f` 재처리 금지.
- **AC 충족(1~6)**: ① 기존 `extract-python-capabilities`+`extract-python-inventory` 를 `importlib` 재사용(재구현 없음). ② 출력 = `(경로,함수,능력id[],근거라인)` → `sensitive-functions` 초안, 코드 주석 미부착. ③ `mode: draft_only`·adoption_note(수동 채택)·근거 evidence 필수·결정적·`--json`. ④ 한계 문구(`limitation_statement`): 위험 프리미티브 없는 "의미상 민감" 순수 로직은 미탐 — 스캐너·하네스 공통 미해결 영역·후속 sink tracing/unknown-code 필요 명시. ⑤ SQL 테이블 근거(선택 `--tables`, 없으면 스킵·오류 아님). ⑥ `anchor`(정규화 심볼+시그니처 해시)+`status: proposed`+fingerprint(line 제외)+rejected 원장 스키마+accepted/rejected 재제안 금지.
- **적대 검증(fresh, 픽스처 밖 — CLAUDE.md 고정 세트)**: ① 동명 오버로드(getter/setter) → start_line 로 별도 후보·시그니처로 지문 분리. ② 조건부/중첩 def·클로저 → 가장 안쪽 함수로 정확 매핑. ③ 결정성 2회 stdout 동일. ④ 비UTF8(`0xe9`) 파일 → `errors` 격리·형제 정상파일 보존·exit 0(TASK-013 교훈 준수). ⑤ 빈 repo·무 tables → exit 0. **fail-safe 불변식**: `deepest_function_for_line` 폴백이 신호를 **드롭하지 않고** 최악의 경우 `<module>` 로 귀속 → 어떤 능력 신호도 유실 없음.
- **보수적 개발 OK**: 델타 = Codex 소유 `bootstrap-sensitive-functions.py`(신규 408줄·무관 리팩터 없음)·`tests/cases.yaml`(3)·`tests/run-tests.sh`·fixture 4파일·`README.md` 1줄·공동 summaries/handoff. **Claude 소유 policies/·docs/·CLAUDE.md·TASKS.md·decisions.md·templates/ 무접촉**(name-only 확인)·scope-creep/over-reach 없음. `py_compile`·`git diff --check` OK·64/64 PASS.
- **비민감 판정 근거**: draft_only 수동 씨딩 헬퍼 — verdict 파이프라인 미연결·자동차단/자동채택 없음·정산/인증·인가/암호화/DB migration/infra 무관(CLAUDE.md §3). TASK-014(D-035·D-036) 및 TASK-005~013·018~020 게이트 계열과 동일 범주 Claude 머지 선례 → 형 승인 불요, Claude 머지.
- **비차단 관찰 3건(전부 fail-safe/내재한계 → §2B 대로 차기 AC 가드로 *명시*, 반려 아님)**:
  - **O-1 rename 노트 미발화**: `signature_hash` 가 함수명 포함 → rename 시 `symbol`·`signature_hash` 동시 변경 → `anchor_note` "move or rename" 분기가 **move 에만 발화·rename 엔 미발화**(fresh: `pay`→`pay2` `review_note=None`). AC#6 "이름 변경 시 재확인" 이름측 미충족. **단 fail-safe**(rename→지문변경→재제안, 보호 미해제; 손실=연결 힌트뿐). AC#6 명세갭(D-035 O-2 동형) → 차기 AC 가드: `signature_hash=인자 시그니처만(이름 독립)`+회귀 픽스처(accept→rename→재제안 AND move/rename 노트).
  - **O-2 데코레이터 라인 능력호출 → `<module>` 귀속**: `@subprocess.getoutput(...)` 등 데코레이터 식 능력호출은 라인이 `def`(start_line) 위라 함수 미귀속·`<module>` 폴백(inventory start_line 한계, TASK-005/006 성질). **단 fail-safe**(신호 드롭 없음·정확 라인 evidence 로 노출). CLAUDE.md 요구 **데코레이터 상설 회귀 픽스처가 TASK-015 부재** → 차기 AC 가드: 데코레이터-능력호출 픽스처 상설화 + 데코레이터 라인을 함수로 귀속.
  - **O-3 동일 지문 충돌**: 한 파일 내 이름·시그·능력·evidence 전부 동일한 두 함수(조건부 twin/@overload)는 같은 fingerprint → 한쪽 reject/accept 시 둘 다 suppress(fresh: twin `pay` 하나 reject→`suppressed_rejected=2`). 유일 fail-unsafe 방향이나 초안상 사람도 구분 불가한 사실상 동일함수 = 내재한계·draft_only 로 실해 미미 → 차기 AC 가드: suppression 키에 `start_line`/본문해시 disambiguator(위치 churn 주의).

## D-036 (2026-07-11) TASK-014 fingerprint 안정성 가드 (D-035 O-2 이월분 마감) — **통과·머지완료**
대상: 브랜치 `codex/2026-07-11-task014-fingerprint-stability` (fix `4ecdc68`·핸드오프 `f04de7d`). 판정: **통과** → 코드 브랜치 `main` 머지·push(구현자 Codex ≠ 머지자 Claude). 상세: `review-notes.md` TASK-014 fingerprint(D-036) 절. **멱등성**: `4ecdc68`·`f04de7d` 재처리 금지.
- **수정계약(D-035 O-2) 이행 확인**: fingerprint 입력을 evidence 전체 → **`path`+`level`+정렬된 `{(source, rule_id)}` 집합**(`evidence_identity` = source/rule_id 만; `matched`/개별 파일 `path`/`owner` 제외)으로 변경. evidence 보고에는 파일 경로 그대로 유지, 지문 산출에서만 제외 = 명세(TASKS.md AC#6 가드) 정확 이행. `set` 후 `sorted` = 순서·중복 무관.
- **적대 검증(fresh, 픽스처 밖·격리 worktree)**: scratch repo 에 존당 파일 1개(login.py·001_init.sql)로 지문 캡처 → 형제 파일(logout.py·002_add_index.sql) 추가 후 재산출 → **지문 완전 동일**(`services/auth/**`=`92efc7c9…`·`db/migrations/**`=`f2d0592e…`·`src/security/**`=`d69633e6…`), evidence 파일수는 1→2·2→3 로 증가해도 불변 = D-035 alert-fatigue 시나리오 실제 차단 실증. 픽스처 저장 지문과도 일치.
- **음성검증(rig-and-revert)**: 동일 입력을 **예전 evidence-전체 스킴**으로 재산출 시 형제 추가만으로 `db/migrations/**`·`services/auth/**` 지문 CHANGED(회귀 재현), 단일 evidence 인 `src/security/**` 만 SAME → 스킴 변경이 load-bearing 임을 실증. 테스트단: `tests/run-tests.sh` 61/61 PASS, 저장 지문을 예전 스킴으로 monkey-patch 하면 suppression 0/후보 3(Codex 보고 재현).
- **회귀 픽스처 = AC 가드 명세 충족**: `previous.yaml` 에 `services/auth/**` **rejected** 원장 + `db/migrations/**` **accepted** 원장을 두고 repo 에 각 형제 파일 추가 → 재스캔 시 `suppressed_rejected=1`·`suppressed_accepted=1`·잔여 후보 1(`src/security/**`)로 **양방향**(reject·accept) suppression 검증(D-035 요구 "존 reject→형제추가→여전히 suppressed"·양쪽). `run-tests.sh` 에 `suppressed_accepted` 단언 추가(테스트 하네스 확장, scope-creep 아님).
- **보수적 개발 OK**: 델타 = Codex 소유 `bootstrap-sensitive-zones.py`(+11줄, 무관 리팩터 없음)·`tests/cases.yaml`·`tests/run-tests.sh`·fixture 2파일·`previous.yaml`·handoff·summaries. **Claude 소유 policies/·docs/·TASKS.md·CLAUDE.md·decisions.md·review-notes.md 무접촉**(name-only 확인). `py_compile`·`git diff --check` OK.
- **비민감 판정 근거**: draft-only 수동 씨딩 헬퍼의 안정성 보정 — verdict 파이프라인 미연결·자동채택 없음·정산/인증/인가/암호화/DB migration/infra 무관(CLAUDE.md §3). TASK-014(D-035) 및 TASK-005~013·018·019·020 게이트 계열과 동일 범주로 Claude 머지 선례 → 형 승인 불요, Claude 머지.
- **비차단 관찰(O-1, 이월 불요)**: 스킴 변경으로 이전(`ecd5d68`) 스킴 지문이 든 기존 previous.yaml 원장은 지문 불일치로 suppression 이 조용히 깨질 수 있음. **단** 본 도구는 아직 draft_only·미도입(실운영 원장 부재)이고 D-035 가 명시적으로 요구한 스킴 변경의 의도된 귀결이라 실해 없음 → 가드 불요(관찰만 기록).

## D-035 (2026-07-11) TASK-014 정책 자동 씨딩 스캐너 `bootstrap-sensitive-zones.py` — **통과·머지완료**
대상: 브랜치 `codex/2026-07-11-task014-bootstrap-zones` (impl `ecd5d68`·핸드오프 `bdb7e4a`). 판정: **통과** → 코드 브랜치 `main` 머지·push(구현자 Codex ≠ 머지자 Claude). 상세: `review-notes.md` TASK-014(D-035) 절. **멱등성**: `ecd5d68`·`bdb7e4a` 재처리 금지.
- **AC 충족(1~6)**: ① 2종 씨딩 소스 — 경로 네이밍 토큰(외부화 `--rules`) + CODEOWNERS 소유자 규칙. ② 후보별 근거 evidence(source·rule_id·matched·path/owner) 필수. ③ **draft_only**(mode 필드·adoption_note 에 "automatic" 금지·파일 미덮어쓰기, stdout/`--json`만). ④ 결정적(2회 동일 실증)·규칙매칭만(LLM/휴리스틱 없음). ⑤ 빈 규칙·CODEOWNERS 부재 = 오류 아님(exit 0·`codeowners_read:false`·path rule 단독 동작 실증). ⑥ `status: proposed` + 결정적 fingerprint + rejected 원장(`rejected_reason`/`rejected_by` 스키마) + accepted/rejected 재제안 금지.
- **적대 검증(fresh, 픽스처 밖)**: ① 파일명 토큰 매칭(`app/auth.py`) → 글로브가 `app/auth.py/**` 로 생성 — 이 repo 자체 매처(`check-sensitive-zones.match_glob`)에서 **후행 `**`가 0세그먼트 매칭** → `app/auth.py` 를 실제 매칭함(직접 실증). 보기엔 어색하나 기능상 정합 = **비차단**. ② no-CODEOWNERS repo → path rule 단독 후보 생성·exit 0. ③ 빈 규칙 → 후보 0·exit 0. **음성검증**: `candidate_count` 기대값 3→99 변조 시 `bootstrap-sensitive-zones-candidates` **단독 FAIL(60/61)**, 원복 61/61 = 테스트 load-bearing(항상-PASS 아님) 실증.
- **보수적 개발 OK**: 델타 = Codex 소유 `bootstrap-sensitive-zones.py`(신규)·`tests/*`(케이스 3·픽스처)·README 레지스트리 2줄·handoff·summaries. **policies/·docs/·CLAUDE.md·TASKS.md 등 Claude 소유·정책파일 무접촉**·무관 리팩터/scope-creep 없음. `py_compile`·`git diff --check` OK·61/61 PASS.
- **비민감 판정 근거**: **draft-only 수동 씨딩 헬퍼** — verdict 파이프라인에 물리지 않고 사람이 채택 승인(자동차단·자동채택 없음). 정산·인증/인가·암호화·DB migration·infra 어디에도 해당 없음(CLAUDE.md §3). TASK-005~013·018·019 게이트 계열과 동일 범주로 Claude 머지 선례(D-020~D-034). → 형 승인 불요, Claude 머지.
- **🔴→차기 AC 가드 이월(O-2) — fingerprint 취약성**: fingerprint 를 `path+level+evidence` **전체**(매칭된 파일별 `path` 포함)로 산출 → 이미 **accepted/rejected 된 존에 형제 파일 1개만 추가돼도 evidence 집합이 바뀌어 fingerprint 가 변함 → 후보가 재출현**(fresh 실증: rejected `services/auth/**` 에 `logout.py` 추가 시 `suppressed_rejected` 1→0 재제안; accepted 도 동일 재제안). 이는 AC#6 이 명문화한 🔴 목적("스캔 재실행마다 거절 후보 재출현 → 씨딩 자체가 alert fatigue")을 **일상적 repo 성장에서 그대로 defeat**. **단, 이는 구현 이탈이 아니라 AC#6 명세 자체("경로+근거 정규화 해시")를 Codex 가 충실히 이행한 결과** = 명세설계 갭. Codex 반려는 부당(수용기준·논리 정합·테스트 충족). → §2B "거버넌스 영향 논리결함은 차기 AC 가드로 *명시적으로* 막는다" 에 따라 **TASK-014 AC#6 개정 + 회귀 픽스처를 차기 가드로 명시**(비차단으로 안 흘림). 수정계약: fingerprint 를 **후보 정체성**(`path`+`level`+정렬된 `{(source, rule_id)}` 집합)으로 산출(개별 매칭파일 `path` 는 evidence 보고에는 남기되 지문에서 제외). 회귀 픽스처: 존 reject → 형제 파일 추가 → 재스캔 시 **여전히 suppressed**. (TASKS.md TASK-014 AC#6·TASK-015 anchor 조항에 반영.)

## D-034 (2026-07-11) TASK-020 R-1 보정 재제출 재리뷰 — **통과·머지완료** (MVP-1.5 TASK-020 완결)
대상: 브랜치 `codex/2026-07-11-task020-maturity` (보정 `32726a6`·헤드 `d1c98e1`). 판정: **통과** → 코드 브랜치 `main` 머지·push(구현자 Codex ≠ 머지자 Claude). 상세: `review-notes.md` TASK-020 재리뷰(D-034) 절. **멱등성**: `5449c65`·`42062f6`(정상경로·D-033 통과분)·`32726a6`·`d1c98e1` 재처리 금지.
- **R-1 해소 ✓**: D-033 수정계약 그대로 이행. `check-policy-change.py` 구조비교에 `maturity_weakened(before, after)` 추가 — 기존 zone/capability 의 (무maturity=enforcing 또는 enforcing)→`shadow` 전환을 `weakened_zone_maturity`/`weakened_capability_maturity` 로 기록 → `policy_loosening` → `approval_required`(exit 2). 신규 shadow 룰 신설(base 에 없던 zone/cap)은 교집합 루프 밖이라 미발동 = pass 유지. 정합성: 런타임 게이트(sensitive-zones·new-capabilities)와 동일하게 **정확히 `"shadow"`** 만 완화로 취급(대문자·오타는 런타임서 fail-closed enforcing → 완화 아님이므로 미탐이 정합).
- **적대 재검증(fresh, 격리 worktree)**: ① no-maturity frozen 정산존 +`maturity: shadow` → `approval_required`/exit 2·`weakened_zone_maturity`(픽스처 밖 fresh). ② 신규 shadow 존 추가 → pass/exit 0(과탐 없음). ③ capability enforcing→shadow → `weakened_capability_maturity`/approval. ④ **음성검증(rig-and-revert)**: `maturity_weakened`→`return False` 변조 시 `policy-change-maturity-shadow-loosening` **단독 FAIL(57/58)**·`-new` 는 그대로 PASS, 원복 58/58 = 감지블록 load-bearing·픽스처 실가드 실증.
- **보수적 개발 OK**: 델타 = Codex 소유 `check-policy-change.py`(+28줄, 무관 리팩터 없음)·`tests/cases.yaml`(2케이스)·픽스처 2쌍. Claude 소유 정책파일 무접촉·scope-creep 없음. `py_compile`·`git diff --check` OK.
- **비민감 판정 근거**: 하네스 거버넌스 *메타게이트* 강화(완화 미탐 구멍 닫음 = fail-closed 방향)·자동차단(1층) 권한 없음(verdict=approval_required 2층)·기존 감지 무회귀(58/58). TASK-018/019 동일 범주(gate 코드)로 Claude 머지 선례 존재 → 형 승인 불요.
- **비차단 이월(MVP-2, O-1)**: `maturity_weakened` 가 `before` 를 **리터럴 `"enforcing"`** 로만 비교 → **`maturity: pilot`(무효·런타임 fail-closed enforcing) → `shadow`** 전환은 실효적 완화인데 미탐(fresh 실증 T-D: pass/exit 0). 발동 전제(base 가 이미 무효 maturity = 오류표시 상태)가 비정상이고 R-1 이 실증한 **주 경로(유효 enforcing/무기입→shadow)는 닫힘** → 차기 AC 가드로 명시(§2B: "보정 또는 차기 AC 가드로 *명시적으로*"). 수정형: 효과적 maturity 정규화(`m if m in VALID else "enforcing"`) 후 `before_eff != "shadow" and after_eff == "shadow"`.

## D-033 (2026-07-11) TASK-020 규칙 성숙도(maturity/shadow) **보정요청** (R-1 · 🔴)
대상: 브랜치 `codex/2026-07-11-task020-maturity` (헤드 `42062f6`, 구현 `5449c65`). 판정: **보정요청** — 코드 브랜치 머지 **보류**, 리뷰기록만 `main` 머지. 상세: `collab/answers/A-0010.md`·`review-notes.md` TASK-020 절.
- **통과(재론불요)**: AC #1(기본 enforcing·하위호환)·#2(shadow→verdict 미반영+shadow_hits, 4게이트·혼합존 T6/T7 포함 실증)·#4(쌍 픽스처+독립 음성검증 rig-and-revert 2종)·AC #3 **fail-closed 절**(잘못된 maturity→enforcing+검증오류, T5·capability 실증). 56/56 PASS. 보수적개발 OK(무관 리팩터·scope-creep 없음·Claude 소유 무접촉).
- **R-1(🔴 보정사유)**: AC #3 **정합성 조항**("`maturity: shadow` 로 바꾸는 diff 는 TASK-018 이 완화로 잡는다 — 두 태스크 정합 필수") **미충족**. clean fresh 실증: frozen 정산존에 한 줄 `maturity: shadow` 추가 → ① sensitive-zones 가 그 존을 PASS(자동차단 무력화) ② 그 **정책 diff 를 `check-policy-change.py` 가 완화로 미탐(exit 0)**(양성대조: 등급하향은 정상 감지). = 유일한 하드-차단(1층 frozen·불변원칙 §4)이 어떤 게이트에도 안 걸리는 한 줄로 무력화 → **§2B 직접구멍, 비차단 불가**.
- **수정계약**: `check-policy-change.py` 구조비교에 maturity 차원 추가 — 기존 zone/cap 의 enforcing→shadow 전환 = `policy_loosening`(approval), 신규 shadow 룰 신설 = pass. 회귀 픽스처 1쌍 + 음성검증. (파일 Codex 소유 → Codex 보정.)

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

## D-032 (2026-07-11) TASK-019 보정 재제출 재리뷰 — R-1·R-2 해소 확인 · **통과 · Claude main 머지** (MVP-1.5 TASK-019 완결)
대상: `codex/2026-07-09-task019-coverage-statement` · 보정 impl `c72169d` · 헤드 `29a48e9` (선행 D-031/A-0008). 재리뷰 범위 = **보정 델타(R-1·R-2)만**, 정상 verdict 경로는 D-031 에서 통과 확정·재론 없음. 멱등성: `d8ad086`·`195a957`·`c72169d`·`29a48e9` 재처리 금지.
**판정 = 통과, `main` 머지·push 완료. 더 할 일 없음.**
**R-1 해소 ✓**: `coverage_statement(diff_input, verdict, checked=None)` 선택인자 추가(기본 `None`→기존 `executed_gate_records()` 보존)·`main()` 예외 핸들러만 `checked=[]`. **적대 재검증 fresh 오류입력 3종 전부 `checked:[]`·17키 정합**(① `--change-intent /nonexistent-XYZ.yaml`=A-0008 원 재현입력 ② `--sensitive-zones /tmp/broken.yaml` 파손 YAML ③ `no-such-ref-abc..HEAD` git RuntimeError) — 픽스처 1건이 아니라 **예외 핸들러 전 경로**에 적용됨 확인. 정상경로 동적성(baseline 2게이트 vs function 3게이트) **무회귀**. **설계 정합**: 예외는 전부 `build_evidence` 초입(`load_intent`→정책로드→`read_diff_lines`)에서 발생 = `intent_result`/`sensitive_result`/`build_function_gov_result` **평가 이전**이므로 `checked:[]` 가 사실과 정확히 일치(공허한 방어 아님)·`policy_sha:{}`·`changed_files:[]`·`summary:0` 과 카드 전체 일관.
**R-2 해소 ✓**: 오류 카드 `changed_functions:[]` 추가 → top-level **17키==템플릿 17키**(fresh 3종 전부 확인). 신규 회귀 케이스 `evidence-error-missing-intent` 가 `coverage_checked_gates:[]`·`changed_functions:[]`·`schema_keys_match_template` 를 **오류 카드에** 적용. `run-tests.sh` 는 `if "<key>" in expect` 로 검사 → **빈 리스트 기대값도 실제 비교됨**(falsy 스킵 무력화 아님·소스 확인). 49→**50/50 PASS**.
**음성검증(rig-and-revert) 2종**: ① `checked=[]` 제거(보정 전 과잉주장 복원) → `evidence-error-missing-intent` **단독 FAIL(49/50)**, ② 오류카드 `changed_functions:[]` 삭제 → **단독 FAIL(49/50)**, 원복 **50/50 PASS**. 두 변조 모두 **기존 49 케이스는 전부 통과** → D-031 이 지적한 "기존 테스트가 오류 카드를 한 번도 안 봤다(거짓확신)"의 실증이자, 신규 픽스처가 그 사각지대를 정확히 메운 **실가드**임의 증명(항상-PASS 아님).
**보수적 개발(§1)**: 코드 델타 = `generate-change-evidence.py` **7줄** + `tests/cases.yaml` 1케이스 = 수정계약 범위 정확 준수. 정상 verdict 경로 **무변경**(A-0008 명시요구·기본인자 `None` 로 기존 호출부 무영향). 무관 리팩터·포맷·이름변경 없음 → scope-creep·over-reach 없음. `c72169d` 가 함께 들여온 `A-0008`/`decisions`/`review-notes`/`docs/adr/*` 는 COMMON-RULES §5.1 요구 **`origin/main` 동기화 머지**로 들어온 내 기존 기록(origin/main 과 동일 확인·Codex 변조 없음). 검증 `tests/run-tests.sh` **50/50 PASS**·`git diff --check` clean·`py_compile` OK (격리 worktree 재현).
**비차단 이월**: **O-2(신규·차기 AC 가드로 명시)** 오류 카드 `verdict_statement` 가 여전히 `governance violation detected` — 실제론 입력/설정 오류이지 위반 탐지 아님. A-0008 R-1 이 문구 교체를 **"권장하나 비필수"** 로 못박아 보정사유 아니며, §2B 필수질문=**아니오**(심각도를 *과대* 진술·fail-closed·exit 1 → 민감 변경을 통과시키는 구멍 아님). 차기 AC 로 고정: 오류 카드 중립 문구(`governance checks did not run (tool error)` 류)+회귀 픽스처. **O-3(신규)** `check_function_gov_level` raise 시 intent·sensitive 2게이트는 실제 실행됐는데 `checked:[]` = **과소보고** — 보수적(더 검증된 것처럼 보이게 하지 않음)이라 구멍 아님·비차단. 차기: 실행 게이트 누적기록 후 예외 시 그때까지 목록 방출. **O-4(신규)** 오류 픽스처가 가리키는 `tests/fixtures/evidence-error/missing-change-intent.yaml` 은 **부재 자체가 트리거**(무주석) — 훗날 실제 생성되면 verdict 가 blocked 밖으로 튀어 **테스트가 시끄럽게 실패**(조용한 무력화 아님) → 비차단, 차기 주석 1줄. **O-1(이월)** `schema_keys_match_template` top-level 한정 → MVP-2 재귀 형상비교. **AC #8(이월)** policy bundle digest 는 `policy_sha` 로 부분충족·전체 번들 해시 MVP-2.
**머지 판정(D-007)**: `generate-change-evidence.py` = **감사카드 생성·집계 게이트**(정산·인증/인가·암호화·DB migration·infra 해당 없음·자동차단 권한 없음) → CLAUDE.md §3 기준 **비민감**, TASK-005~013·TASK-018 동일 범주(D-020~D-030 선례). 구현자(Codex)≠머지자(Claude) → **Claude 가 `main` 머지·push.** **MVP-1.5 TASK-019 완결.** 상세: `collab/answers/A-0009.md` · `review-notes.md` TASK-019 재리뷰(D-032) 절.

## D-056 (2026-07-16) TASK-024 역도달성 게이트 `check-indirect-impact.py` — 리뷰 **통과** + Claude main 머지 (MVP-2 간접영향)
대상: `codex/2026-07-16-task024-indirect-impact` · impl `74bdcf2` · 헤드 `7f12e73`. 브랜치는 `origin/main`(`0e7e258`)의 **클린 후손**(Codex 재제출 전 병합 준수 — **D-050 함정 종식 지속**). 미머지 `origin/codex/*` 는 이 하나 → **Claude 리뷰 차례**(handoff 최신이 `[2026-07-16] Codex → Claude | 74bdcf2` = 신규 제출, 보정요청 아님).
**판정 = 통과, `main` 머지·push 완료. 더 할 일 없음.** 멱등성: `74bdcf2`·`7f12e73` 재처리 금지.

**설계 정합(방향)**: 게이트는 sink 로부터 **forward(caller→callee)** BFS 로 도달하는 노드 = sink 의 **의존(callee)** 을 구한다. changed 함수가 그 집합에 있으면 "sink 이 의존하는 상류를 고쳐 민감행동을 무너뜨림" = 간접영향. **적대 방향검증(fresh advrepo2)**: sink 의 **소비자**(`consumer.run` 이 `transfer()` 호출)를 변경 → **미발화**(소비자는 sink 의존 아님·정론), 반면 sink 의 의존 `compute_fee` 변경 → **발화**. 방향 반전 아님 확인.

**AC 전 항목 fresh 적대검증(격리 worktree `wt-task024` + advrepo1~3)**:
- **AC#1(발화·차단금지)** ✓ direct 픽스처 + fresh: **method-as-sink**(`app.reports.Report.export` 가 module-level `check_permission` 호출, advrepo1)→`indirect_impact`·`approval_required`·class-qualified path. exit code 는 **0(pass)/2(approval) 뿐, 1(block) 없음**(최상위 except 핸들러도 exit 2) = 차단금지 불변식 준수.
- **AC#2(감사필드)** ✓ `sink_id`·`changed_function`·`path`(sink→…→changed)·`hops`(=len(path)-1, 최단) + `sink_function`·`reviewer`·`reason`·`maturity`. 30초 판독 충족.
- **AC#3(라우팅=sink owner)** ✓ `finding.reviewer = sink.owner or tool_owner`. fresh frozen-auto sink(advrepo2)에서 zone `required_approval: settlement-reviewer` → `reviewer=settlement-reviewer`·`reviewer_required=[settlement-reviewer]` 전파 확인. 분석실패 시 `tool_owner` 폴백(F-2).
- **AC#4(shadow 성숙도)** ✓ shadow 픽스처: shadow sink → `shadow_hits`(verdict-neutral·`reviewer_required` 미포함·verdict pass). enforcing 만 `approval_required` 승격.
- **AC#5(N홉 경계·과탐경계·음성검증)** ✓ two-hop-boundary 픽스처(N=1 서 2홉 `normalize_user` 미발화) + advrepo1 `unrelated`(sink무관) 미발화. **파라미터 실배선 확인**: 같은 픽스처 `hops:2` 로 올리니 `normalize_user`(2홉) **발화**(하드코딩 1 아님). **음성검증(rig-and-revert)**: `reachable_paths` 의 `if depth >= max_hops` 무력화 → `indirect-impact-two-hop-boundary` **단독 FAIL(0/1)** = 경계필터 load-bearing.

**정직성(ADR-001 D4)**: 이름기반 콜그래프가 `self.compute()` 등 attribute/동적 호출을 미해소 → 그 경로의 간접영향은 verdict 에 안 잡히나 **`coverage.unevaluated` 로 명시 노출**(fresh advrepo3: `Report.export`→`self.compute` unresolved 가 coverage 에 등장, verdict pass). 조용한 누락 아님 = 설계 §7 영구한계의 정직한 공개. TASK-025 AC#3 이 이 정직성을 회귀로 고정.

**fail-closed(F-2)**: map/classify/callgraph/sinks 오류 → `fail_closed` 레코드 + `approval_required` + `tool_owner`. analysis-error 픽스처(head `broken.py` 구문오류)에서 **부분결과(진짜 finding `check_permission`)와 fail_closed 동시 방출**(콜그래프 per-file 복원력) → 실오류가 진짜 finding 을 가리지 않음·최악에도 fail-safe(approval). errors_present·fail_closed_present·reviewer_required=[security-reviewer, tool_owner] 확인.

**게이트간 이름 조인 무결(하류 정합)**: map-diff·classify·callgraph·extract-sinks **네 게이트 전부 동일 `full_function_name`(module.<scoped>) + class-qualified 스코프명** 사용 → changed_function ↔ callgraph 노드 ↔ sink.function 이 method(`app.reports.Report.export`)·module-level·frozen-auto(`frozen:app.settlement.core.transfer`) 전부 정확히 매칭(fresh 실증). TASK-023 R-1~R-3 오해소 폐쇄가 여기서 **민감 엣지 보존**으로 결실.

**검증 요약**: `run-tests.sh` **85/85 PASS**(병합 후 main 재확인) · `mutation-check.sh` PASS(139 expectation mutations load-bearing + policy mutation) · fresh advrepo1~3 4시나리오 정답 · rig-and-revert 2종.

**보수적 개발(§1)**: 델타 = 신규 `check-indirect-impact.py`(337L) + `cases.yaml`(+88)·`run-tests.sh`(+66)·fixtures(indirect-impact 4종 + analysis-error) + `README.md`(-1 stale count/+1 usage)·`handoff-log`·`summaries`. `policies/*`·`templates/*`·`docs/*`·`CLAUDE.md`·기존 게이트 `.py` **무접촉**(check-indirect-impact.py 만 gates 하위 신규). 기존 map/classify/callgraph/sinks 게이트를 **importlib 재사용**(재구현 아님). scope-creep·over-reach 없음.

**머지 판정(D-007)**: 정적 콜그래프 역도달성 **분석 게이트** = **비민감**(정산·인증/인가·암호화·DB migration·infra 코드 무해당·자동차단 권한 없음·approval_required 상한). TASK-018/019/022/023 동일 범주 선례(D-020~D-032·D-046·D-052~D-055). 구현자(Codex)≠머지자(Claude) → **Claude `main` 머지·push.**

**비차단 관찰(차기 AC 가드로 명시 — 비차단 방류 아님, §2B 필수질문=아니오)**:
- **O-1(TASK-025 AC#1 로 고정)** 상설 회귀 픽스처가 **registry sink(module-level 함수)만** 커버. **method-as-sink**·**frozen-auto sink**·**@gov(sink=true) sink** 의 이름조인은 이번에 fresh 로 정상 실증했으나 **상설 픽스처 부재** → 침묵 회귀 위험. 거버넌스 구멍 아님(현행 동작 정확)이나 §2B "고정 적대세트" 정신상 TASK-025 7종 세트에 **method/frozen-auto/@gov sink 변형**을 명시 포함.
- **O-2(설계 §7 영구한계·TASK-025 AC#3)** self/attribute 메서드 호출로 이어지는 sink 의존은 verdict 미포착·coverage 만 노출. 정직성 회귀를 TASK-025 가 고정.

상세: `review-notes.md` TASK-024(D-056) 절 · `summaries/2026-07-16.md`.

## D-057 (2026-07-16) TASK-025 과탐 통제 + 고정 적대 입력 세트 — 리뷰 **통과** + Claude main 머지 (MVP-2 간접영향 상설 회귀)

**대상 impl**: `b15696c`(픽스처)·`8256fe4`(handoff) / 머지 헤드 `11ec86b`, 브랜치 `codex/2026-07-16-task025-adversarial-fixtures`. 순수 회귀 픽스처 태스크(게이트 로직 무변경).

**델타(테스트 전용)**: `tests/fixtures/indirect-impact/` 6종 신규(method-sink·frozen-auto·gov-opt-in·consumer-overdetect·dynamic-coverage·conditional-same-name) + `cases.yaml`(+137, 7 케이스에 `group: adversarial`) + `run-tests.sh`(+10, `coverage.unevaluated` 기대값 단언 추가) + `handoff-log`·`summaries`. **`.harness/gates/*`·`policies/*`·`templates/*`·`docs/*`·`CLAUDE.md`·기존 게이트 `.py` 무접촉.**

**AC 대비 검수(TASKS.md TASK-025)**:
- **AC#1(설계 §9 7종 상설 회귀)**: `adversarial` 그룹 7종 = ①직접경로 `indirect-impact-direct` ②method sink ③frozen-auto sink ④`@gov(sink=true)` opt-in 경계 ⑤sink 소비자 과탐 경계 ⑥동적 `coverage.unevaluated` 노출 ⑦조건부 동명 2홉. **§9 원문 7 중 N홉경계(§9.2)는 기존 `two-hop-boundary`(default 그룹·상설), 음성검증(§9.6)은 `mutation-check.sh`(151 mutations)로 상설 회귀** — 개념상 7종 전부 상설화됨. `adversarial` 그룹은 이 둘 대신 method-sink·frozen-auto(TASK-024 O-1 이월)를 담아 §9 와 문자적 1:1 아님(→O-1).
- **AC#2(hops 정책값·하드코딩 금지)**: conditional-same-name `hops:2`→hop2 발화 / two-hop-boundary `hops:1`→hop2 미발화 / **fresh 변조**(dynamic-coverage 정적화+`hops:1→2`)→hop2 `check_permission` 발화. hops 가 실제 판정 구동 = 하드코딩 아님 실증.
- **AC#3(동적 미탐 coverage.unevaluated 정직성)**: dynamic-coverage 의 `getattr(utils, check_name)(user)`→`coverage.unevaluated=[{caller:app.reports.dispatch, kind:dynamic, name:getattr(...)}]` 노출·verdict pass(조용한 통과 아님). rig(→[]) 단독 FAIL=load-bearing.
- **AC#4(고팬인 dampening 미구현)**: 게이트 로직 무변경으로 자명 충족(후속 검토 대상).

**적대적 검증(격리 worktree `wt-task025` · fresh 입력 + 음성검증)**:
- **게이트 직접실행 raw JSON**(5픽스처): conditional-same-name→approval(fallback hop2)·consumer-overdetect→pass(무발화)·dynamic-coverage→pass+coverage.unevaluated·gov-opt-in→pass+shadow_hits[download_report]·frozen-auto→approval(settlement-reviewer). **전부 cases.yaml 기대값 완전일치·거버넌스 정답.**
- **fresh 변조 3종**: ① consumer-overdetect 에서 **의존(check_permission) 수정→approval 발화** = 무발화가 forward-only 방향규율이지 죽은 게이트 아님 증명 ② conditional-same-name 에서 **if-분기 `normalize` 수정→hop2 발화** = 조건부 양분기 보수적 union 실증(else-분기 fallback 만 우연히 맞은 것 아님) ③ dynamic-coverage 정적 module-attr(`utils.check_permission`)+`hops:2`→hop2 발화 = 엣지 해소 정상·getattr 무발화는 hop 한계+동적 이중원인(침묵 누락 아님).
- **rig-and-revert**: dynamic-coverage `coverage_unevaluated`→[] · conditional-same-name verdict→pass 각각 단독 FAIL(0/1)·원복 `adversarial` 7/7=load-bearing.

**검증 요약**: `run-tests.sh` **91/91 PASS** · `adversarial` **7/7** · `mutation-check.sh` PASS(151 expectation mutations + policy mutation + metamorphic/negative groups).

**보수적 개발(§1)**: 델타 = 테스트 픽스처·cases·러너 단언만. 무관한 리팩터·이름변경·포맷 없음·intent 밖 경로 없음. scope-creep·over-reach 없음.

**머지 판정(D-007)**: 정적 콜그래프 역도달성 **분석 게이트의 회귀 픽스처** = **비민감**(정산·인증/인가·암호화·DB migration·infra 코드 무해당·자동차단 권한 없음·approval 상한·frozen-auto 픽스처의 settlement 는 테스트 데이터일 뿐 프로덕션 정산 로직 아님). D-020~D-056 동일 범주 선례. 구현자(Codex)≠머지자(Claude) → **Claude `main` 머지·push.**

**비차단 관찰(§2B 필수질문=아니오 — 거버넌스 구멍 아님)**:
- **O-1**: `adversarial` 그룹이 설계 §9 의 문자적 7종과 1:1 아님 — N홉경계(§9.2)·음성검증(§9.6)을 method-sink·frozen-auto 로 치환. 두 개념 모두 타 위치(`two-hop-boundary` 케이스 + `mutation-check.sh`)서 상설 회귀되므로 AC#1 "상설 회귀 픽스처로" 충족. 다만 설계 §9 "매 리뷰마다 이 세트를 돌린다"를 `TEST_CASE_GROUP=adversarial` 단일 명령으로 해석하면 N홉경계·rig 이 그 그룹엔 없음 → 후속에 `two-hop-boundary` 를 `adversarial` 그룹에 편입하면 §9 세트가 한 명령으로 완결(ergonomics·비차단).
- **O-2**: dynamic-coverage 는 `hops:1` 이라 helper(`check_permission`)가 hop2 로 hop 한계+getattr 이중원인으로 미발화. §9.3(사거리 내 동적 호출이 coverage.unevaluated 로 노출) 충족하나, `hops:2` 변형을 두면 "미발화 유일 원인=getattr" 대조가 더 순수. 비차단 강화 제안.

상세: `review-notes.md` TASK-025(D-057) 절 · `summaries/2026-07-16.md`.

## D-058 (2026-07-16) TASK-026 킷에 MVP-2 반영 — 역도달성 게이트 배선 — 리뷰 **통과** + Claude main 머지 (킷 v0.2-mvp2)

**대상 impl**: `9e04c13`(구현)·`259d49e`(handoff/summaries), 브랜치 `codex/2026-07-16-task026-kit-mvp2`. 킷 스냅샷 태스크 — **dev 쪽(`.harness/*`·`policies/*`·`docs/*`·`tests/*`) 무접촉 확인**(`git diff origin/main -- .harness policies docs tests …` 공백).

**델타**: ① sync 산출물 — `kit/gates/*` 16종(dev와 **전량 바이트 동일** `cmp` 확인)·`kit/tests/`(dev tests 와 동일 + 킷 전용 `run-entrypoint-tests.sh`만 추가) ② 손작성 — `kit/run.sh`(3층 배선)·`kit/sync-from-dev.sh`(sink-registry·진입점테스트 보존)·`kit/manifest.yaml`(13→16)·`kit/README.md`·`kit/selftest.sh`(문구 16종)·`kit/tests/run-entrypoint-tests.sh`(+2 케이스)·`kit/policies/sink-registry.yaml`(설계 §3.1 기본본) ③ `collab/questions/Q-0004.md`(비차단 질문).

**AC 대비 검수(TASKS.md TASK-026)** — 전부 실증 충족:
- **AC#1(sync 16종+정책)**: dev=16 kit=16 카운트 가드 + 내가 직접 `cmp` 로 16종 바이트 동일 확인(개수 아닌 실내용). **sync 재실행 멱등** — worktree 에서 `sync-from-dev.sh` 재실행 후 `git status` clean = 브랜치 킷 내용이 실제 sync 산출물이며 sink-registry·진입점테스트 보존 로직 실작동.
- **AC#2(4번째 판정층 배선)**: `run_gate "check-indirect-impact" "0 2" … "$RANGE" --sensitive-zones --sink-registry --repo .` — 게이트 argparse(위치 range·`--sensitive-zones`·`--sink-registry`·`--repo`)와 정확 일치. 게이트는 exit 0/2 만 방출(차단 금지 불변식·예외도 catch-all 로 2) → 허용 `0 2` 정합, 비정상 exit/traceback/timeout 은 `RUN_FAILED`→2 정규화. 최종 = `max(카드3축, 능력, 간접영향, 정책)` — `indirect_exit=1` 분기는 도달불가 방어코드(무해). `HAS_RANGE=0` 이면 fail-closed 승인요구+`ANALYSIS_FAILURES` (fresh 재현 ✓).
- **AC#3(--policies 일관+부재 fail-safe)**: `--policies` 처리 후 `SINKS="$POL/sink-registry.yaml"` 재계산 + 필수 4정책 존재검사 → 부재 시 exit 2 "필수 정책 파일 없음"(조용 통과 금지). fresh 재현 ✓(아래 ④·진입점 `missing-sink-registry`). ※ 설계 §3.1 은 게이트 수준 "파일 부재=정상"이나 킷 수준은 AC#3 이 명시적으로 fail-safe 요구 — 킷이 기본본을 동봉하므로 정합(의도된 차이).
- **AC#4(manifest·README)**: manifest 판정7+추출7+도구2=16·`check-indirect-impact`(L3)·`extract-sinks/callgraph` 추가·정책 목록에 sink-registry·v0.2-mvp2. README 게이트표·§알려진갭 4번("MVP-2 개발 중"→반영 완료)·"반영된 MVP" MVP-2 갱신.
- **AC#5(selftest/진입점 간접층 검증)**: 진입점 신규 2케이스(`indirect-impact-approval`: 대상 repo 자체 sink-registry(enforcing)로 sink 의존함수 수정→exit 2+"indirect sink impact requires review" / `missing-sink-registry`) + 기존 9케이스 무회귀 11/11.

**적대적 검증(격리 worktree `wt-task026` · fresh 입력 + 음성검증 — 전부 직접 실행)**:
- **selftest 전량 재현**: `kit/selftest.sh` PASS — 러너 91/91(adversarial 7/7 포함)·진입점 11/11·mutation 151+정책 mutation+metamorphic+negative.
- **fresh ① 킷 기본정책 경로**(--policies 없음·registry 빈 상태): frozen `**/settlement/**` 자동 sink 의 의존함수(`app.utils.normalize`) 수정 → 간접영향=2·최종 exit 2·경로 `transfer -> normalize` 출력. **진입점 테스트에 없는 기본정책 경로까지 발화 확인.**
- **fresh ②** 동일 repo sink 무관 함수 수정 → 간접영향=0·최종 PASS(항상-2 아님).
- **fresh ③ HAS_RANGE=0**(`run.sh HEAD`): 간접영향층 `range_required` fail-closed=2.
- **fresh ④ --policies+hops 정책값 실배선**: 대상 repo 자체 registry(enforcing `app.gateway.pay`), 2홉 체인 sink→a→b 에서 b 수정 — `hops:1`→PASS / `hops:2`→발화(`pay -> a -> b`·reviewer=sec-team 라우팅). 정책값이 킷 경유로 실제 판정 구동.
- **fresh ⑤ 분석실패 fail-closed**: head 에 문법오류 `.py` → `fail_closed`(callgraph·sinks errors)+exit 2.
- **rig-and-revert(음성검증)**: (A) `run.sh` 에서 `indirect_exit` 를 0 고정(배선삭제 시뮬) → 진입점 `indirect-impact-approval` **단독 FAIL(10/11)**·fresh ① 이 오판 PASS = 신규 가드 load-bearing·타층 중복 아님. (B) `check-indirect-impact.py` 삭제 → `gate_missing` fail-closed exit 2(조용통과 없음). (C) 기대값 변조(expected 2→0) → 해당 케이스 FAIL = 항상-PASS 아님.

**보수적 개발(§1)**: 델타 = `kit/*`(Codex 소유)+`collab/questions/`+handoff/summaries 만. Claude 소유 파일·dev 게이트/정책/테스트 무접촉. sync 산출물 외 무관 리팩터 없음. scope-creep 없음.

**Q-0004 처리**: `policies/sink-registry.yaml` dev 원본(설계 §3.1 기본값·킷 동봉본과 바이트 동일)을 Claude 가 이 리뷰 브랜치에서 추가 — 단일 소스 정합 회복. `collab/answers/A-0021.md`·Q-0004 status=answered.

**머지 판정(D-007)**: 킷 러너 verdict 배선+스냅샷 동기화+빈 sink 기본본 = **비민감**(TASKS.md TASK-026 비고 명시: "민감도는 기존 킷과 동일" · 정산/인증/암호화/DB/infra 코드 무해당 · 3층은 승인 상한·차단 금지). 구현자(Codex)≠머지자(Claude) → **Claude `main` 머지·push.**

**비차단 관찰(§2B 필수질문=아니오 — 과차단 방향이거나 문서 정비)**:
- **O-1 (main 기존결함·비델타)**: `kit/run.sh` 의 `INTENT_ARGS=()` 빈 배열 + `"${INTENT_ARGS[@]}"` 가 **bash 3.2(macOS 기본)에서 `set -u` unbound variable 로 크래시(exit 1)** — 대상 repo 에 `change-intent.yaml` 이 **없으면** 항상 재현(fresh 실증). run.sh 가 "intent 없음 — 층 생략"을 공식 지원 경로로 안내하는데 그 경로가 구식 bash 에서 죽는다. 과소탐지 아님(과차단 방향·조용 통과 없음)이라 비차단이나, 진입점 스위트가 전 케이스에 intent 를 만들어 **사각지대**. → **차기 킷 정비 AC 로**: `${INTENT_ARGS[@]+"${INTENT_ARGS[@]}"}` 패턴(또는 bash4 요구 명시) + intent 부재 진입점 케이스 추가.
- **O-2**: 킷 전용 자산(`run-entrypoint-tests.sh`·sink-registry 기본본)이 `rm -rf` 대상 디렉토리 안에 살고 snapshot-복원 패턴으로 보존됨 — 현재 실작동(멱등 확인)하나 킷 전용 파일이 늘면 취약. 차기에 `kit/kit-local/` 류 분리 검토(ergonomics).
- **O-3**: frozen 자동 sink 의 reviewer 가 zone 에 `required_approval` 없으면 `tool_owner` 폴백(fresh ① 관찰) — 킷 기본 sensitive-zones 의 frozen zone 들엔 `required_approval` 이 없어 배포 기본값에서 간접영향 라우팅이 전부 tool_owner. 게이트 로직은 정직(D-056 검증)하나 킷 기본 정책 문서/주석에 "frozen zone 에 required_approval 명시 권장" 추가하면 라우팅 품질 개선(정책면 후속·Claude 몫).

상세: `review-notes.md` TASK-026(D-058) 절 · `summaries/2026-07-16.md`.

## D-059 (2026-07-16) TASK-027·028 설계 — `expected_paths` 부재 탐지(패치 생존성) — Claude 설계 확정

**발단(형 질문 2026-07-16)**: 벤더-브랜치 전략(오픈소스 origin 갱신 → patch/custom 브랜치 재적용)에서 "패치 브랜치에 **명시된 파이썬 파일들이 실제로 수정됐는지**"(Q2)를 하네스로 볼 수 있나. 형 제안: "민감경로에 A.py B.py 정의해두면 되지 않나."

**판단 = 민감경로(존재 탐지)로는 Q2 를 못 막는다(논리 실증)**:
| 상황 | 민감경로(존재 탐지) | Q2 가 원하는 것 |
|---|---|---|
| 패치 **적용됨**(A.py 변경) | 발화(중복·불필요) | "정상" 확인 |
| 패치 **유실됨**(A.py 미변경) | **침묵**(diff 에 없어서) | **여기서 발화해야** |
→ 존재 탐지는 *정확히 필요한 순간(패치 유실)에 실패*한다. 필요한 건 **반대 방향 = 부재 탐지**(선언한 파일이 diff 에 **없으면** 발화). 현행 하네스 전 게이트가 존재 탐지뿐이라 이 층은 **완전 신규 방향**.

**설계 결정**:
- 신규 **선택** 필드 `change_intent.expected_paths`(allowed/forbidden 과 대칭). 미선언=기존 동작 완전 동일(**기본 off·하위호환** — #1 회귀 가드).
- 시맨틱: 각 항목 "변경 파일 중 **≥1 매칭이면 충족**"(기존 `match_glob` 재사용). 불충족 항목 → `missing_expected` → 최소 `approval_required`.
- **판정 상한 = approval_required(차단 없음)**: 선언 문제는 확인 요청이지 차단 사유 아님(TASK-021 #3 계보). 빈 diff + expected 선언 → 전부 missing → approval(패치 전면 유실의 핵심 신호).
- **카드 미러링 필수**: 킷 `run.sh` 는 `check-change-intent` 단독이 아니라 `generate-change-evidence`(카드)를 intent 층으로 호출(D-058 확인) → 카드 인라인 intent 로직에도 `expected_paths` 반영해야 킷에서 작동. 이게 TASK-028(킷 반영)의 전제.

**적대적 자기검토(§2B — 내 설계를 깨보기)**:
- **glob 거친 보증**: `vendor/**` 는 "그 아래 아무 파일 1건 변경으로 충족" → 실제 패치 코드파일 미변경이어도 무관 README 변경으로 통과 가능. → **리터럴 경로 권장**을 템플릿/출력/카드 coverage 에 명시(TASK-019 정직화). cap 이 approval 이라 거친 오탐은 비파괴(사람 확인).
- **rename/delete**: name-status R=목적지만 changed, D=경로가 changed 로 잡혀 수정/삭제 미구분 → 코너 오탐 가능하나 방향은 안전(과차단·approval cap). 문서화로 처리.
- **거버넌스 구멍 질문(§2B 필수질문=아니오)**: 이 기능은 **탐지를 추가**할 뿐 어떤 통제도 약화 안 함. 유일 false-pass 경로 = expected_paths 미선언(작성자 선택·allowed_paths 와 동일 성격) 또는 glob 과대매칭(문서화된 한계). 차단 없음·기본 off → 과차단/우회 위험 없음.
- **최우선 회귀 가드 = 하위호환**: expected_paths 없을 때 현행 91/91 무변화. TASK-027 #1.

**구조**: TASK-027(dev: `check-change-intent`+카드 미러링+픽스처, Codex 저자·Claude 리뷰·비민감→머지) → TASK-028(킷 스냅샷 sync + 진입점 실증, run.sh 무변경). **최종 = MVP-2 킷에 부재 탐지 반영**(형 요구 "최종은 그걸 반영한 MVP2").

**역할 경계**: 게이트 코드는 Codex 저자(Claude 미작성 — 상호견제). 본 결정·TASKS.md AC 는 Claude 정책면 산출. dev 게이트 확장(intent 층)은 비민감 → 통과 시 Claude 머지(D-007).

## D-060 (2026-07-16) TASK-027 리뷰 통과 — `expected_paths` 부재 탐지 dev 게이트 · Claude main 머지

**대상**: `codex/2026-07-16-task027-expected-paths` (구현 `d8e6fa4` · 헤드 `308fc12`) vs main `c5367e6`. 델타 = `check-change-intent.py`(+20) · `generate-change-evidence.py`(+30, 카드 미러링) · 정책 템플릿/예시 주석 · 카드 템플릿 키 3종 · 픽스처 4종 + 카드 통합 케이스 · 러너 단언 · handoff/summaries.

**판정 = 통과 · 비민감 → Claude 머지 (D-007, 구현자 Codex ≠ 머지자 Claude)**

### AC 실증 (전부 격리 worktree에서 직접 실행)
- **AC#1 (하위호환·무회귀 — 최우선)**: `run-tests.sh` **96/96 PASS**(기존 91 전부 + 신규 5). `expected-none` 픽스처 = 미선언 무영향 상설 실증. fresh: 빈 diff + 미선언 → exit 0(TASK-001 #6 보존).
- **AC#2 (부재 탐지)**: `missing_expected` = 변경 파일 중 ≥1 매칭 없는 패턴만, 기존 `match_glob` 재사용, `sorted()` 정렬. missing → `approval_required`/exit 2 상한 — **missing 으로 인한 exit 1 경로 코드에 없음**(차단금지 불변식).
- **AC#3 (우선순위)**: fresh ADV — forbidden+missing 동시 → **blocked/exit 1 우선**(missing 은 JSON 병기). 빈 diff + 선언 → 전부 missing → exit 2 (픽스처 + fresh `**` 변형). 선언 없으면 빈 diff pass.
- **AC#4 (출력·결정론)**: JSON `expected_paths` 에코 + `missing_expected` 정렬, 텍스트 `missing_expected: {pattern}` 라인 실행 확인, 2회 실행 `cmp` 바이트 동일.
- **AC#5 (시맨틱 정직성)**: 게이트 텍스트 `expected_paths_semantics` 라인 + 카드 동명 키 + `checked` 문구 + 템플릿/예시 주석 3파일. **한계를 문서만이 아니라 실증**: rename R100 에서 origin 경로 선언 → missing/exit 2(목적지만 changed — 과탐 방향 안전) · 목적지 선언 → 충족 / delete D → 경로 변경으로 충족 / glob `vendor/**` → 무관 하위 파일 1건으로 충족(거친 보증 = D-059 수용 한계).
- **AC#6 (픽스처+음성검증)**: 4종 문자 그대로 + `evidence-expected-missing`(카드 `reasons_contain`·`schema_keys_match_template`). **rig-and-revert 3종**: ① intent 게이트 verdict 에서 `or missing_expected` 제거 → `expected-missing`·`expected-empty-diff` **단독 FAIL(94/96)** ② 카드 `verdict_and_exit` 에서 제거 → `evidence-expected-missing` **단독 FAIL(95/96)** = 미러가 독립 load-bearing(타 케이스에 안 가려짐) ③ 기대값 변조(missing→[]) → FAIL = 항상-PASS 아님. 원복 96/96. `mutation-check` **PASS(161 = 기존 151 + 신규 10 편입)**.
- **AC#7 (카드 미러링 — TASK-028 전제)**: `intent_result`(status fail 편입)·`verdict_and_exit`·`build_reasons`(`missing_expected:{pattern}`)·`executed_gate_records` 문구·**fail-closed 예외 카드 스키마까지** 신규 키 반영 + 템플릿 동시 개정. fresh: **빈 diff + 선언 → 카드 exit 2**(픽스처 미커버 핵심 신호 경로 직접 실증) · frozen+missing → blocked 우선 + reasons 병기.

### 프로덕션 경로 (fresh git repo · ref 모드)
6-디렉토리 합성 repo `base..HEAD`: 패치 유실(선언 파일 미변경) → `missing_expected` 발화/exit 2 · 패치 존재 → exit 0. 부수 확인: 2-디렉토리 toy repo 에서 exit 2 는 TASK-021 광역 커버리지 층(100%≥80)의 정상 발화였음 — 층 간 독립·간섭 없음 실증.

### 보수적 개발 (COMMON-RULES §1)
델타 전부 태스크 범위. Claude 소유 `policies/change-intent.{template,example}.yaml`·`templates/change-evidence.template.yaml` 접촉은 **AC#5·#7 명시 위임**(scope-creep 아님). `APPROVAL_REQUIRED` 텍스트 일반화("변경 의도 확인이 필요합니다")는 다원인(oos/broad/missing) 정합 — 무관 리팩터 아님. `kit/` 무접촉(TASK-028 분리 준수). 게이트 코드 = Codex 저자(상호견제 보존).

### 비차단 관찰 (§2B 필수질문 "거버넌스 구멍?" = 전부 아니오 — 과탐/과차단 방향, under-detection 아님)
- **O-1**: 리터럴 **디렉토리** 경로 선언(`vendor/foo`) 은 파일 경로와 전체일치 불가 → 영구 missing → approval. 사람이 보게 되는 과탐 방향 + 시맨틱 문구가 리터럴 *경로* 권장이라 표면화됨. 차기 문서/스키마 검증 후보.
- **O-2**: `expected_paths` 비문자열 원소(`[123]`) → 크래시 → blocked exit 1(과차단·allowed/forbidden 기존 동일 거동) / 스칼라 문자열(리스트 아님) → 문자 단위 해석 → approval(과탐). 차기 intent 스키마 타입 검증 일괄 후보(신규 결함 클래스 아님).
- **O-3(미용)**: 중복 선언 시 `missing_expected` 중복 에코.
- **under-detection 부재 논증**: 리터럴 경로는 세그먼트별 `fnmatchcase` 정확 일치라 거짓 충족 불가. 유일 false-pass = glob 과대매칭(D-059 가 문서화로 수용한 설계 한계) 또는 미선언(작성자 선택·기본 off 설계).

### 하류 영향 (TASK-028)
킷 `run.sh` 는 카드 게이트를 intent 층으로 호출(D-058) → 카드 미러링이 rig B 로 독립 load-bearing 실증됐으므로 `sync-from-dev.sh` 바이트 복사만으로 킷 부재 탐지 작동 전제 성립. `run.sh` 배선 변경 불필요(신규 판정층 아님 — 기존 게이트 내부 확장) 확인.

**멱등성**: `d8e6fa4`·`308fc12` 재처리 금지. **다음 = Codex TASK-028**(킷 스냅샷 sync + 진입점 부재 탐지 케이스). 상세 `review-notes.md` TASK-027(D-060) 절.

## D-061 (2026-07-16) MVP-3 다국어 확장 설계 — 언어 어댑터 아키텍처 (Java/Spring 우선) — Claude 설계 + 형 방향승인

**발단(형 요구 2026-07-16)**: "파이썬 말고 프론트랑 Java/Spring 코드도 똑같은 하네스로 구성" 기획/설계.

**형 문답으로 확정된 방향**:
- **언어 우선순위 = Java/Spring 먼저**(형 선택). 근거: 은행 핵심(정산·인증) 로직이 Spring 백엔드·Spring 어노테이션이 민감도 개념과 1:1·정적타입. 프론트는 후속(저위험 UI·단 XSS 실질위험).
- **파서 = tree-sitter 백본**(형이 "각각 뭔지 모르겠다" → 설명 후 권고 수용). **Python 은 `ast` 유지**(형 질문 "파이썬도 tree-sitter로 바꾸나" → **아니오** 확정).

**핵심 설계 결정**:
- **seam = 공통 IR(중간표현) 4종 + 확장자 라우터**. 판정 엔진 하나에 언어별 추출기만 갈아끼움. "N언어 × 4추출기 → 판정엔진 1개"(판정 로직 안 늘어남).
- **파일별 라우팅**(언어 모드 통째 선택 아님 — 한 PR 에 다언어 혼재 가능). 확장자→어댑터 정책 매핑. 미지원 확장자 = 경로층만 + **coverage 정직 노출**(형 질문 "자바껄 돌리는지 파이썬걸 돌리는지 어떻게 아나" → 확장자 자동분배로 답).
- **Python `ast` 무개조**(형 질문 "지금 기능 다 보완하나" → 3분류로 정직 답: 🟢경로층 이미 작동 / 🟡깊은층 재구현 / 🔴간접영향 Java 에서 더 약함·정직노출).
- **Spring 어노테이션 카탈로그**(신규 정책 아티팩트) = Java 판 능력 카탈로그. `@PreAuthorize`→protected 등. 은행 도메인 최고 ROI.

**정직한 한계(§2B — rubber-stamp 아님, 설계 §5)**:
- **간접영향(L3)은 Java 에서 Python 보다 *더 불완전***: DI(`@Autowired`)·AOP(`@Transactional` 프록시)·인터페이스 다형성 → 정적 콜그래프가 런타임 호출 더 놓침. "동등"이 아니라 "더 약함" → coverage.unevaluated 노출. "다 커버"는 거짓.
- TS 타입 미해소(tree-sitter CST)·동적(리플렉션/eval) 완전복원 불가 — 존재만 잡고 값추정 안 함(현행 Python 원칙 동일).
- tree-sitter = 외부+네이티브 의존 한 겹 위(prebuilt wheel·실부담 pyyaml 수준). 다중런타임 네이티브 툴과 급 다름.

**태스크 구조**: MVP-3 = TASK-029(J0 seam/라우터/tree-sitter 도입) → 030(J1 Java 인벤토리) → 031(J2 @Gov+Spring 카탈로그) → 032(J3 Java 능력). 이후 W1(프론트)·X(콜그래프→간접영향) 후속. 각 게이트=Codex 저자·Claude 리뷰(비민감 분석/추출층→머지 D-007). 설계문서 = `docs/multi-language-adapter-design.md`.

**마일스톤 정리**: 다국어를 **MVP-3 로 확정**. 구 "MVP-3 후보"였던 cross-commit 누적은 **후속 마일스톤으로 재이월**(무상태 모델 유지 위해).

**역할 경계**: 게이트/라우터 코드는 Codex 저자(Claude 미작성·상호견제). 본 결정·설계문서·TASKS.md AC 는 Claude 정책면. **순서: TASK-027/028(expected_paths) 먼저 구현 대기 중 → 그다음 MVP-3.**

## D-062 (2026-07-16) MVP-3 설계 재검토 — 파이썬 동등성(parity)을 최우선 합격기준으로 격상

**발단(형 지시)**: "전체적으로 상세 재검토 + **가장 중요한 건 파이썬과 동일한 성능(parity)**." → parity 를 다국어 확장의 **1순위 제약**으로 승격하고 설계를 그 렌즈로 재검토.

**재검토 결과 — 층별 parity 판정**:
- 🟢 **경로층**(의도·zones·expected_paths·정책·maturity): 언어무관 → parity 100% 공짜.
- 🟢 **인벤토리·헝크매핑·classify**: tree-sitter 가 함수경계·라인범위·어노테이션·시그니처 다 제공 → 탐지 parity 직행. 오버로드 매칭은 `(name,signature)` 키(Python order_key 계보).
- 🟢 **주석(@Gov)+능력**: 구조·이름 기반이라 정보량 동일 → parity 달성. Java 는 Spring 카탈로그 **초과분**(더 강함). 단 **엄밀성 parity** 위해 Java 도 자기 난독 우회세트(리플렉션·문자열SQL) 를 Python getattr(D-024~027) 급 깊이로 막아야 함.
- 🔴 **L3(간접영향)만 parity 가 공짜 아님**: Java 관용구(인터페이스+DI+AOP)가 호출부-구현 분리 → 이름기반 콜그래프가 실제 엣지 놓침. 앞 초안(D-061)은 이걸 "Java 는 더 약함"으로 방치 → **parity 요구 하에선 결함**.

**핵심 설계 변경 — L3 을 "약함 방치"에서 "보수적 과대근사로 안전 parity"로**:
- 인터페이스 호출 → repo 내 **모든 구현체 엣지** · `@Autowired`→그 타입 모든 구현 · `@Transactional`/AOP 프록시→직접엣지. 결과 = 실제 런타임 엣지의 **상위집합(superset)** → **진짜 엣지 안 놓침 = 안전 방향 parity**(과탐은 승인상한이라 감내). tree-sitter `implements`/`extends` 열거로 가능(네이티브 불필요).
- **정밀 parity**(과탐 감축)는 후속 네이티브 심볼솔버(JavaParser/Spoon) 옵션 — Java 정적타입이라 도입 시 오히려 Python L3 능가 가능.

**parity 의 조작적 정의(4축) + 강제장치**(설계 §1.5 신설):
1. 탐지 동등(동일 위험→동일 verdict) 2. 엄밀성 동등(언어별 고정 적대세트+음성검증+fail-closed) 3. 정직성 동등(coverage 노출) 4. **안전 방향 동등**(불완전 시 과탐 쪽·과소탐 절대 금지 = 놓침은 parity 위반).
- **강제장치 = 교차언어 등가 픽스처**(`tests/parity/`): 각 위험클래스 py판+java판 쌍 → 동일 verdict 단언 + 음성검증. 하나라도 어긋나면 parity 회귀 FAIL. "동일 성능"의 **자동 증명**(주장 아님).

**기타 재검토 보정**:
- **결정성 parity**: tree-sitter 문법 버전 pin + 카드에 언어별 파서버전 기록(TASK-019 AC#3 계보·재현성 계약).
- **IR 중립화**: `decorators→annotations`·`decorator_start_line→signature_start_line`·`signature` 필드 추가(classify·오버로드용). Python 어댑터는 이름만 매핑(값 동일).
- **라우터 additive**: Python 골든패스 무개조 — 라우터는 `.py` 를 기존 추출기로 위임(현행 96/96+뮤테이션 보존).
- **Java import 뉘앙스**: `java.lang.*`(Runtime) 암시적 import → import-backstop 대신 call 신호로 커버(비대칭 픽스처 고정).

**반영**: 설계문서 §1(원칙에 parity 최우선 추가)·**§1.5 신설**·§3.1(IR 중립화)·§3.3(문법pin)·**§5 재작성**(L3 과대근사). TASKS.md MVP-3 intro·공통·TASK-029(#6 parity 기반장치)·031(#7 parity 픽스처)·032(#2 import뉘앙스·#6 parity 픽스처). **게이트/픽스처 코드는 여전히 Codex 저자**(Claude 미작성). 착수순서 불변: TASK-028 → MVP-3.

## D-063 (2026-07-16) TASK-028 리뷰 — 스냅샷 동기화 통과, 진입점 부재탐지 케이스 **보정요청(R-1)** · 머지 보류

**대상**: `codex/2026-07-16-task028-expected-paths-kit` (`c858c9b` 구현 + `7b3faf9` 인계). 킷에 `expected_paths` 부재 탐지 반영(D-059·D-060 계보).

**통과 확인(재작업 불요 — 격리 worktree 실증)**:
- **AC#1 ✓** 게이트 17파일(16종 .py+README) dev↔kit **md5 전부 동일**, main 의 D-060 승인본과도 동일(게이트 내부 재리뷰 불요) · policies/templates/tests 트리 **바이트 동일** · `sync-from-dev.sh` 재실행 → working tree 클린(멱등) · 게이트수 dev=16 kit=16.
- **AC#3 ✓** manifest `0.2.1-mvp2`·부재탐지 명기·`detects:` 키는 소비자 없음(안전) · README 능력+시맨틱 정직 문구(리터럴 권장·glob 거친 보증·rename/delete 한계)+MVP-2 라인.
- **AC#4 ✓** `kit/selftest.sh` **96/96 + 진입점 12/12 + mutation 161 PASS** 재현(bash 3.2 환경 — 크로스셸 보너스) · `kit/run.sh` 무접촉 diff 실증.
- **selftest git init(AC 밖 신규)**: 정당 — 제거 rig 시 **정확히 신규 2픽스처만** FAIL(81/83·타 케이스 무영향) = load-bearing. dev 러너도 git repo(저장소 루트)에서 돌므로 환경 정합이고, 비-git fallback(변경파일→top-dir 100%)은 **과탐 방향**이라 마스킹 아님.
- **fresh E2E(픽스처 밖)**: 격리 missing→2(**단독 원인** — out_of_scope 0건)·충족→0·frozen+missing→1(차단 우선·missing reasons 병기)·no-range→2(층별 fail-closed)·`--policies` 오버라이드 frozen→1·`--policies` 부재 디렉토리→2·intent YAML 파손→1(카드층 의도된 최강 fail-closed — dev 기존 거동·D-060 범위)·카드 2회 실행 `cmp` 동일.
- **보수적 개발 ✓**: `kit/*`+handoff+summaries 만 접촉·무관 리팩터 없음·scope-creep 없음.

**R-1 보정요청 — 진입점 케이스 `expected-path-missing-approval` 이 load-bearing 아님** (상세 `collab/answers/A-0022.md`):
- 선언 수정(change-intent.yaml)과 코드 변경이 **같은 커밋** → diff 에 intent 파일 포함 → allowed 밖 = `out_of_scope:change-intent.yaml` **항상 동반**(카드 실측) → exit 2 이중 원인. 카드 grep 2종은 **빈 키 에코**(`missing_expected: []`)와 **`expected_paths` 에코**에도 매칭.
- **결정 실증**: 킷 카드 게이트 missing 계산 무력화(키 에코 유지) rig → **진입점 12/12 PASS 유지**(기능이 죽어도 침묵). 러너 `evidence-expected-missing` 은 FAIL(82/83) → 오늘은 방어층 존재.
- **§2B 필수질문 = 예**: `sync-from-dev.sh` 는 `kit/tests/` 를 dev 로 덮어쓰고 진입점 스위트만 스냅샷 보존 → **진입점 = sync 를 살아남는 유일한 킷 소유 가드**. 그 가드가 이 기능에 대해 비어 있음 = AC#2 목적(신규 가드 load-bearing) 미충족 → 비차단 불가, 보정요청.
- **보정안(실증 완료)**: ① 선언을 base/선행 커밋으로 분리(마지막 커밋 = 코드 파일 단독 — 이 구성은 missing 단독 원인 exit 2, detection-kill rig 에서 exit 0→FAIL = load-bearing 회복) ② grep 을 `missing_expected:app/required_patch.py`(reasons 라인)로 강화 ③ 기대값 rig 유지 + detection-kill rig 기록.

**비차단 관찰**: **O-A** intent 파일 없는 repo + bash<4.4(macOS 기본 3.2) → `run.sh` `INTENT_ARGS[@]: unbound variable` 크래시(exit 1·카드 미생성) — **main 재현 = 기존 결함·TASK-028 도입 아님**·과차단 방향 → **TASK-033 등록**으로 명시 가드. **O-B** `run.sh` 콘솔 1층 요약에 missing_expected 미표기(카드엔 있음) → TASK-033 병합. **O-C** manifest `detects:` 소비자 없음.

**D-007 처리**: 코드 브랜치 **머지 보류**. 리뷰 기록(decisions·review-notes·A-0022·TASKS TASK-033·summaries·handoff)은 `claude/2026-07-16-review` → main 머지. 재제출 시 **보정 커밋만** 재리뷰(멱등 — `c858c9b`·`7b3faf9` 재처리 금지).

## D-064 (2026-07-16) TASK-028 보정(0f4d1a0) 재리뷰 — **통과** · Claude main 머지 (킷 expected_paths 스냅샷 완결)

**대상**: `codex/2026-07-16-task028-expected-paths-kit` 보정 커밋 `0f4d1a0`(+docs `d57b086`)만 — 멱등 원칙(`c858c9b`·`7b3faf9` 재처리 안 함, D-063 통과분 재작업 불요).

**보정 델타 확인(한 줄씩)**: `kit/tests/run-entrypoint-tests.sh` 단일 파일 3+/2-.
- ① `expected_paths` 선언을 **선행 커밋**(`expected-declaration`)으로 분리, 마지막 커밋은 `git add app/service.py` **명시 경로**로 `app/service.py` 단독 — `HEAD~1..HEAD` 에 intent 파일 미포함 → `out_of_scope` 동반원인 제거. (A-0022 보정안 ① 정확 구현. 기존 `git add .` → 명시 add 전환도 미래 오염 방지로 적절.)
- ② 카드 grep 을 `missing_expected:app/required_patch.py` **reasons 정확 문자열** 1개로 — 빈 키(`missing_expected: []`)·`expected_paths` 에코와 매칭 불가(필드 에코는 YAML 리스트 개행/콜론 뒤 공백이라 비매칭·게이트 reasons 포맷 `missing_expected:{pattern}` 과 정확 일치 확인). (보정안 ②)
- ③ handoff·summaries 에 기대값 rig + **detection-kill rig** 양쪽 기록. (보정안 ③)

**격리 worktree 실증(전부 fresh 재실행)**:
- **진입점 12/12 PASS**(fresh) · `kit/selftest.sh` **96/96 + 진입점 12/12 + mutation 161 PASS** · `sync-from-dev.sh` 재실행 → working tree 클린(멱등·보정된 진입점 스크립트 sync 생존 확인).
- **detection-kill rig(결정타)**: 킷 카드 게이트 `intent_result` 의 missing 계산을 `[]` 고정(키 에코 유지) → `expected-path-missing-approval` **단독 FAIL(11/12)**·카드 reasons [] 확인 → **load-bearing 회복**(D-063 에서 12/12 유지되던 R-1 결함 해소). 원복 후 clean.
- **fresh 픽스처 밖 입력**: 다른 패턴 2종(`app/must_touch.py`·`app/also_required.py`) 선언·코드단독 diff → exit 2 + reasons `missing_expected:` 2건·**out_of_scope 0건** = 단독 원인.
- **음성검증 2종(rig-and-revert·변조 적용을 count==1 assert 로 확인)**: 기대 rc 2→0 변조 → 단독 FAIL(11/12) / grep 문자열 변조(`DOES_NOT_EXIST`) → 단독 FAIL(11/12) — rc 축·카드증거 축 각각 load-bearing.

**보수적 개발 ✓**: `0f4d1a0` = 킷 테스트 1파일(Codex 소유)·`run.sh`/게이트 무접촉(커밋 diff 실증), `d57b086` = handoff/summaries 만. 무관 리팩터·scope-creep 없음 — A-0022 최소 델타 그대로.

**대안 검토**: 내가 짜도 동일 구성(A-0022 에서 사전 실증한 그 형태). 미세 보강 여지 1건 = 케이스에 `out_of_scope` reasons **부재 단언**을 추가하면 미래에 케이스 구성 변경으로 이중 원인이 재유입되는 드리프트도 자동 검출 — 현 구성에선 단독 원인이 실증됐고 케이스 수정 자체가 리뷰 대상이므로 **비차단 관찰(O-D)**, TASK-033 진입점 케이스 추가 시 함께 반영 권고(§2B 필수질문=아니오 — 현재 가드는 살아 있음).

**D-007 처리**: **통과 + 비민감**(킷 테스트 하네스 — 정산/인증/암호화/DB/infra 무해당) → Claude 가 `claude/2026-07-16-review` 에서 머지(`d1e3c94`) 후 main push(구현자 Codex≠머지자 Claude). **TASK-028 완결** — 다음 = Codex **TASK-033**(킷 run.sh 견고성 — 028 보정 통과가 선행조건이었음) 착수 가능, 이후 MVP-3(TASK-029~032). **멱등성**: `0f4d1a0`·`d57b086`·`d1e3c94` 재처리 금지.

---

## D-065 — TASK-033 킷 `run.sh` 견고성 리뷰: **보정요청**(합성 intent 주입 = 카드 위조 + 의도층 우회) · AC#2 정정 · TASK-034 등록 (2026-07-16, Claude)

**대상**: 브랜치 `codex/2026-07-16-task033-kit-run-robustness` · `8e6b54b`(구현)·`c8d8e7b`(docs). 델타 = `kit/run.sh`(+16/-4)·`kit/tests/run-entrypoint-tests.sh`(+31/-1)·handoff·summaries.

**판정 = 보정요청(R-1) · 코드 머지 보류.** 상세 = `collab/answers/A-0023.md`.

**제출 주장은 전부 재현됨**(격리 worktree·bash 3.2): 진입점 **13/13** · `kit/selftest.sh` **96/96 + 진입점 13/13 + mutation 161 PASS** · `bash -n` PASS · 임시파일 누수 없음(정상경로 tmp 증가 0) · 크래시 실제 소멸. **AC#3**(콘솔 `missing_expected` grep)·**AC#5**(D-064 O-D 병합 — `out_of_scope` 부재 단언) **수용**. **AC#1 전수점검**: run.sh 배열은 `INTENT_ARGS`·`ANALYSIS_FAILURES` 둘뿐 — 후자는 `[ "${#A[@]}" -gt 0 ]` 가드 뒤라 빈 확장 불가(추가된 `+` 가드는 무해한 방어).

**R-1 결함 — 크래시를 없앤 *방법*이 판정 의미를 바꾼다.** `run.sh` 가 intent 부재 시 `allowed_paths: ["**"]` **가짜 change-intent 를 합성해 게이트에 주입**한다.
- **① 카드 위조(정직성 위반)**: 게이트는 합성 여부를 모른다 → 카드 실측 `verdict: pass` · `intent_check.status: pass` · `changed_files[].in_allowed_paths: **true**`(선언이 없는데) · `coverage_statement.checked` 에 `check-change-intent: "changed paths against **declared** allowed_paths…"` = **선언 대조 수행을 명시 주장** · `reasons: []`. 합성 흔적 0(`policy_sha` 는 zones·routing 만). 대조군(합성 없음)은 정직: `verdict: blocked` · `reasons: ['의도 선언 누락…']` · **`coverage.checked: []`**. 정직한 "아무것도 검사 안 함"을 "3게이트 검사 완료"로 바꾼 것 = 조용한 통과 금지 원칙(TASK-019 계보) 정면 위반. **콘솔 "생략" 안내는 휘발성이고 감사 산출물은 카드다.**
- **② 의도층 우회 + bash≥4.4 탐지 회귀(fresh 적대입력 실증)**: 픽스처 밖 repo(`forbidden_paths: ["app/keys.py"]`·`expected_paths: ["app/must_patch.py"]`)에서 forbidden 수정 + expected 미터치 diff → **intent 존재 시 3판본 모두 exit 1 BLOCKED**. **`change-intent.yaml` 삭제 후**: main(bash3.2) = 크래시 exit 1·카드 없음(O-A) / main+안전관용구(**= bash≥4.4 에서 main 의 실동작**) = **exit 1 BLOCKED·카드 생성·정직** / **이 브랜치 = exit 0 PASS**. ⇒ **intent 파일 삭제만으로 forbidden_paths 차단 + expected_paths 부재탐지(TASK-027/028 패치생존성 층 전체)가 통과로 소멸.** 리눅스 CI 에선 크래시 수정이 아니라 **BLOCKED→PASS 판정 완화 회귀**. **under-detection → §2B 필수질문 = 예 → 비차단 불가.**
- **③ AC#1 안전관용구가 dead code**: 합성 때문에 `INTENT_ARGS` 가 절대 비지 않음 → 관용구가 빈 배열로 확장될 일이 없다. **RIG1**(관용구만 원복·합성 유지) → **13/13 PASS 유지** = AC#1 가드가 죽어도 아무 테스트도 안 움. **RIG2**(합성만 제거·관용구 유지 = AC#1 최소수정) → 크래시 소멸·카드 생성·전층 실행되나 신규 케이스만 **FAIL(12/13)** = **실제 크래시를 막는 건 관용구, 테스트가 지키는 건 합성**(가드-테스트 불일치).

**AC#2 정정(내 오류 — Claude 책임)**: AC#2 가 요구한 "intent 없는 repo → **exit 0**" 의 전제가 틀렸다. D-063 O-A 는 exit 1 을 순수 크래시 산물로 봤으나, **bash≥4.4 에선 크래시 없이 게이트가 돌아 의도적으로 `blocked`(exit 1)** 를 낸다(`load_intent`→`FileNotFoundError`→정직 카드). Codex 는 틀린 AC 를 충실히 구현한 것. **크래시 결함의 실체 = 카드 미생성·2/3/메타층 미실행·판정 없는 죽음** 이 셋뿐 → **판정은 건드리지 않는다**. → 정정 AC#2 = "크래시 없이 게이트 자신의 판정이 그대로 흐른다(현행 `blocked`/exit 1·정직 reasons·카드 생성·전층 실행)". `TASKS.md` 반영.

**대안 검토 — "내가 짠다면"**: RIG2 그대로. `run.sh` 델타 = **안전관용구 1줄 + 콘솔 grep 1줄**(+문구 정정). 합성 파일·mktemp·정리로직 전부 불필요 = 더 단순·더 정직·우회 없음. 부수로 151행 `(change-intent.yaml 없음 — 의도이탈 층은 생략)` 은 **실동작과 모순**(층은 생략 안 되고 게이트가 차단 판정) → 사실 문구로 정정 요청(표시만·판정 무변경).

**보수적 개발 평가**: 파일 범위 자체는 AC 산출물(`kit/run.sh`+진입점 테스트+docs)로 정확·무관 리팩터 없음·dev 무접촉 → **scope-creep 없음**. 다만 **blast radius 가 의도보다 큼**(크래시 수정 요청 → 판정 완화 동반) = `COMMON-RULES.md` §1 의 over-reach 축에 해당.

**하류 영향**: 킷은 배포 최전선이고 카드는 CI 감사 산출물 → 위조 카드는 사람 리뷰어가 검출 불가. 또 TASK-034 가 미선언을 approval 로 정규화할 때, 합성 주입이 남아 있으면 **정규화 자체가 도달 불가**(게이트가 미선언을 영영 못 봄).

**후속 분리 — TASK-034 등록(정책 판정)**: 게이트가 "의도 선언 누락"을 **blocked(1)** 로 내는 건 선행 결함(이 브랜치 탓 아님). 하네스 불변식 **"1층 frozen 만 차단"** + 러너 fail-closed 관례(필수입력 부재/분석불가 → **approval_required(2)**)에 비추어 **차단은 과함** → 정책 판정 = **approval_required(2) + 카드 정직 표기**(`intent_not_declared`·coverage 미검사 노출). dev 게이트 + 킷 sync = Codex 저자. AC = `TASKS.md` TASK-034.

**D-007 처리**: 코드 브랜치 **머지 보류**. 리뷰 기록(decisions·review-notes·A-0023·TASKS TASK-033 AC#2 정정+TASK-034·summaries·handoff)은 `claude/2026-07-16-review` → main 머지. 재제출 시 **보정 커밋만** 재리뷰(멱등 — `8e6b54b`·`c8d8e7b` 재처리 금지).

---

## D-066 — TASK-033 보정(`9769ece`) 재리뷰: **통과** · 합성 intent 주입 제거로 카드 정직성·의도층 복구 확인 → main 머지 (2026-07-16, Claude)

**대상**: 브랜치 `codex/2026-07-16-task033-kit-run-robustness` 의 **보정 커밋만** 재리뷰 — `9769ece`(fix)·`fe9f1c6`(docs). 멱등: `8e6b54b`·`c8d8e7b` 는 D-065 에서 처리 완료·재리뷰 대상 아님.

**보정 델타(`8e6b54b`→`fe9f1c6`)**: `kit/run.sh` **+2/-10**(합성 주입 전량 제거) · `kit/tests/run-entrypoint-tests.sh`(케이스 재작성) · handoff · summaries. **A-0023 보정안 ①②③④ 정확 구현**.

**A-0023 R-1 해소 실증 (격리 worktree · 전부 fresh · `/bin/bash` 3.2)**:
- **합성 잔재 0**: `run.sh` 에 `TEMP_INTENT`·`mktemp`(정리 trap 포함)·가짜 `allowed_paths` 생성 코드 **전무**(grep 전수). 최종 `run.sh` 델타 = **안전관용구 1줄 + 콘솔 grep 1줄 + 문구 정정 1줄** = A-0023 "내가 짠다면"(RIG2) 형태 그대로.
- **① 카드 위조 해소(정직성 회복)**: fresh no-intent repo 카드 실측 — `intent_check.status: fail` · `verdict: blocked` · **`coverage_statement.checked: []`**(선언 대조 수행을 주장하지 않음) · `reasons: ['의도 선언 누락: change-intent.yaml 파일을 찾을 수 없습니다.']` · `in_allowed_paths: true` **부재**. D-065 대조군의 정직한 거동과 **완전 일치** = 위조 소멸.
- **② 의도층 우회 해소(결정타 · fresh 픽스처 밖 적대 repo)**: `forbidden_paths:["app/keys.py"]`·`expected_paths:["app/must_patch.py"]` 선언 + forbidden 수정·expected 미터치 → **intent 존재 = exit 1 BLOCKED**. **`change-intent.yaml` 삭제 후 = 여전히 exit 1 BLOCKED**(카드 생성·정직·크래시 없음). ⇒ D-065 에서 실증했던 **"삭제만으로 BLOCKED→PASS"(exit 0) 우회가 재현되지 않음** = TASK-027/028 패치생존성 층 소멸·bash≥4.4 판정 완화 회귀 **모두 해소**.
- **③ AC#1 가드 dead code 해소(가드-테스트 일치 회복)**: **RIG-A**(안전관용구 `${INTENT_ARGS[@]+"${INTENT_ARGS[@]}"}` → `"${INTENT_ARGS[@]}"` 원복 · 치환 `count==1` assert) → `no-intent-bash32-blocked` **단독 FAIL(12/13)**. **D-065 의 RIG1 은 13/13 유지였다** = 가드가 죽어도 무음이던 결함이 **load-bearing 으로 회복**.
- **음성검증(항상-PASS 아님)**: **RIG-B**(케이스 기대 rc 1→0 변조 · `count==1` assert) → 동일 케이스 **단독 FAIL(12/13)**. 원복 후 working tree clean.

**정정 AC#2(D-065) 대비 전항 충족 — fresh 실측**: 크래시 없음(`unbound variable` 부재·`/bin/bash` 3.2) · **게이트 자신의 판정이 그대로 흐름**(rc=1 현행 계약·판정 무변경) · 카드 생성·비어있지 않음 · **2층/3층/메타층 전부 실행**(`게이트 판정 : 카드3축=1 · 능력=0 · 간접영향=0 · 정책=0`) · 카드 정직성 3단언 모두 케이스에 내장(`의도 선언 누락` 존재 · `verdict: pass` 아님 · `in_allowed_paths: true` 부재 = **합성 재유입 자동검출 가드**).

**나머지 AC**: **AC#1** 빈 배열 전수점검 — `run.sh` 배열은 `INTENT_ARGS`·`ANALYSIS_FAILURES` 둘뿐. **bash 3.2 직접 probe 로 위험 경계 확정**: `${#A[@]}` 는 빈 배열에서 **안전(0)**, `${A[*]}`/`${A[@]}` 는 **`unbound variable` 크래시**. ⇒ 160행(`INTENT_ARGS` 확장·가드 없음)이 **유일한 실제 위험 지점**이고 보정이 정확히 거기를 막음. 225행 `${ANALYSIS_FAILURES[*]+...}` 는 `[ "${#A[@]}" -gt 0 ]` 가드 뒤라 빈 확장 도달 불가 = **무해한 방어**(dead 지만 거동 무변경 — 비어있지 않은 경로 직접 실행 비교로 출력 **바이트 동일** 확인). **AC#3** 콘솔 `missing_expected` grep(판정 무변경·표시만) — 케이스 단언 존재. **AC#4** 무회귀 — `kit/selftest.sh` **96/96**(adversarial 7/7·default 83/83·metamorphic 3/3·negative-corpus 3/3) **+ 진입점 13/13 + mutation 161 PASS** · `bash -n` 2파일 PASS · **`sync-from-dev.sh` 재실행 멱등**(working tree clean · 보정된 `run.sh` 관용구 생존). **AC#5**(D-064 O-D 병합) `expected-path-missing-approval` 에 `out_of_scope:` **부재 단언** + 콘솔 표시 단언 추가 — 이중원인 드리프트 자동검출 확보. **부수**: 151행 문구 `(의도 선언 누락 — 카드 게이트가 미선언으로 판정)` 로 정정 = 실동작 정합(D-065 지적한 "층 생략" 허위 문구 소멸·표시만·판정 무변경).

**보수적 개발 평가(COMMON-RULES §1)**: 파일 = `kit/run.sh`·`kit/tests/run-entrypoint-tests.sh`(둘 다 TASK-033 산출·Codex 소유) + handoff/summaries. **dev 무접촉 실증**(`kit`/`collab`/`summaries` 제외 시 main 대비 diff **0**) · 게이트·정책 무접촉 · 무관 리팩터·이름변경 없음 → **scope-creep 없음**. D-065 에서 지적한 **over-reach(크래시 수정 요청 → 판정 완화 동반)가 제거되어 blast radius 가 의도와 일치**(순수 견고성 수정으로 축소).

**대안 검토 — "내가 짠다면"**: 동일(A-0023 에서 RIG2 로 사전 실증한 형태). 더 단순·더 정직한 대안 없음.

**하류 영향**: 합성 주입이 사라져 게이트가 "미선언"을 실제로 보게 됨 → **TASK-034**(미선언 → `approval_required` 정규화 + 위조방지 불변식)의 **도달 가능성 회복**(D-065 에서 경고한 차단요인 해소). 진입점 케이스가 rc=1 현행 계약을 고정하므로 TASK-034 는 AC#5 대로 **rc 1→2 갱신 동반** 필요(이미 AC 에 명시).

**비차단 관찰 O-E**: 225행 `+` 관용구는 도달 불가한 방어(가드가 이미 차단) — 제거해도 무해하나 방어심층으로 유지 가치 있음. §2B 필수질문 = **아니오**(under-detection 아님·거동 무변경). 조치 불요.

**D-007 처리**: **통과 + 비민감**(킷 러너 견고성 수정 + 테스트 — 정산/인증·인가/암호화/DB migration/infra 무해당 · **판정 로직 무변경 실증**: 96/96+13/13 무회귀 + fresh 대조군 BLOCKED 동일) → Claude 가 `claude/2026-07-16-review` 에서 `main` 머지(구현자 Codex ≠ 머지자 Claude). **TASK-033 완결** — 다음 = **TASK-034**(미선언 판정 정규화) 착수 가능, 이후 MVP-3(TASK-029~032). **멱등성**: `9769ece`·`fe9f1c6` 재처리 금지.

---

## D-067 — TASK-034 "의도 선언 누락" 판정 정규화 리뷰: **보정요청**(미선언이 1층 frozen 차단을 무력화 + 카드 허위) (2026-07-16, Claude)

**대상**: 브랜치 `codex/2026-07-16-task034-intent-not-declared` — `22fe433`(fix)·`a4037ce`(docs). **판정 = 보정요청 · 코드 머지 보류**(리뷰 기록만 main).

**재현된 제출 주장(수용·재작업 금지)**: 무해+미선언 → exit 2(AC#1 절반) · 하위호환 96/96(AC#4) · 킷 selftest·진입점 13/13·mutation 161 · dev↔kit 게이트 **md5 동일**(`263f1ee4…`)·템플릿 동일(AC#5 sync 절반) · `in_allowed_paths: true` 위조 없음·합성 선언 생성 없음(AC#3 형식 충족·D-065 R-1 재유입 없음) · 음성검증 4종(`validate_no_intent_card`) 구조 양호.

**R-1(차단·under-detection)**: `build_evidence()` **첫 줄**이 `load_intent()` → 미선언 시 예외로 **카드 전체를 `intent_not_declared_evidence()` 로 대체** = 의도층만이 아니라 **민감경로층(`sensitive_result`)·@gov 함수층(`build_function_gov_result`)까지 통째로 미실행**. `run.sh` 에서 **1층 판정은 오직 `generate-change-evidence` 하나가 낸다**(`ge_exit` — 별도 `check-sensitive-zones` 실행 없음) → 카드 게이트가 abort 하면 **frozen 차단 주체가 소멸**.
**fresh 픽스처 밖 실증 2벡터**: ① `app/settlement/core.py`(🔴 frozen 정산·금전 직접영향) 수정 + intent 미선언 → **main `kit/run.sh` 🔴BLOCKED(1) → 브랜치 🟠APPROVAL(2)** · 카드 `frozen_touched: []`·`changed_files: []` ② `@gov(level="frozen")` 함수 본문 변경 + 미선언 → **main 1 → 브랜치 2**·`changed_functions: []`. 킷 게이트도 md5 동일이라 **배포 최전선에 그대로 실림**(kit gate 실측 exit 2). ⇒ **`change-intent.yaml` 삭제만으로 1층 frozen 차단 우회.** 게다가 카드가 `frozen_touched: []`·`files_changed: 0` 뿐이라 **승인자는 정산 코드 변경 사실 자체를 볼 수 없다**(카드=CI 감사 산출물·킷=배포 최전선).
**§2B 필수질문 = 예**(하네스 최상위 불변식 "1층 frozen 만 차단"의 유일한 차단을 무력화·방향이 과소탐) → **비차단 불가**.
**AC 해석 정정**: AC#1 의 "`blocked` 금지(1층 frozen 아님)" = **미선언 *자체* 를 frozen 취급 말라**(무해+미선언→2). **"frozen 을 건드렸는데 미선언이면 frozen 검사를 생략하라"가 아니다.** AC#2 도 **의도층** 미검사만 요구 — `sensitive_zone_check: not_checked` 는 요구한 적 없다. 민감경로·@gov 층은 **intent 를 입력으로 쓰지 않아** 건너뛸 이유가 없다.

**R-2(차단·R-1 과 동일 뿌리·AC#2 정직성 위반)**: 미선언 카드가 `summary.files_changed: 0`·`changed_files: []` 라고 **주장**하나 실제 변경 존재(fresh `git diff --name-only`=1). D-065 의 "합성 pass 위조"는 사라졌지만 **"변경 없음"이라는 다른 허위**가 유입(`base_commit: unknown`·`policy_sha: {}`·`generated_on: 1970-01-01` 도 계산 가능한데 폐기). **픽스처가 허위를 계약으로 고정**: `missing-change-intent` 입력이 `tests/fixtures/good/name-status.txt`(=`M app/features/search.py`, 1건)인데 기대값 `files_changed: 0`·`changed_files: []` ⇒ **96/96 초록인데 구멍 = 무발견이 아니라 미측정**. 정직성 = "검사 안 한 걸 했다고 안 함" **+ "본 사실을 안 봤다고 안 함"** — 후자 파손.

**보정안(프로토타입 실증 완료·델타 ≈10줄)**: abort 대신 **의도층만 `not_declared` 표시 후 파이프라인 계속** — ① `load_intent` 를 `try` 로 흡수(빈 선언 + `requirement_id`/`author: None`) ② `intent_check` 의 `status` 를 `not_declared` 로 덮어쓰고 `out_of_scope`/`missing_expected` 비움(**합성 선언 주입 금지 — D-065 재발 방지**·빈 선언 과탐 차단) ③ verdict 우선순위 = **frozen/forbidden(blocked) > not_declared(approval)** ④ `intent_not_declared_evidence()` 삭제(카드 대체 경로 제거) ⑤ `in_allowed_paths` 는 **`null` 권장**(AC#3 은 false 도 허용이나 "대조할 선언 없음"이 사실) ⑥ coverage — `checked` 에 `check-change-intent` 불포함 유지 + `intent_not_declared` 토큰 유지, 단 **실제 검사한 민감경로·@gov 는 `checked` 에 정상 등재**(현행 `checked: []` 는 보정 후 거짓이 됨).
**프로토타입 실측**: 무해+미선언 → **2**(AC#1 ✅) · **frozen+미선언 → 1**(`zone_level: frozen`·`frozen_touched` 채워짐·`files_changed: 1`) · **@gov frozen+미선언 → 1**(`function_frozen:app/biz.py::compute_interest`). ⇒ **AC#1 과 1층 불변식은 상충하지 않는다.**
**픽스처 보강(필수)**: `missing-change-intent` 기대값을 실제값으로 정정 + **신규 고정 적대 2종 상설 회귀**(frozen+미선언→1 · @gov frozen+미선언→1) + **음성검증**(1→2 변조 시 각각 단독 FAIL) + 킷 sync. 진입점 `no-intent-bash32-approval` 은 **무해 변경이라 rc 2 계약이 정당 — 유지**.

**보수적 개발 평가(COMMON-RULES §1)**: 파일 범위 적정(dev+kit 게이트·템플릿(AC 위임)·픽스처·진입점·docs)·무관 리팩터/이름변경 없음 → **scope-creep 없음**. **단 blast radius 가 의도 초과 = over-reach**: 요청은 "미선언 판정 정규화(1→2)" 인데 구현은 **"1층 민감경로·@gov 차단 완화"** 동반 — **D-065 와 정확히 동일 패턴**(그때는 "크래시 수정" 요청 → 판정 완화 동반). 판정 완화가 요청 범위를 넘으면 항상 결함.

**하류 영향**: `checked: []`+`changed_files: []` 는 후속 소비자(사람 승인자·CI·MVP-3 라우터 coverage)가 **"분석했고 깨끗함" vs "아예 안 봤음"** 을 구분 못 하게 함 → TASK-019 coverage 정직성 계보와 정면 충돌. 보정 시 미선언 카드도 민감경로·@gov 근거를 실은 채 승인 큐에 오름 = 태스크 원목적("검증 불가 → 사람이 본다")에 정합.

**차기 AC 가드**: TASK-034 에 **AC#6 신설**(미선언이 1층을 먹지 않음 — frozen/@gov frozen 고정 적대 픽스처 + 음성검증)·**AC#2 명시 보강**(민감경로·@gov 는 계속 검사·카드 사실 보존).

**D-007 처리**: 코드 브랜치 **머지 보류**. 리뷰 기록(decisions·review-notes·A-0024·TASKS AC 보강·summaries·handoff)은 `claude/2026-07-16-review` → main 머지. 재제출 시 **보정 커밋만** 재리뷰(멱등 — `22fe433`·`a4037ce` 재처리 금지).

---

## D-068 — TASK-034 보정(`9ecad20`) 재리뷰 **통과** · Claude `main` 머지 (2026-07-19)

**대상**: `codex/2026-07-16-task034-intent-not-declared` 보정 커밋 `9ecad20`(+`c5a04e3` docs). **멱등**: `22fe433`·`a4037ce` 는 D-067 처리완료 — 재처리 금지.
**판정**: **통과 · 비민감 → Claude `main` 머지**(D-007, 구현자 Codex ≠ 머지자). **D-067 R-1·R-2 둘 다 실증 해소.**

**보정 델타 = D-067 보정안 ①~⑥ 과 일치**: `intent_not_declared_evidence()`(카드 전체 대체) **삭제** · `build_evidence()` 가 `IntentNotDeclaredError` 를 `try` 로 흡수해 **빈 선언으로 파이프라인 계속**(합성 `["**"]` 주입 아님) · `not_declared_intent_result()` 가 `status: not_declared` + `out_of_scope`/`missing_expected`/`forbidden_touched` 비움(빈 선언 과탐 차단) · `verdict_and_exit` 는 **frozen/forbidden 을 여전히 먼저** 판정하고 `not_declared` 는 approval 분기에 추가(**`blocked > not_declared`**) · `combine_verdicts` 가 `function_gov: blocked` 독립 반영 · `in_allowed_paths: None` · `evidence_checked_records()` 가 **`check-change-intent` 만** `checked` 에서 제외. `IntentNotDeclaredError(FileNotFoundError)` 는 **파일 부재에서만** raise — 잘못된 YAML·디렉토리는 기존 `except Exception` → fail-closed 유지(우회 표면 확대 없음).

**적대적 실증(픽스처 밖 fresh·격리 worktree·pre-fix 대비 delta)**: ① `services/settlement/**`(🔴 frozen) + 미선언 → `22fe433` **exit 2·`frozen_touched: []`·`files_changed: 0`** → 보정본 **exit 1 BLOCKED·`frozen_touched` 채워짐·`files_changed: 1`** ② **`@gov(level="frozen")` 함수**(경로는 민감존 아님 = @gov 만이 판정 동인) + 미선언 → **2 → 1**(`function_frozen:lib/ledger.py::write_entry`) ③ 무해 + 미선언 → **exit 2**(AC#1) ④ **빈 선언**(존재·`allowed_paths: []`) → **exit 2·`status: fail`·`out_of_scope` 채워짐·`in_allowed_paths: false`·`requirement_id` 보존 = 미선언과 구분 유지**(AC#4). **킷 레이아웃 게이트 직접 실행으로 ①② 재현(둘 다 exit 1)** + **E2E `kit/run.sh` fresh repo 실측 = `카드3축=1` → 🔴 BLOCKED(exit 1)·2/3/메타층 전부 실행** ⇒ **1층 차단 주체 복원·배포 최전선 전파 확인**.

**R-2 정직성 실측(미선언 카드)**: `base_commit` 실제 SHA(‘unknown’ 아님)·`policy_sha` 실제 해시 2종·`summary.files_changed: 1`·`changed_files:[{settlement/calculate.py, zone_level: frozen, in_allowed_paths: None}]`·`sensitive_zone_check.status: blocked` + `frozen_touched` 에 **사유("정산 핵심 로직 — 금전 직접영향")** 포함·`coverage.checked: [check-sensitive-zones, check-function-gov-level]`(의도층만 제외)·`reasons: [intent_not_declared:…, frozen:…]`. ⇒ **"검사 안 한 걸 했다고 안 함" + "본 사실을 안 봤다고 안 함"** 양쪽 충족 — **승인자가 정산 변경 사실과 사유를 카드에서 직접 본다**.

**음성검증 rig-and-revert(치환 `count==1` assert·원복 후 `git diff` clean)**: **RIG-1**(`verdict_and_exit` 최상단에 `not_declared → approval` 조기반환 = R-1 판정층 재유입) → **`evidence-error-missing-intent-frozen-zone` 단독 FAIL(97/98)** · **RIG-2**(`in_allowed_paths` 항상 계산 = 위조 재유입) → **미선언 3케이스 전부 FAIL(95/98)**. ⇒ 신규 가드 **load-bearing**(항상-PASS 아님).

**픽스처 허위계약 정정(D-067 R-2 핵심)**: `missing-change-intent` 기대값 `files_changed: 0`·`changed_files: []`·`coverage_checked_gates: []` → **실제값 1건·`in_allowed_paths: null`·`[check-sensitive-zones]`** 로 정정 + **상설 회귀 2종 신설**(`-frozen-zone`·`-function-frozen`) + `frozen_touched`/`protected_touched`/`watched_touched` 단언 헬퍼를 dev·kit 러너에 배선 ⇒ **"96/96 초록인데 미측정"이 실제 측정으로 전환**.

**검증 주장 전량 독립 재현**: dev **98/98**(adversarial 7·default 85·metamorphic 3·negative-corpus 3) · mutation **165** · 킷 진입점 **13/13**(`no-intent-bash32-approval` = rc 1→2, AC#5) · `kit/selftest.sh` **PASS** · dev↔kit **게이트 16종 md5 전부 동일** + 킷 레이아웃 실작동 확인. *(두 스위트 동시 실행 시 진입점이 9/13 로 보이나 동일 worktree 임시파일 경합 — 단독 실행 13/13. 내 실행 아티팩트·결함 아님.)*

**AC 6/6 충족**(#1 토큰·#2 정직성 및 층 분리·#3 위조방지·#4 하위호환+빈선언 구분·#5 픽스처/음성/킷 sync·#6 신설 1층 독립성).

**보수적 개발(COMMON-RULES §1)**: 접촉 = 게이트 2(dev/kit 미러)·`cases.yaml` 2·픽스처 2·러너 2·진입점 1. 정책·템플릿·무관 코드 무접촉, 리팩터/포맷 혼입 없음. **D-067 의 over-reach(판정 완화 동반) 제거 — 이번 델타는 정반대로 차단 복원(안전 방향)** ⇒ scope-creep·over-reach 없음, blast radius 가 의도와 일치.

**하류**: 미선언 카드가 민감경로·@gov 근거를 실은 채 승인 큐에 오름 → TASK-019 coverage 정직성 계보와 정합. 후속 소비자가 **"분석했고 깨끗함" vs "아예 안 봤음"** 구분 가능 · `checked` 가 실제 실행 게이트를 반영해 MVP-3 언어별 coverage 확장 기반으로도 정합.

**비차단 관찰**: **O-F(선재·본 커밋 무관)** `kit/tests/run-tests.sh` 가 게이트를 `.harness/gates/*` 로 잡아 **킷 단독 실행 시 0/98** — `main` 에서도 동일이라 회귀 아님. 킷 실질 검증은 `selftest.sh`·진입점이 담당해 공백 없으나 킷 사용자 오해 소지 → **차기 킷 태스크에서 `kit/gates` 로 해소 또는 "dev 전용" 명시** 권고. **O-G(선재)** 분석 실패 일반 경로가 `blocked(1)` — 러너 관례(approval)와 다르나 **과탐 방향(안전)** 이라 무해.

**D-007 처리**: 통과 + **비민감**(정산·인증/인가·암호화·DB migration·infra 코드 아님 — 하네스 자체 게이트) → **Claude `main` 머지**. 상세 `collab/answers/A-0025.md`·`review-notes.md`. **다음 = MVP-3(TASK-029~032)**.

---

## D-069 — TASK-029 다국어 어댑터 seam(J0) 리뷰: **보정요청**(가드 약화 회귀 + 정책 부재 무음 + 킷 공백) (2026-07-19, Claude)

**대상**: `codex/2026-07-19-task029-language-router` · `d1dbdca`(feat)·`65e1164`(docs). **멱등**: 이 두 커밋이 본 리뷰 대상 — 재제출 시 **보정 커밋만** 재리뷰.
**판정**: **보정요청 · 구현 코드 `main` 머지 보류.** 리뷰 기록만 `main` 반영(collab-protocol §5.1).

**제출 주장 전부 재현 — 재작업 금지**: `tests/run-tests.sh` **101/101 PASS** · tree-sitter 4문법(java/javascript/typescript/tsx) **실제 로드·파싱** · pin 버전이 **실설치본과 일치**함을 케이스가 단언(vacuous PASS 아님 — 의존 부재 시 exit 2 로 FAIL) · Python `ast` **로직 무개조**(필드 추가만) · 확장자 라우팅 결정적 · `.java`(stub)/`.go`(unsupported) 카드 `not_checked` 노출. **fresh 픽스처 밖 실증**: `services/settlement/Calculator.java`(🔴 frozen) → **exit 1 BLOCKED·`zone_level: frozen`·frozen 사유** 와 **동시에** 언어 coverage 문구 병기 = **AC#3 "경로층 판정 유지 + coverage 노출" 충족**. **음성검증 RIG-1**(카드 `+ lang_coverage["not_checked"]` 제거) → `evidence-language-coverage` **단독 FAIL(100/101)**·원복 clean = 신규 coverage 가드 **load-bearing**.

**R-1(차단 · 가드 약화 *회귀*)**: `validate_inventory` 가 **전체 리스트 동등비교 → 기대 키만 부분비교**로 바뀌어, ① 실제 items 초과분이 비교에서 탈락 ② 기대에 없는 필드 미검사. **rig-and-revert 실증**(유령 함수 `PHANTOM_GHOST` 주입): **`main` = FAIL 97/98(잡음) vs 본 브랜치 = 101/101 무음 통과**. 즉 **이번 델타가 살아있던 가드를 죽였다**(D-063 R-1·D-065 ③ 와 동일 클래스). 인벤토리는 `check-function-gov-level` 입력 = 함수레벨 민감도의 뿌리 → §2B 필수질문 **예** → 비차단 불가. 원인은 공통 IR 3필드 추가로 기대값이 깨진 것이나 **정답은 기대값 갱신**. blast radius 작음(`items` 기대 케이스 2건뿐). 보정: 전체비교 원복 + 픽스처 3필드 기입(+최소 길이 동등 단언) + 유령-아이템 rig 음성검증.

**R-2(차단 · 조용한 통과)**: `language_coverage()` 가 정책 경로 **부재 시 무음 정상반환** → 동일 입력에서 언어 `not_checked` **전부 소멸·exit 0·경고 0**(실측). **형제 정책은 정반대**: `--sensitive-zones` 부재 → **exit 1 fail-closed**(실측). 잘못된 YAML 은 exit 1, `adapters: {}` 는 전부 unsupported 과탐 — **부재 경로만 유일하게 관대**. AC#3 🔴 "조용한 통과 금지" 와 정면 충돌. **정상참작**: 부재 시에도 일반 문구 `non-Python semantic analysis` 가 남아 **카드 위조는 아님**(D-067 R-2 급 허위 아님) → R-1 보다 낮은 등급이나, ① 일관성 붕괴 ② **현실 발생경로 존재**(킷에 해당 정책 없음 = R-3 → 차기 sync 가 정책을 빠뜨리면 배포 최전선에서 무음 전멸) ③ **이 경로 픽스처 0건 = 미측정** 이라 차단 유지. 보정: 명시-부재 시 fail-closed 또는 `not_checked` 흔적 + 회귀 픽스처 + 음성검증.

**R-3(차단 · AC#4 미충족)**: 킷 무접촉 — `kit/policies/language-routing.yaml`·`kit/gates/language-router.py`·`check-tree-sitter-languages.py`·`kit/requirements.txt` **전부 없음**. **dev↔kit md5 동일성 불변식 최초 균열**(실측: `generate-change-evidence.py` dev `79836db6…`/kit `6cf0f17d…`, `extract-python-inventory.py` dev `bc1a36de…`/kit `944887f0…` — D-068 에서 16종 전부 동일이었음). **킷 정직성 후퇴·판정 회귀는 없음**(킷은 구버전이라 언어층 부재 + 일반 문구 유지). 보정은 **택1**: (a) 킷 sync + md5·selftest·진입점 재확인, **또는 (b) "J0 는 dev 전용" 을 킷 README/manifest·TASKS 에 명시**하고 반영 시점을 문서화. **(b) 로 충분 — 대규모 sync 강요 아님.**

**비차단 관찰(차기 AC 로 이월)**: **O-A** AC#6(b) 부분미충족 — 라우터는 `parser_versions` 를 산출하나 `language_coverage()` 가 전부 버려 **카드에 파서/문법 버전 0건**(`+ lang_coverage["checked"]` 는 항상 빈 리스트 = dead code). `policy_sha` 에 `language-routing.yaml` 포함으로 **선언된 pin 은 간접 고정**·Java 파싱 부재로 실해 없음 → **TASK-030 AC 에 "카드에 실제 사용 파서/문법 버전 기록" 명시**. **O-B** AC#6(a) 부분미충족 — `tests/parity/` 는 README 뿐, `run-tests.sh` 에 `parity` 0건·`Group parity` 미출력 = **러너 훅 부재** → **TASK-031 AC#7 전제로 "빈 그룹이라도 러너가 수집·집계" 요구**. **O-C** `not_checked` 가 확장자 단위 dedup 이라 미분석 **파일 수** 비가시 — 차기 건수 병기 검토. **O-D** tree-sitter 스모크는 의존 부재 시 환경 의존 FAIL(설계대로) → CI/킷 문서에 설치 선행 명기 권고(R-3 와 동시 해소 가능).

**보수적 개발**: scope-creep 없음(신규 게이트 2·정책 1·IR 스키마 1·기존 게이트 2 필드추가·테스트·docs — 무관 리팩터/포맷 혼입 없음). **Python `ast` 무개조 원칙 준수 ✅**(파싱·판정 로직 무변경). 다만 **R-1 의 단언 약화 = "요청 범위를 넘어 기존 검증자산 강도를 낮춤"** 이라 over-reach 방향 — MVP-3 전체가 "검증자산 보존" 전제 위에 서 있다.

**하류**: TASK-030(J1) 이 `supported/stubbed` 분기를 Java 추출기 배선점으로 씀 → **R-2 무음이 남으면 "라우팅 안 됨"과 "정책 없음" 구분 불가**. 공통 IR `signature_start_line`(데코레이터 최소 라인)은 **D-057 계보 데코레이터-라인범위 갭을 선제 해소**한 좋은 설계 ✅ — 그러나 그 계약의 **회귀 그물이 R-1 로 뚫려 J1/J2 계약 위반을 잡을 수단이 없다** → R-1 은 J1 착수 **전** 필수.

**D-007 처리**: **보정요청 → 코드 머지 보류**, 리뷰 기록(`A-0026`·본 D-069·`review-notes.md`)만 `main` 머지. 상세 `collab/answers/A-0026.md`.

---

## D-070 — TASK-029 보정(`f734355`) 재리뷰: R-1/R-2/R-3 해소 확인, **신규 R-4 보정요청** (2026-07-19)

**대상**: `codex/2026-07-19-task029-language-router` 보정 커밋 `f734355`(fix)·`48ed2be`(docs). **멱등성**: `d1dbdca`·`65e1164` 는 D-069 처리완료 — 재처리 금지.

**판정**: **보정요청 — 구현 코드 `main` 머지 보류.** 리뷰 기록만 `main` 반영(D-007·collab-protocol §5.1).

**제출 주장 전량 독립 재현(재작업 금지)**: `tests/run-tests.sh` **102/102 PASS** · `tests/mutation-check.sh` **PASS**(metamorphic·negative-corpus·원본무결) · `kit/selftest.sh --quick` **PASS** · 킷 진입점 **13/13 PASS** · **dev↔kit md5 게이트 18종 *전부* 동일**(Codex 주장은 "핵심 7쌍"이었으나 실측은 전량) + `language-ir.schema.yaml`·`README.md` 동봉 ⇒ D-068 동일성 불변식 **완전 복원**.

**R-1 해소 ✅**: `validate_inventory` **전체 리스트 동등비교 원복** + `cases.yaml` 기대 items 9건에 공통 IR 3필드(`signature_start_line`·`signature`·`annotations`) 명시 기입 = 보정안 ①② 그대로. **음성검증 재현**(유령 항목 `PHANTOM_GHOST` 주입·치환 count==1·원복 clean): A-0026 시점 **101/101 무음** → 보정 후 **FAIL `python-inventory` 101/102** ⇒ 죽었던 가드 **load-bearing 회복**. 하류 J1/J2 의 IR 계약 회귀 그물 복구 = TASK-030 착수 전제 충족.

**R-2 해소 ✅**: 경로 미지정(무음)과 지정-부재(오류) 분기 분리 + `errors` 시 **fail-closed `blocked`** + `reasons`·`coverage_statement.not_checked` **양쪽 흔적** = 보정안의 "fail-closed 또는 흔적" 을 **둘 다** 구현. 형제 정책(`--sensitive-zones` 부재 → exit 1)과의 비대칭 해소. `BLOCKED` 는 최고 severity 라 기존 판정을 **낮추는 경로 없음**(안전 방향) 확인. 회귀 픽스처 `evidence-language-policy-missing` 신설. **음성검증 RIG-2**(fail-closed 2줄 제거) → 해당 케이스 **단독 FAIL(101/102)**.

**R-3 해소 ✅**: 택1 중 **(a) 전체 킷 sync** 이행 — `kit/gates/language-router.py`·`check-tree-sitter-languages.py`·`language-ir.schema.yaml`·`kit/policies/language-routing.yaml`·`kit/requirements.txt`(dev 와 바이트 동일) 동봉 · manifest `0.3.0-mvp3-j0`·18종·`language_j0` 그룹 · README 18종·설치 안내 · `sync-from-dev.sh` 에 schema/requirements 복사 라인 추가로 **차기 sync 멱등 보존**. **AC#4 충족**.

**R-4(차단 · 신규 유입 · 배포 최전선 판정 회귀)**: **킷 문서화 기본 사용법에서 무해한 변경조차 100% 🔴 BLOCKED.** 원인 = `--language-routing` argparse 기본값이 **상대경로** `policies/language-routing.yaml` 인데 **`kit/run.sh` 가 이 인자를 아예 넘기지 않아**(`grep -c language kit/run.sh` = **0**) `cd "$REPO"` 후 **대상 repo cwd 기준**으로 해석됨. 형제 정책 4종은 전부 `$POL/...` 절대경로 명시 전달인데 **language-routing 만 누락**. 여기에 R-2 fail-closed 가 얹히면서 **기본값은 항상 "지정됨"** 이라 무음 분기에 안 걸리고 → 대상 repo 에 해당 파일이 없으면 **무조건 blocked**. 내 보정안의 "**명시**됐는데 부재" vs "기본값" 구분이 구현에서 붕괴한 것이 핵심. **fresh repo 실증**(무해 Python-only 변경·intent 정상 선언): `main` **exit 0** · 보정 전 `65e1164` **exit 0** · **보정 후 `48ed2be` exit 1 BLOCKED** — 카드 `verdict: blocked`·`reasons: language routing policy missing: policies/language-routing.yaml`. **`--policies` 로도 구제 불가**(language-routing 은 그 값을 전혀 참조 안 함 — `--policies <kit>/policies` 명시해도 exit 1) · run.sh **preflight 필수정책 루프에도 누락**되어 사전 진단 불가. 통과하는 유일 조건 = 대상 repo **안에** `policies/language-routing.yaml` 존재(실측 exit 0). **전 스위트 초록인데 안 잡힌 이유(미측정≠무발견)**: `run-entrypoint-tests.sh` fixture 가 `cp "$KIT/policies/"*.yaml "$repo/policies/"` 로 **킷 정책 전량을 대상 repo 안에 복사** → 이번 sync 로 들어온 `language-routing.yaml` 덕에 테스트 repo 만 우연히 상대경로 해소. dev 는 repo 루트에 `policies/language-routing.yaml` 이 있고 `.harness/run.sh` 자체가 없어(게이트 직접 호출) **영원히 재현 안 됨** = 전형적 dev/배포 divergence. **§2B 필수질문 = 예**: under-detection 은 아니나 **모든 변경이 상시 🔴 면 BLOCKED 신호의 정보량이 0** 이 되어 승인자가 카드를 무시하거나 킷을 끈다 — "판정 회귀 없음"·"배포 최전선 정직성" 불변식 정면 위반이며 **`main` 대비 명백한 판정 회귀(0→1)**. **보정안(blast radius 작음 — run.sh 2줄 + 픽스처 1건)**: ① `kit/run.sh` 에 `--language-routing "$POL/language-routing.yaml"` 명시 배선(형제 규약 일치 → `--policies` 오버라이드도 자동 존중) ② preflight 필수정책 루프에 추가(부재 → 관례대로 exit 2 진단) ③ argparse 기본값 `None` 권장(미지정/부재 구분 복원) ④ **`policies/` 없는 대상 repo + 킷 동봉 정책 → exit 0** 진입점 회귀 케이스 신설(현재 이 경로 픽스처 0건) ⑤ 배선 원복 시 단독 FAIL 음성검증.

**비차단 관찰**: **O-A**(카드에 파서/문법 버전 0건) · **O-B**(`parity` 러너 훅 부재 — 이번에도 README 만) · **O-C**(`not_checked` 확장자 dedup) · **O-D**(스모크 환경의존) — **A-0026 판단 유지**, TASK-030 AC·TASK-031 AC#7 로 이월. **O-E(신규)**: `not_checked` 는 본래 "분석 못 한 **대상**" 목록인데 오류 문구를 혼입 — 흔적 요구는 충족하고 무해하나 장기적으로 `coverage_statement.errors` 별도 키가 정확 → 차기 카드 스키마 손볼 때 검토.

**보수적 개발**: scope-creep 없음(접촉 = R-1/R-2 대상 게이트·러너·픽스처 + R-3 이 요구한 킷 sync 산출물, 무관 리팩터/포맷 혼입 없음). **A-0026 이 지적한 단언 약화가 정확히 원복** = 이번 델타는 검증자산을 **복원**하는 방향 ✅. 다만 **R-4 는 "정책 부재 정직화" 요청이 "무해 변경 오차단" 이라는 의도 밖 판정 변경으로 번진 것** — 방향은 안전하나 blast radius 가 의도보다 크다.

**하류**: IR 회귀 그물 복구(R-1) + 킷 동일성 복원(R-3) 으로 **TASK-030(J1) 착수 전제는 충족**. 단 **R-4 를 남긴 채 머지하면 킷 사용자 전원이 즉시 상시차단** — J1 보다 먼저 닫아야 한다.

**D-007 처리**: **보정요청 → 코드 머지 보류**, 리뷰 기록(`A-0027`·본 D-070·`review-notes.md`)만 `main` 머지. 상세 `collab/answers/A-0027.md`.

## D-071 — TASK-029 R-4 보정(`7cea158`) 재리뷰: **R-4 해소 확인 · 신규 R-5 보정요청** (2026-07-19, Claude)

**대상**: `codex/2026-07-19-language-router` 헤드 `31f0814` (재리뷰 범위 = `7cea158` + `31f0814`)
**판정**: **보정요청 — 코드 머지 보류.** 리뷰 기록만 `main` 머지. 상세 = `collab/answers/A-0028.md`

**R-4 해소 ✅ (독립 재현)**: `--language-routing` 기본값 `None` + `kit/run.sh` 절대경로 명시 전달로
"대상 repo cwd 기준 상대경로 해석 → 무해 변경 100% BLOCKED" 사슬이 끊겼다. fresh 적대입력
(픽스처 밖·대상 `policies/` 없음·무해 Python-only) 실증 **exit 0** — A-0027 에서 exit 1 blocked 이던 시나리오.
전량 재현: dev **102/102** · `mutation-check` **PASS** · `selftest --quick` **PASS** · 진입점 **14/14** ·
**dev↔kit 게이트 21파일 md5 전량 동일**(D-068 불변식 유지). **RIG-1**: 배선 1줄 제거 → 진입점 **13/14**
단독 FAIL ⇒ 신규 배선 **load-bearing**. dev cases 12건 중 명시 3·생략 9 로 fail-closed/무음 **양 분기 커버** ⇒
기본값 변경에 의한 하류 무음 coverage 손실 **없음**.

**R-5 (보정요청 · 죽은 가드 + 무예고 배포 파괴)**: 보정이 추가한 **필수 정책 preflight 5번째 항목
(`language-routing.yaml`)이 회귀 시험 0**. **RIG-2**(preflight 목록에서 해당 항목만 제거) → 진입점
**14/14 그대로 초록**(RIG-1 은 13/14 로 울었음). 무의미한 가드가 아니라 **제거 시 R-4 동일 계열 오판정이
부활**한다: 레거시 override 디렉터리(구 정책 4종만 보유 — 업그레이드 전 정상 배포)에 무해 변경 →
가드 없으면 **exit 1 / `verdict: blocked` / `reasons: language routing policy missing`**, 가드 있으면
`✗ 분석 실패` 로 **정직한 도구 실패 강등**. 즉 배포 최전선 R-4 재발을 막는 **유일 방벽인데 시험이 없다** —
A-0026 R-1(죽은 유령항목 가드)과 동일 패턴, CLAUDE.md §2B "거버넌스 구멍은 비차단 금지" 해당.
부수: `kit/README.md` 가 `--policies` override 필수 파일 집합을 **미기재**(`manifest.yaml:66` 에만 존재) ⇒
기존 도입처는 업그레이드 즉시 전 실행 분석 실패인데 **마이그레이션 안내 부재**.
→ ① 레거시 override 회귀 케이스 추가(분석실패 규약 + `verdict: blocked` 카드 **미생성** 동시 단언,
RIG 로 단독 FAIL 실증) ② README 에 필수 정책 5종 + 업그레이드 안내 1–2줄.

**보수적 개발(COMMON-RULES §1)**: intent 밖 파일 없음 · 무관 리팩터 없음 · 정책 값 불변(배선만) ·
blast radius 의도 이내 ⇒ **scope-creep·over-reach 없음**. 보정 품질 자체는 양호 — R-5 는
"고친 것이 틀렸다"가 아니라 **"고친 것을 지킬 시험이 없다"**.

**대안 검토**: `$POL` 부재 시 킷 동봉 정책 자동 폴백 안은 **기각** — override 명시 사용자가 조용히 다른
정책으로 검사받는 무음 손실(R-2 가 없앤 것)의 재도입 + 카드상 정책 출처 모호. 명시적 fail-closed + 문서화가 옳다.

---

## D-072 — TASK-029 R-5 보정(`117b4a3`) 재리뷰: **R-5 해소 · 리뷰 통과 · Claude main 머지** (2026-07-20, Claude)

**대상**: `codex/2026-07-19-task029-language-router` 헤드 `b23506e` (재리뷰 범위 = `117b4a3` + `b23506e`)
**판정**: **리뷰 통과 · 비민감(킷 테스트 + README 문서) ⇒ D-007 에 따라 Claude 가 `main` 머지.**
상세 = `collab/answers/A-0029.md`

**R-5 해소 ✅ (제출 주장 전량 독립 재현)**: 보정은 `kit/tests/run-entrypoint-tests.sh` 에
`language-routing-legacy-override-preflight`(정책 4종만 보유한 레거시 override → **exit 2 ·
`필수 정책 파일 없음: …language-routing.yaml` · `verdict: blocked` 카드 미생성** 3중 단언)를,
`kit/README.md` 에 **필수 정책 5종 + 업그레이드 복사 안내**를 추가했다. 전량 직접 실행:
진입점 **15/15** · dev **102/102** · `mutation-check` **PASS** · `selftest --quick` **PASS** ·
dev↔kit 게이트 **21파일 md5 전량 동일**(D-068 불변식 유지) · `sync-from-dev.sh` 재실행 **멱등
(git clean)** 이며 킷 전용 진입점 시험이 스냅샷/복원으로 **생존**.

**RIG (가드가 load-bearing 인가)**: preflight 목록에서 `"$LANGUAGE_ROUTING"` **만** 제거 →
진입점 **14/15 단독 FAIL**, 실패 출력에 R-4 계열 회귀(`verdict: blocked` ·
`reasons: language routing policy missing`)가 그대로 재현. **A-0028 의 RIG-2 가 당시엔 무음이었는데
이제 운다 = 죽은 가드 → 살아있는 가드 전환 실증.** **음성검증**: 기대 rc `2→3` 변조 시 단독 FAIL
⇒ 항상-PASS 아님.

**fresh 적대입력(픽스처 밖 · 직접 생성)**: 정책 4종만 둔 override 로 무해 변경 실행 → **exit 2 ·
카드 미생성**(정직한 도구 실패). README 안내대로 `language-routing.yaml` 복사 후 → **exit 0 ·
`verdict: pass`**. ⇒ 문서가 **실행 가능한 탈출구**임까지 실증. `run.sh:48` · `manifest.yaml:61–66` ·
README 세 곳의 필수 5종 **일치**(드리프트 없음).

**보수적 개발(COMMON-RULES §1)**: 변경 2파일 +30/-0 — A-0028 요청 ①②만. intent 밖 파일·무관
리팩터 없음, 게이트 로직/정책 값/`run.sh` 배선 불변 ⇒ **scope-creep·over-reach 없음**.

**차기 AC 가드 G-1 (비차단으로 흘리지 않고 명시)**: preflight 5항목 중 회귀 시험 보유는 2개뿐
(`sink-registry`·`language-routing`). 나머지 3항목(`sensitive-zones`·`sensitive-capabilities`·
`approval-routing`)은 **R-5 와 동일한 죽은 가드** — 실증: `"$ZONES"` 제거 + 해당 정책 삭제 시
**exit 1 / `verdict: blocked` 카드**로 동일 계열 오판정 부활. **선재 갭이라 보정요청 대신
차기 AC 로 명문화**: 필수 정책 preflight 를 **표 주도 회귀**로 전환해 5항목 **각각** 3중 단언 +
항목별 RIG 단독 FAIL 실증, 정책 추가 시 시험이 자동으로 따라붙는 구조. → TASK-030 또는 킷 후속 AC.

**TASK-029 종결**: R-1~R-5 전부 해소. J1(TASK-030 Java 추출기) 착수 전제 충족.

---

## D-073 — TASK-030 (J1 Java 인벤토리) 리뷰 → **보정요청 R-1** · 코드 머지 보류

**대상**: `origin/codex/2026-07-20-java-inventory` 계열 브랜치
`codex/2026-07-20-task030-java-inventory` (`4ccb8c9` 구현 + `039cd1a` 인계기록).

**판정**: **보정요청(R-1 차단)**. 리뷰 기록만 `main` 머지, 구현 코드는 보류(D-007).

**제출 주장 전량 독립 재현 — 재작업 금지**: dev `run-tests.sh` **107/107**(main 102 → Java 5건 추가) ·
dev↔kit 게이트 **21파일 md5 전량 동일**(D-068 유지) · `kit/manifest.yaml` **19종 = 실제 파일 19개** ·
진입점 단독 실행 **18/18**(main 15/15 → +3) · README/manifest/gates README **네 곳 문구 일치**.
AC#1~#5 전부 충족 실측.

**적대적 검증(픽스처 밖 fresh 입력)**: 신규 오버로드를 기존 것 **앞에 삽입** +
`@PreAuthorize` **인자만** 변경 + 나머지 오버로드 무변경 → 신규 `added` · 인가 변경
`modified/signature_changed:true` · 무변경 오버로드 **무보고**. 이름·순서 단독 키였다면 전부 오판했을 입력.
**음성검증(rig-and-revert · 원복 clean)**: **RIG-1** 매칭키에서 시그니처 제거 → 무변경 오버로드 허위
`modified` + 단독 FAIL **106/107**. **RIG-2** `_signature_dump` 에서 어노테이션 제거 →
`@PreAuthorize` 인자 변경 **완전 소멸**(under-detection) + 단독 FAIL **106/107**. ⇒ 두 가드 모두
load-bearing. **D-072 에서 이월한 차기 AC 가드 G-1(필수 정책 preflight 표 주도 회귀) 실제 구현 확인 ✅**
(3항목 신설 + `missing-sink-registry` 동일 헬퍼 통일 · 3중 단언).

**🔴 R-1(차단 · 판정 회귀 · 배포 최전선)**: **tree-sitter 의존이 부재·불량이면 `.java` 가 든 diff 가
전량 🔴 BLOCKED** 로 뒤집힌다. 동일 repo·동일 무해 변경(`.java` 1개 추가)에서
**main = exit 0 PASS vs 브랜치 = exit 1 BLOCKED** (판정 회귀 0→1). `tree_sitter` 는 정상이고
`tree_sitter_java` 문법만 없어도 동일(킷 `requirements.txt` 부분설치 = 현실 경로)이며,
`run.sh` 에 `check-tree-sitter-languages` 배선 **0건**이라 사전 진단 경로도 없다.
**가상 시나리오가 아니라 이미 터짐** — 내 환경에서 진입점 스위트가 **3/3 재현적으로 FAIL**
(`language-routing-kit-policy-default`), main 은 같은 조건 **3/3 PASS**, 카드 `reasons` 실측 원인은
`dlopen(... tree_sitter/_binding ...) incompatible architecture (have 'arm64', need 'x86_64')`.
(타임아웃 1→8초로 올려도 동일 FAIL ⇒ 타임아웃 무관. 스위트 밖 단독 재실행은 PASS ⇒ 게이트 로직이 아니라
의존 해소 경로 문제.) **사유 정직성 붕괴**: `frozen_touched: []`·`protected_touched: []` 인데
`verdict: blocked` + `verdict_statement: governance violation detected`, 사유는 dlopen 오류 문자열뿐 —
TASK-029 R-4 의 "상시 🔴 = 신호 정보량 0" 과 같은 구조에 **허위 사유**가 얹힌 것.
**반대방향 구멍(더 위험)**: `ImportError` 가 `map-diff` 캐치 튜플 밖이라 전역 `except Exception` 으로
빠져 **`files: []`** 반환 → **`.java` 하나가 같은 diff 의 모든 Python 파일 함수 매핑을 무력화**.
실측: 정상 `[('X.java',['X']), ('calc.py',['calc'])]` vs 깨진 환경 `files: []`
(정산 경로 Python 함수 변경이 매핑에서 소멸). **§2B 필수질문 = 예**(과차단 + 과소탐지 동시) ⇒ 비차단 불가.
AC#4 의 "파일 단위 격리 · 형제 보존 · exit 0" 규약이 **문법오류에만 적용되고 의존 부재에는 없다**.
**보정안(blast radius 작음 — 게이트 2파일 + 픽스처)**: ① `ImportError`·`OSError` 를 잡아
`{"items": [], "parse_error": "java analysis unavailable: …"}` 로 **파일 단위 격리 강등**(기존
`fallback_file`·`file_record["parse_error"]` 배선을 그대로 탐) ② `map-diff`·`classify` except 튜플에
`ImportError`·`OSError` 추가로 `files: []` 경로 봉쇄 ③ 결과가 차단이 아니라 **coverage 노출**로 흐를 것
(`.java` 는 routing 상 `status: stub` — verdict 상승 금지) ④ **회귀 픽스처 신설**(이 경로 픽스처 0건 =
무발견이 아니라 미측정): 의존 부재 강제 상태에서 `.java` diff → exit 0 + coverage 문구,
python+java 혼합 diff → Python 매핑 생존 ⑤ 격리 원복 시 **단독 FAIL** 음성검증 ⑥ (권장) preflight/카드에
Java 심층분석 가용 여부 1회 진단.

**비차단 관찰(차기 AC 이월)**: **O-1** 익명 내부클래스 메서드가 `Outer.run`, 메서드 내 로컬 클래스가
`Outer.Local` 로 명명돼 **실존하지 않는 이름** 생성·동명 실메서드와 충돌 가능 — J2 가 이름으로 인가 등급을
귀속시키면 **잘못된 함수에 붙는다** ⇒ **TASK-031 AC 에 고정 적대 픽스처(익명 내부클래스·로컬 클래스) 명시**.
**O-2** record compact constructor 미추출. **O-3** Java `start_line` 은 이름 토큰 라인(Python 은 `def` 라인) —
`map-diff` 는 `signature_start_line` 을 써서 구멍 없음. **O-4** Java 시그니처 변경은 `modified` 가 아니라
deleted+added(안전 방향이나 Python 과 비대칭) ⇒ TASK-031 parity 기대값 고정. **O-5**
`java_match_signature` 가 문자열 리터럴 안 괄호도 세어 불균형 시 키가 `(name,"")` 로 퇴화(안전 방향).
**O-6** routing 의 java 가 여전히 `status: stub` 이라 카드는 "deep semantic analysis not yet implemented"
라고 말하나 실제로는 인벤토리·매핑·분류가 동작 = **과소 주장**(안전 방향·부정확), **O-A**(카드에 파서/문법
버전 0건)도 미해소 ⇒ 둘 다 TASK-031 AC 로. **O-7** 없는 파일 인자 → traceback.

**보수적 개발**: intent 밖 파일·무관 리팩터 없음 ⇒ scope-creep 없음. 다만 **R-1 은 "Java 인벤토리 추가"가
의존 부재 환경에서 판정을 뒤집는 의도 밖 blast radius 로 번진 것 = TASK-029 R-4 와 동일 패턴 재발**
(그때는 정책 경로, 이번엔 파서 의존).

**하류**: Java IR 계약·오버로드 키·어노테이션 매핑은 **TASK-031(J2) 착수 전제로 충분**. 단 R-1 을 남기면
tree-sitter 미비 환경의 킷 도입처가 `.java` 든 모든 변경에서 상시차단 + 허위 사유를 보고, 같은 diff 의
Python 함수 추적까지 잃는다 ⇒ **J2 보다 먼저 닫을 것**.

상세: `collab/answers/A-0030.md` · `review-notes.md` TASK-030 절 · `summaries/2026-07-20.md`.

---

## D-074 — TASK-030 R-1 보정(`1b11550`) 재리뷰: **R-1 해소 · 리뷰 통과 · Claude main 머지** (2026-07-20, Claude)

**결정**: TASK-030(J1 Java 인벤토리) 리뷰 **통과**. 비민감 변경이므로 D-007 에 따라 Claude 가 `main` 머지.
재리뷰 범위는 보정 커밋 `1b11550` 만(멱등성).

**근거 — R-1 필수항목 1~5 전량 해소, 독립 재현**
- 의존부재를 게이트 내부에서 `parse_error` 로 통일 강등(#3) + map-diff·classify 캐치 튜플 확장(#1·#2).
- **증상 A/B**: 킷 진입점 **브랜치 18/18 PASS**(R-1 당시 3/3 FAIL) vs main 15/15.
- **증상 C**: fresh 민감입력에서 브랜치 카드 ↔ main 카드 **diff 0**. 사유는 `protected:...:인증/인가`
  = **경로 기반**이라 파싱 가용성과 무관. dlopen 문자열 누출 경로 소멸.
- **증상 D**: fresh 혼합 diff 에서 `.java` 는 `parse_error` 로 격리되고 `svc/calc.py` 매핑 **생존**.
- 검증환경이 `tree_sitter` **미설치**라 shim 없이 네이티브로 실패경로 재현(최적 적대조건).

**음성검증(rig-and-revert, 전부 원복)**
- 세 가드가 **상호 중복**이라 개별 rig 로는 안 죽음 → 경로 분리 실증.
- RIG-C(#3 제거) → `java-inventory-analysis-unavailable` **단독 FAIL**(107→105).
- **co-located 게이트 파일 결손**(킷 부분배포) 경로: `#1/#2 제거` → 전역 `ERROR:` = 증상 D 부활 /
  `#1/#2 존재` → 우아한 강등 + Python 생존 ⇒ **#1·#2 도 load-bearing**.
- 기대값 변조(`pass→blocked`, `calc→NOPE`) → 해당 2케이스 단독 FAIL ⇒ 항상-PASS 아님.

**킷 정합성**: dev↔kit 게이트 **19/19 md5 전량 동일**(D-068 유지). `run.sh` 판정 조립 무변경.

**환경 의존 FAIL 4건은 결함 아님**: tree-sitter 미설치로 양성 Java 경로가 못 도는 것.
`selftest --quick` FAIL 도 **main 이 동일 환경에서 FAIL(101/102)** 이라 선재 동작.

**보수적 개발**: 게이트 3쌍 + 픽스처 + `run-tests.sh` per-case `env`(픽스처에 필요한 최소 확장).
scope-creep·over-reach 없음.

**차기 AC 이월(명시)**
- **O-4 (TASK-031)**: #1·#2 의 유일한 load-bearing 경로인 *co-located 게이트 파일 결손* 에 픽스처 **0건**
  → "게이트 파일 결손 시 파일단위 격리 + 형제 보존" 을 AC 픽스처로 고정.
- **O-5 (TASK-031/J2 · R-1 item 6 승격)**: `language_coverage()` 가 정책 유래로만 `not_checked` 를 만들어
  **열화/정상 분석을 구분 못함**. J1 은 java=`stub` 이라 무해하나 **J2 에서 `supported` 가 되는 순간 허위 카드**.
  J2 AC 에 ①`parse_error` 파일의 카드 coverage 노출 ②Java 심층분석 가용여부 진단 명시.

상세 = `collab/answers/A-0031.md`

---

## D-075 (2026-07-20) TASK-031 J2 프레임워크 어노테이션 정책 — **Q-0005 답변 · 정책 작성**(리뷰 아님)

**대상**: `codex/2026-07-20-task031-java-gov-annotations` (`4dc0b7c`). **미머지 codex 브랜치는 이 1건뿐**이었고,
내용은 **구현이 아니라 협업 질문 문서 1개**(`collab/questions/Q-0005.md`, 20줄 추가)였다.
⇒ 리뷰 통과/보정요청이 아니라 **정책 답변**이 정확한 처리다. 비민감(협업 큐 문서) ⇒ D-007 로 `main` 머지.

**분류 확인**: `git branch -r --no-merged origin/main` = 1건. handoff-log 최신 줄은 TASK-030
**리뷰 통과·머지 완료**(D-074)라 "보정 차례" 브랜치 없음. 작업트리에 TASK-031 구현 WIP(미커밋
`extract-java-gov-annotations.py`·`tests/fixtures/java-gov/`·`tests/parity/*`)가 보이나 **제출물이 아니므로
리뷰 대상 아님** — 건드리지 않았다.

**Codex 판단이 정확했다**: 정책값을 하드코딩하지 않고 멈춰서 물은 것이 옳다. AC#2 는 "카탈로그 외부화·
하드코딩 금지"이고 `policies/*` 는 Claude 소유(CLAUDE.md §1). 임의 결정했다면 `over-reach` 보정요청감이었다.

**작성물**: `policies/framework-annotations.yaml` (18항목 · `policy_version: 0.1-mvp3-j2`).
검증 — 추가 상태 `tests/run-tests.sh` **110/111**, 미추가 baseline 과 **완전 동일**(유일 FAIL
`tree-sitter-smoke` 는 이 환경 `tree_sitter` 미설치 = D-074 확정 선재 환경 FAIL) ⇒ **inert 임을 실측 확인**.

**스키마 확정 — Codex 제안(`annotations.<SimpleName> = {level, entrypoint, source, owner}`) 대비 4곳 수정**:
- **①🔴 마지막 점-세그먼트 매칭**: Java 는 `@PreAuthorize` 와 FQN 인라인
  `@org.springframework...PreAuthorize` 를 **둘 다 허용**. 원문 토큰 비교면 FQN 표기를 **놓친다 = 과소탐 =
  MVP-3 공통 "놓침 금지" 위반**. `fqns` 는 감사·문서용이며 매칭에 쓰지 않는다.
- **②🔴 인자 조건 `when` 필요**: AC#2 의 `@Query(nativeQuery=true)` 는 조건부인데 제안 계약엔 인자를 볼
  자리가 없다 → 전부 protected(신호 소멸) 또는 전부 무시(원시 SQL **놓침**) 양자택일이 된다.
  `defaults.unresolved_argument: match` — 상수참조 등 미해소 시 **추정 금지 + 매칭 취급**(과탐 반올림).
- **③ map → list**: 형제 `sensitive-capabilities.yaml` 과 동형이고 **중복 `name` 을 검증오류로 포착**
  (map 이면 중복 키가 조용히 덮여 등급이 소리 없이 바뀐다).
- **④ `reason`·`reviewer` 필수**: 없으면 카드가 사람에게 위험을 설명 못하고(§2C) 승인 라우팅 대상이 안 정해진다.

**등급 확정**: 인가 6종(`@PreAuthorize`·`@PostAuthorize`·`@Secured`·`@RolesAllowed`·`@PermitAll`·`@DenyAll`)
= protected/security-reviewer · `@Query(nativeQuery=true)`·`@Modifying` = protected/dba-reviewer ·
`@Transactional` = watched/dba-reviewer · HTTP 매핑 6종 = watched+entrypoint/api-owner ·
`@Scheduled`·`@EventListener`·`@KafkaListener` = watched+entrypoint/platform-reviewer.
`source` 는 형제 정책의 `builtin:`/`org:` 에 **`framework:` 추가**(프레임워크 공식 의미론이 근거인 항목이 다수).
**AC 초과 3종**(전부 과탐 방향·정책 소유자 판단): `@PermitAll`·`@DenyAll`(인가 **해제/차단** 선언 = 인가 약화의
가장 직접 신호 — 형제 4종만 넣으면 구멍) · `@Put/Patch/DeleteMapping`(DELETE 진입점 제외는 정당화 불가).

**🔴 불변식 3개(구현 필수)**:
1. **이 카탈로그 level 은 protected|watched 뿐 — frozen 금지**. 프레임워크 어노테이션은 **추론 신호(2·3층)**
   이고 2·3층은 자동 차단 금지(CLAUDE.md §4·D-004). `@Transactional` 붙인 사람이 동결을 선언한 적 없다.
   frozen 오면 **검증오류 + protected clamp**(조용한 무시 금지). ↔ `@Gov(level=frozen)` 은 **저자 명시 선언**
   = 1층 등가라 blocked 가능(AC#1 · Python parity) ⇒ 게이트는 **declared vs inferred 출처를 끝까지 구분 보존**
   해야 한다. 뭉쳐서 max 만 취하면 프레임워크 카탈로그가 frozen 을 만들 경로가 열린다.
2. **`entrypoint` 는 판정 무영향** — verdict 는 `level` 에서만. entrypoint 는 카드 메타데이터 + 후속 L3
   진입점 시드. 이걸로 등급을 올리면 정책 외부화가 무력화된다(등급 드리프트).
3. **정책 부재/불량 fail-closed**: 명시됐는데 부재 → `approval_required` + 사유(차단 금지, 2·3층 상한).
   **`kit/run.sh` 에 `$POL/framework-annotations.yaml` 절대경로 배선 + preflight 필수정책 루프 추가**를
   **AC 가드로 요구** — TASK-029 **R-4** 가 정확히 이 누락으로 킷 사용자 전원 상시차단을 만들었다. 3회차 금지.

**🔴 Java `stub → supported` — 단순 플립 불승인(조건부 승인)**: `status` 는 언어당 스칼라 1개인데
`language-router.py:117` 이 이를 `deep_analysis: available` 로 그대로 번역한다. J2 시점 사실은
inventory ✅ / gov_level ✅ / **capabilities ❌(J3 미착수)** / callgraph ❌ 이므로, `supported` 로 올리면
카드가 **하지도 않은 Java 능력분석을 보증**한다 — `Runtime.exec` 신규 도입 Java PR 이 무신호 통과하는데
카드는 "available" 이라 말하는 **조용한 통과 + 허위 카드**(D-074 O-5 가 예고한 실패). 요구:
①`layers:` 층별 스키마 도입(java/python 동형, dev+kit) ②소비자는 `layers.<layer>` 를 읽고 **`supported`
정확일치만 available**(`partial`·미지값 = fail-safe 아님) ③카드 coverage 를 **층별**로 서술
④**🔴 가용성은 정책이 아니라 실측** — `parse_error` 파일은 정책 status 와 무관하게 카드 미분석 목록에
반드시 노출(**status 플립의 하드 전제**) ⑤회귀 픽스처(현재 이 경로 **0건 = 미측정**) + 음성검증 단독 FAIL.

**킷**: `sync-from-dev.sh:32` 가 `policies/*.yaml` 통째 복사 ⇒ 신규 정책은 sync 로 자동 반입.
단 manifest 종수·README 갱신 + **dev↔kit md5 동일성(D-068) 재확인**은 TASK-031 브랜치에서 Codex 가 수행.
Claude 는 킷 매니페스트 무접촉(킷 도구 = Codex 소유).

**TASKS.md AC 반영**: TASK-031 에 **AC#8(정책 계약·불변식)** · **AC#9(layers + 실측 가용성 = supported 전제)** 신설,
AC#5 에 익명 내부클래스·로컬 클래스 고정 적대 픽스처 명시(D-073 O-1), AC#7 에 러너 훅 명시(D-069 O-B),
O-4(게이트 파일 결손 픽스처) 편입.

**머지 판정(D-007)**: codex 브랜치(질문 문서) **비민감 ⇒ `main` 머지**. 정책·답변·AC 기록도 `main` 머지.
상세 = `collab/answers/A-0032.md`

---

## D-076 (2026-07-20) TASK-031 J2 층별 `language-routing` 정책 — **Q-0006 답변 · 정책 확정**(리뷰 아님)

**대상**: `codex/2026-07-20-task031-java-gov-level` (`54fe2e8` / 헤드 `2a47e64`). **미머지 codex 브랜치는
이 1건뿐**이었고 델타는 `collab/questions/Q-0006.md`(24줄) + handoff/summary 기록 = **구현 코드 0줄**.
⇒ 리뷰 통과/보정요청이 아니라 **정책 답변**이 정확한 처리. 비민감(협업 큐 문서) ⇒ D-007 로 `main` 머지.
handoff 최신 줄은 D-075 **답변·머지 완료**라 "보정 차례" 브랜치 없음. TASK-031 구현 WIP 는 미커밋 =
제출물 아님이라 무접촉(D-075 와 동일 판단).

**Codex 판단이 정확했다(2회 연속)**: `policies/*` 는 Claude 소유이고 AC#9(a) 는 **정책 스키마 변경**을
요구한다. 임의 기입 + java `supported` 플립이었다면 **over-reach + 등급 드리프트** 두 건이었다.

**확정값 — 4언어 × 4층** (`policy_version: 0.1-mvp3-j0` → **`0.2-mvp3-j2`**):
python = inventory/gov_level/capabilities/callgraph **전부 supported**(TASK-005·008/009·016·018 실재 확인) ·
**java = inventory ✅(J1) · gov_level ✅(J2) · capabilities stub(J3 미착수) · callgraph stub** ·
javascript/typescript = **네 층 전부 stub**. JS/TS 에 `unsupported` 를 쓰지 않은 이유 = `unsupported` 는
**확장자 미매칭(다룰 계획 없음)** 의미로 예약돼 있고, JS/TS 는 **어댑터 등록됨·미구현** = `stub` 이 정확
(카드가 "지원 안 함"이 아니라 "아직 분석 안 함"으로 나가야 후속 커버리지를 기대할 수 있다).

**🔴 핵심 설계 결정 — legacy `status` 를 "보수적 floor" 로 재정의(플립하지 않는다)**:
D-075 는 "java 를 supported 로 올리되 층별로 정직하게" 를 요구했으나, **`status` 자체를 올리면**
아직 `layers` 를 모르는 **구 소비자**(dev 현행 `language-router.py:117`, 미동기화 킷 사본)가 그 즉시
`deep_analysis: available` 로 번역한다 = **정책만 머지돼도 허위 카드가 생기는 창(window)** 이 열린다.
⇒ `status` = **네 층 전부 supported 일 때만 `supported`** 인 deprecated floor 로 정의하고 **java 는
`stub` 으로 유지**한다. 층 승격은 오직 `layers` 로만. 이로써 **정책은 구 소비자에 완전 inert**,
승격은 소비자 이관과 **원자적으로** 일어난다. (Codex 에게 "`status` 를 올리지 마라"를 명시 지시.)

**소비자 계약 6개(AC#9(b) 구체화)**: (a) **`supported` 정확일치만 available** — `partial`·`stub`·미지값·
층 키 부재·`layers:` 블록 부재 전부 not-available(fail-safe) · **대소문자 정규화 금지**(`Supported` 오타는
과소주장으로 떨어지는 게 옳다) · 열거(`defaults.layer_states`) 밖 값은 not-available + `errors` 흔적
(**조용한 통과 금지**) (b) **`layers:` 부재 시 legacy `status` 로 역추론 금지** — 하면 D-074 O-5 허위 카드
부활 (c) `status` 무시 (d) **🔴 가용성은 정책이 아니라 실측** — `parse_error` 파일은 층 상태와 무관하게
카드 미분석 노출, **어긋나면 실측이 이긴다**(D-074 R-1 계열) (e) 카드 coverage **층별 서술** — 기존
`deep semantic analysis not yet implemented for .java` 단일 문구는 J2 부터 **거짓**이며 특히
**capabilities 미분석은 명시**(`Runtime.exec` 신규 도입 Java PR 이 무신호 통과함을 승인자가 알아야 함)
(f) **층 상태는 verdict 무영향**(D-075 불변식 2 동형 — stub 이라고 과차단, supported 라고 하향 금지).

**실측(가정 아님)**: `tests/run-tests.sh` 변경 전 **111/111** ↔ 후 **111/111** 동일. **픽스처 밖 fresh repo**
(신규 생성 · `app/auth/Guard.java` `@PreAuthorize` 인가 약화 `ADMIN→USER` + 같은 diff 에 `svc/calc.py` 변경):
구/신 정책 카드가 **`policy_sha` 한 줄 빼고 바이트 동일**, 둘 다 `verdict: approval_required` ·
사유 `protected:...:인증/인가`(경로층 = 언어 무관). 라우터 단독도 동일 — `Guard.java → status stub ·
deep_analysis not_yet_available` ⇒ **floor 설계가 실제로 과소주장 쪽으로 떨어짐을 실증**.
`policy_sha` 변화는 정책 내용이 실제 바뀐 결과라 **정상·의도**.

**Codex 잔여 몫**: dev↔kit md5 동일성(D-068) 재확인 + manifest/README 갱신(`sync-from-dev.sh` 가
`policies/*.yaml` 통째 복사라 반입은 자동) · 소비자 게이트 dev↔kit 동일 · **AC#9(e) 회귀 픽스처
(현재 0건 = 미측정)**: ①파서 부재 강제 + `inventory: supported` → 미분석 노출·**exit 0**(차단 아님)
②카드 문구가 capabilities 미분석 명시 ③`layers:` 없는 구 스키마 → 전 층 not-available ④`partial`·오타 →
not-available, 각각 **음성검증 단독 FAIL** 까지가 AC.

**하류**: TASK-032(J3) 완료 시 승격 지점은 `java.layers.capabilities: stub → supported` **한 줄**(값 변경은
Claude 가 수행). legacy `status` 삭제는 **전 소비자 이관 + 킷 동기화 이후**(지금 지우면 미동기화 킷이
전 언어 `unsupported` 로 떨어져 신호 손실). 이 층별 스키마는 L3 진입점·콜그래프 등 "언어 단위 이분법이
거짓이 되는" 모든 후속 층에 재사용된다.

**머지 판정(D-007)**: codex 브랜치(질문 문서) **비민감 ⇒ `main` 머지**. 정책·답변 기록도 `main` 머지.
상세 = `collab/answers/A-0033.md`

---

## D-077 (2026-07-20) TASK-031 J2 Java 함수레벨 게이트 리뷰 → **보정요청 R-1/R-2 · 코드 머지 보류**

**대상**: `2e5d644`(구현) / `9bec936`(핸드오프) · `codex/2026-07-20-task031-java-gov-level-impl`
**판정**: **보정요청**. R-1 은 거버넌스 직접 구멍이라 CLAUDE.md §2B 에 따라 비차단 이월 금지. 상세 `collab/answers/A-0034.md`.

### 확정 1 — 통과한 것 (실증)
픽스처 밖 fresh repo 로 AC#1·#2·#3·#5(오버로드·익명/로컬 클래스)·#7(`Group parity 2/2`)·#8(a~f 전부)·#9(a~d) **직접 재현 확인**.
특히 **AC#3 제거 우회 차단**(`@PreAuthorize` 삭제 → `side: base` 로 생존), **AC#8(b) FQN 인라인 매칭**,
**AC#8(d) 카탈로그 frozen 금지**(정책 rig → 검증오류 + protected clamp, frozen 은 선언 `@Gov` 만),
**AC#8(f) `run.sh` 배선 + preflight + `--policies` 오버라이드**(TASK-029 R-4 3회차 방지 성공) 확인.
`tests/run-tests.sh` **122/122** · `kit/tests/run-entrypoint-tests.sh` **20/20** · `kit/selftest.sh` **PASS**(mutation 205) ·
dev↔kit 게이트 21 + 정책 8 **md5 전량 동일**(D-068 유지).
음성검증: 기대값 변조 → **단독 FAIL**(121/122). rig-and-revert: `java_analysis_unavailable()` → `return False` 시
`java-analysis-unavailable-evidence-coverage` **단독 FAIL** ⇒ 신규 가드 **load-bearing**.
이 환경은 `tree_sitter` **실설치**라 D-074 와 달리 양성 Java 경로를 **shim 없이 네이티브 검증**했다.

### 🔴 확정 2 — R-1: Java 파싱 실패 파일이 gov_level 축을 **조용히 통과**시킨다 (AC#4 위반 · parity 파손)
`java_result_from_source()` 가 `(SyntaxError, ImportError, OSError)` 를 **한 메시지로 뭉개고**,
`java_analysis_unavailable()` 이 이를 **문자열 부분일치**로 판정해 본 루프가 **`continue`** —
`parse_failed()` 기반 **fail-closed 블록에 도달하기 전에** 파일을 건너뛴다.

**킷 end-to-end A/B 실증** (동일한 `@PreAuthorize` ADMIN→USER 인가 약화, 유효 `change-intent` 선언):
- 같은 파일에 파싱 불가 메서드 1개 **추가** → **🟢 PASS · exit 0 · `reasons: []`**
- **미추가** → 🟠 APPROVAL_REQUIRED · exit 2 · `function_protected:...:base`/`:head`
⇒ **망가진 메서드 하나를 덧붙이면 인가 경계 변경이 무사통과한다.** Python 형제 경로는 같은 조건에서 exit 2 = **언어 간 반대 판정**.

**정책 소유자 경계 확정 (이번 결정의 핵심)** — AC#4 와 AC#9(e) 는 **서로 다른 두 조건**이며 합치면 안 된다:
- **툴체인 부재**(`ImportError`/`OSError`) = 환경 조건, 모든 `.java` 에 균일 → **exit 0 + coverage 노출**(현행 유지).
  의존성 미설치로 전 PR 을 승인요구로 만드는 것은 D-074·D-076 이 의도적으로 피한 실패다.
- **파일별 구문오류**(`SyntaxError`) = 내용 특정, 그 파일의 `@Gov`·`@PreAuthorize` 를 임의로 은닉 가능
  → **AC#4 그대로 `approval_required`(exit 2). blocked 아님.**
전자는 "못 봤고 그렇게 말했다"(정직), 후자는 "숨겼는데 통과라 말했다"(허위 카드).
보정은 **예외 종류 구조화 보존**(`unavailable_kind: toolchain|syntax`, 문자열 부분일치 금지) + `syntax` 는 fail-closed 경로로 +
**회귀 픽스처 3종**(구문오류→exit 2 / 툴체인부재→exit 0 / 각각 음성검증) + **parity 쌍 확장**.

### 🟠 확정 3 — R-2: AC#5 "게이트 파일 결손"(D-074 O-4) 픽스처 **두 태스크 연속 0건**
동작은 안전(수동 재현 시 `approval_required` exit 2 = fail-closed)하나 **Traceback 그대로 노출**이고,
AC 가 명시 요구한 픽스처가 또 누락 ⇒ 이번에 닫는다. 형제 Python 생존 단언 + 음성검증 포함.

### 비차단 관찰 (차기 AC 후보)
- **O-1(TASK-032)**: 오버로드가 단일 이름으로 정규화 → 어노테이션 귀속이 이름 기준(**과탐 방향이라 안전**). J3 시그니처 키 도입 시 정밀화.
- **O-2**: frozen clamp 기준 `allowed_levels` 를 **정책 파일 자신**에서 읽어 D-075 불변식 1 이 정책값으로 껐다 켤 수 있다.
  현 정책은 올바르고 `policies/*` 는 Claude 소유라 실질 위험은 낮으나, 불변식은 **코드 하드 플로어**가 옳다.

### 보수적 개발 (COMMON-RULES §1)
문제 없음 — 변경은 TASK-031 범위 내(게이트 3종 + 배선 + 픽스처 + dev↔kit 동기화), 무관한 리팩터·포맷 없음,
Claude 소유 `policies/*.yaml` 무수정(kit 사본은 sync 반입분·md5 동일). `scope-creep`·`over-reach` 해당 없음.

### 절차
코드 브랜치 **머지 보류**. 리뷰 기록(A-0034·D-077·review-notes·handoff)은 **`main` 머지**(다음 세션 가시성).
Codex 는 재제출 전 **`origin/main` 머지 필수**(collab-protocol §5.1).

## D-078 (2026-07-21) TASK-031 J2 보정 재제출 재리뷰 → **통과 · `main` 머지**

**대상**: 보정 커밋 `d7bc1be` 만(멱등성 — `2e5d644`/`9bec936` 은 D-077 처리분, 재처리 금지).
**결론**: D-077 의 **R-1·R-2 모두 폐쇄** 확인 ⇒ 리뷰 통과 · **비민감**(하네스 게이트 코드,
프로덕션 인증/인가 아님 · 변경 방향이 *더 엄격*) ⇒ D-007 로 Claude 가 `main` 머지.

**R-1 폐쇄(실증)**: `SyntaxError` ↔ `ImportError`/`OSError` 를 `unavailable_kind`
(`syntax`/`toolchain`)로 **구조화 분리** — 문자열 부분일치 술어 제거. coverage skip 은
toolchain 만, syntax 는 Python 형제와 동일한 fail-closed 경로. 픽스처 밖 fresh repo
(`@PreAuthorize` ADMIN→USER)에서 **파싱불가 메서드 덧붙임 → exit 2**(보정 전엔 PASS·exit 0·`reasons: []`).
**rig-and-revert**로 보정 전 동작 재현 시 PASS 복귀 ⇒ 가드 **load-bearing**.

**🔴 자기교정 기록(방법론)**: 1차 exploit repo 를 `app/auth/` 에 두어 `**/auth/**` **경로층**이
판정을 대신 실었고 — rig 를 걸어도 exit 2 라 "고쳐졌다"로 **오판할 뻔했다**. `app/report/`(zone free)로
옮겨 **gov_level 단독 축**을 분리한 뒤에야 유효 검증이 성립. ⇒ **다축 러너에서 축 분리 없이 한
적대 실험은 가짜 통과를 만든다** — 이후 리뷰의 상설 절차로 삼는다.

**R-2 폐쇄**: head syntax 실패 시 base 민감 어노테이션을 reason 에 보존
(`Guard.canTransfer:base:메서드 진입 전 인가 규칙` + `<file>:head:...could not be parsed`).
해당 한 줄 제거 rig → base 신호 완전 소실 ⇒ load-bearing.

**정책 경계 유지**: 툴체인 부재(`tree_sitter` ImportError 강제) → **exit 0 + 카드 파일별
coverage 노출** 유지(전 PR 승인요구 실패 회피) · 구문오류만 최소 `approval_required`(차단 아님,
2·3층 자동차단 금지 준수) · 카탈로그가 frozen 을 만드는 경로 없음(D-075 불변식 1).

**킷 실측**: 게이트 md5 **19/19 동일** · 정책·`cases.yaml` 동일 · 킷 누락 0 (D-068 유지) ·
`tests/run-tests.sh` **127/127**(parity 4/4) · entrypoint **20/20** · `selftest` PASS(mutation 213) ·
기대값 변조 → **단독 FAIL 126/127**. 세 스위트 **순차** 실행.

**보수적 개발**: 범위 밖 파일·리팩터 없음 · `scope-creep`/`over-reach` 없음.

**비차단(후속 AC)**: **O-1** `ACGH_JAVA_INVENTORY_PATH` 시험용 env override 가 임의 파이썬
파일을 실행 — 단 적대 스텁은 **BLOCKED**, 조용한 스텁도 gov 신호 생존 ⇒ **거짓 PASS 불가**로
실측 확인(비차단 근거). TASK-032 AC 로 시험 플래그 게이팅 권고. **O-2** 툴체인 부재 coverage 가
`run.sh` 콘솔에 미노출(카드에만). **O-3** 제출 브랜치가 `origin/main` 미머지(§5.1 관행 유지 요망).
**O-4** base=toolchain·head=syntax 혼합은 `continue` 선점이나 환경 균일성상 실경로 없음.

상세 `collab/answers/A-0035.md`.

---

## D-079 (2026-07-21) TASK-032 J3 Java 능력 카탈로그 **정책 계약 확정** (Q-0007 답변)

**맥락**: Codex 가 TASK-032(Java 신규능력 감지) 착수 전 `Q-0007` 로 정책값을 요청. `policies/*` 는 Claude 소유(CLAUDE.md §1)이고 프로덕션 카탈로그에 Java 항목이 없어 **blocking**. 코드 제출 아님 ⇒ 리뷰가 아니라 **정책 판단**(CLAUDE.md §2A) 업무.

**Q1 — 공유 파일 확장 vs 별도 카탈로그 → 별도 파일 `policies/java-sensitive-capabilities.yaml`.**
취향이 아니라 **실측된 회귀 방지 요건**이다. `extract-python-capabilities.py:66-69` 는 `capabilities:` 를 **언어 필터 없이** 읽고 `{imports,calls,builtins}` 밖 신호 키를 `unknown_signal_kind` **검증오류**로 만든다. `check-new-capabilities.py:258` 은 `errors` 하나만 있어도 **approval_required(exit 2)**. ⇒ 공유 파일에 Java 를 넣으면 **Java 무관 순수 Python PR 까지 전부 승인요구**. **fresh repo A/B 실증**: 무해한 2줄 Python PR → 현행 `pass`/exit 0 ↔ Java 주입 정책 `approval_required`/exit 2(`unknown_signal_kind` × 2). 이는 D-074·D-076 이 피해온 "전 PR 승인요구" 실패모드(= 게이트 신뢰 붕괴 → 사람이 무시 → 거버넌스 무력화) 그 자체. 부수 이득: Python 추출기 **무개조**(shipped 층 회귀 위험 0) · 선례 일치(J2 `framework-annotations.yaml` 도 분리) · **오배선은 시끄럽게 실패**(Java 카탈로그를 Python 추출기에 주입 → `errors: 11`, 조용한 오통과 아님). **Codex 의 질문이 이 결함을 사전 차단했다** — 임의로 확장했으면 전 Python PR 이 뒤집혔다.

**Q2 — 능력 레코드 8개** (AC#1 의 7종 + `crypto` 분할). 전부 `protected`, `crypto_hash` 만 `watched`. `command_exec`(CWE-78) · `unsafe_deserialization`(CWE-502) · `reflection`(CWE-470) · `sql_injection_surface`(OWASP A03) · `jndi_lookup`(CWE-74·Log4Shell) · `outbound_http`(OWASP A10) · `crypto`(CWE-327) · `crypto_hash`(CWE-328). 등급은 **Python 대응 항목과 대칭**으로 잡았다(과소탐 = parity 위반).
**🔴 AC#1 로부터 의도적 편차 1건**: AC#1 은 `Cipher`/`MessageDigest` 를 한 항목(`crypto`)으로 지시했으나 **분리**했다 — Python 카탈로그가 `cryptography`·`ssl`·`hmac` 은 걸면서 **`hashlib` 은 의도적으로 제외**하고, `MessageDigest.getInstance("SHA-256")` 은 체크섬 용도가 압도적이라 hashlib 과 같은 위치다. protected 로 두면 **Java 만 Python 보다 엄격 = parity 왜곡 + 잡음**. ⇒ 능력은 카탈로그에 남기되(AC#1 목록 충족·카드 노출) **등급만 watched**. `Mac`(=HMAC)은 Python `hmac` 대칭으로 `crypto` 에 유지. AC#1 이 "등급은 정책값"으로 위임했으므로 권한 내이나 **문구와 다르므로 명시 기록**(조용한 변경 금지).
**이연 2건**(조용한 누락 아님·파일에 기록): ① **인증서 검증 우회** — Java 대응은 커스텀 `TrustManager`/`HostnameVerifier` **구현**이라 `implements:` 신호가 필요(신호 스키마 밖·AC#1 목록 밖). Python 은 `ssl._create_unverified_context` 로 잡고 있어 **parity 갭으로 남음**을 인지하고 이연. ② 자격증명·PII(Python 과 동일 사유).

**Q3 — 신호 스키마 4종**: `imports`(FQN 자기/하위접두 · 와일드카드 `.*` 포함) · `types`(simple name, `new X`/정적수신자/선언타입, **마지막 점-세그먼트 매칭** → `new java.lang.ProcessBuilder()` 도 포착) · `calls`(정규화 `Type.method`, 체인의 **구문상 뿌리**가 타입이름 또는 `new X(...)`) · `methods`(수신자 무관 백스톱). Python 의 `builtins` 는 Java 에 없음.
**Java 비대칭 4케이스 해소**: (a) `java.lang` 암시적 import → import backstop 원리적 무효 ⇒ `calls` 로 커버(`Runtime.getRuntime`·`Runtime.exec`). (b) `java.io.ObjectInputStream` → import backstop 유효, **그리고 `ois.readObject()` 는 뿌리가 변수라 타입 해소 불가**(타입추론 = 값 추정 = 금지) ⇒ `imports`+`types`+`methods` **3중 계층 방어**. (c) `new ProcessBuilder(...).start()` → 뿌리가 `new X` ⇒ `ProcessBuilder.start`. (d) 미해소 동적 → **추정 금지**, `unresolved_dynamic` 으로 coverage 정직 노출(단 `Class.forName`·`Method.invoke` 등 구문상 확정분은 정상 감지).
**`methods` 사용 제한**: 4종 중 과탐 위험 최대("잡음 폭증 = 게이트 무시"는 설계 §3 이 명시한 실패모드) ⇒ **이름 자체가 고신호인 것만**(`exec`·`readObject`·`lookup`). `invoke` 는 프레임워크 관용구에 흔해 **의도적 제외**.

**Q4 — frozen 금지·protected clamp → 확인. 단 코드 하드 플로어로 강화.** 2층은 자동 차단 금지(D-004·CLAUDE.md §4)이므로 `frozen` 은 검증오류 + `protected` clamp. **그냥 확인만 하면 D-077 O-2 반복** — clamp 기준을 정책 파일 자신의 `allowed_levels` 에서만 읽으면 **정책을 고쳐 불변식을 끌 수 있다**(정책값으로 껐다 켜지는 건 불변식이 아니다). ⇒ **TASK-032 AC#7 로 명시 가드화**: 코드 하드코딩 상한 + 정책은 *좁히는* 방향만 허용 + 검증은 `level: frozen` **과** `allowed_levels: [frozen]` **동시 rig**(한쪽만 rig 하면 이 결함을 못 잡는다) + 음성검증.

**Q5 — `language-routing.yaml` 승격 → stub 유지, 승격은 Claude 가.** D-076 under-claim 계약상 `supported` 는 실제 동작하는 층에만 — 구현 중 선승격은 카드가 "deep analysis available" 이라 **거짓말**(D-074 O-5 금지 false card). 통과 후 Claude 가 `capabilities: supported` 로 올리되 `callgraph` 가 stub 이므로 **`status:` 는 stub 유지**(전 층 supported 일 때만 승격). Codex 는 이 파일 무수정. AC#11 로 명문화.

**미결 관찰 2건 AC 화**(CLAUDE.md §2B — 거버넌스 영향 관찰은 비차단으로 흘리지 않는다): **D-078 O-1** → **AC#8**(`ACGH_JAVA_INVENTORY_PATH` 계열 임의 파이썬 실행 env override 를 프로덕션 기본 비활성 + 명시 시험 플래그 필요 + 무시 사실 coverage 노출) · **D-077 O-2** → **AC#7**(위). 추가 **AC#9**(정책 분리 + 무해 Python PR pass 유지 회귀 픽스처 + Python 추출기 무개조) · **AC#10**(킷 sync + `run.sh` 배선·preflight·`--policies` — TASK-029 R-4 계보로 3회 연속 누락 방지) · **AC#11**(라우팅 승격 주체).

**검증**: Java 카탈로그 YAML 파싱 PASS · 능력 8 · 중복 id 0 · level 위반 0 · 필수필드 누락 0 · 미정의 신호종류 0 · frozen 0 · 분리 후 무해 Python PR `pass`/exit 0 유지 · 교차소비 음성검증 `errors: 11`.

**머지 판정**: Codex 제출분(`codex/2026-07-21-task032-java-capabilities`)은 **질문 문서 3파일 48줄·게이트 코드 0줄 = 비민감** ⇒ D-007 로 `main` 머지(`24cf778`). 이번 Claude 산출물은 **정책 신규 파일**이라 성격이 다르나 ① 2층 승인상한 유지로 **차단 권한을 늘리지 않고** ② 판정 방향이 **더 엄격(과탐)** 쪽이며 ③ 아직 **어떤 게이트도 이 파일을 읽지 않는다**(routing 은 stub 유지 = 무효과) ⇒ **비민감**으로 판단해 머지. 실제 활성화는 TASK-032 리뷰 통과 + 라우팅 승격 시점이며, **그 시점이 민감 판정 지점**이다.

상세 `collab/answers/A-0036.md` · `policies/java-sensitive-capabilities.yaml` · TASKS.md TASK-032 AC#7~#11.

---

## D-080 (2026-07-21) TASK-032 J3 Java 능력 카탈로그·신규능력 감지 리뷰 → **통과 · `main` 머지** (Claude)

**대상**: `codex/2026-07-21-task032-java-capabilities-impl` — `b2f847e`(구현) · `42bdce4`(handoff). 58파일 +1866/-63.

**판정: 리뷰 통과.** AC#1~#11 **전 항목 실증 충족**. 상세 `collab/answers/A-0037.md`.

**적대적 검증 (거수기 아님 — 픽스처 밖 fresh 입력으로 독립검증)**:
AC#3 고정 적대 세트를 **내가 새로 작성한 Java 소스**로 재현 — 리플렉션 `Method.invoke` · 문자열조립 SQL · `Class.forName` 동적로드 **3종 전부 포착**. 추가로 **`java.lang` 암시적 import 비대칭**(import 문 없는 `Runtime.getRuntime().exec`) 과 **FQN 인라인**(`new java.lang.ProcessBuilder()`) 도 포착 확인 — AC#2 가 요구한 비대칭 해소가 실제로 작동한다. **난독화 내성**(고정 세트 밖·내 설계): 리플렉션 핸들을 `Object` 필드로 세탁 후 캐스팅 호출 → 여전히 `reflection` 포착 + 미해소 수신자 `unresolved_dynamic` 정직 노출 ⇒ 계층 방어(imports+types+calls+methods) 실작동.

**AC#7 (D-077 O-2 폐쇄) — 이중 rig 통과**: 정책을 `level: frozen`(7건) **과** `allowed_levels: [frozen]` **동시** rig → 등급 `protected` clamp · `errors` 7건 `invalid_capability_level` · exit **2**(exit 1 없음). 결정적으로 게이트는 `allowed_levels` 를 **코드에서 전혀 읽지 않고** `VALID_LEVELS` 코드 상수로만 판단 ⇒ **정책 편집으로 불변식을 끌 수 없다**. **음성검증(rig-and-revert)**: `VALID_LEVELS` 에 `frozen` 추가 → `java-capabilities-frozen-clamp` **단독 FAIL**(139→138), 되돌리면 139/139 ⇒ 가드가 **load-bearing**.

**AC#8 (D-078 O-1 폐쇄)**: `ACGH_JAVA_INVENTORY_PATH` 에 **임의 파이썬 파일**을 지정해 양방향 실증 — 플래그 없으면 **무시**(임의코드 미실행), `ACGH_ALLOW_TEST_OVERRIDES=1` 이면 로드. 게이팅 실동작 확인.

**AC#9 (D-079 계약)**: `extract-python-capabilities.py` **diff 0줄**(무개조) · Claude 소유 파일 수정 **0건** · 무해 Python PR `pass`/exit 0 유지.

**킷 집중 검토 (AC#10 — 배포 최전선)**: dev↔kit **md5 3쌍 전부 동일**(바이트 동일, 개수만이 아님) · `run.sh` 의 `JAVA_CAPS` 가 **기본·`--policies` 재바인딩 후 2곳 모두** 반영 · verdict 조립 `1>2>0` 우선순위가 게이트 exit 의미와 정합하고 `cap_exit` 이 **양 분기 모두** 배선 · `HAS_RANGE=0` → `cap_exit=2` fail-closed · **6-file 레거시 override 디렉터리**로 실행 시 preflight 가 exit 2 + 명확 메시지로 차단(조용한 통과 아님) · **E2E**: 내 적대 Java repo 에 `kit/run.sh` → `능력=2` → `🟠 APPROVAL_REQUIRED (exit 2)` · **진입점 적대 22/22 PASS**.

**테스트**: dev **139/139** · 진입점 **22/22** · 음성검증 2종 모두 단독 FAIL 확인.
✅ **킷 자체시험 `kit/selftest.sh --quick` → 139/139 + 진입점 22/22 PASS**(킷의 지원 진입점 — 임시 작업공간에 `.harness/gates`·`policies`·`templates` 를 심링크해 개발 레이아웃을 재구성한 뒤 실행). ⚠️ **자기정정**: 처음에 `kit/tests/run-tests.sh` 를 **직접** 호출해 0/139 를 보고 "선재 결함" 으로 판단했으나 **오진** — 그 스크립트는 단독 실행용이 아니라 `selftest.sh` 가 만드는 레이아웃을 전제한다(main 대조군 0/110 도 동일 사유). **결함 아님, 킷 스위트 정상.**

**보수적 개발(COMMON-RULES §1)**: Claude 소유 파일 0건 수정 · 기존 게이트 2개 수정은 **AC#8 이 지시한 6줄씩**뿐 · 무관 리팩터/포맷 없음 ⇒ `scope-creep`·`over-reach` **없음**.

**비차단 관찰 3건 → 전부 차기 AC 가드로 명시**(CLAUDE.md §2B — "거버넌스에 구멍 내나?" 를 먼저 물었고 셋 다 아니오, 그러나 표류시키지 않는다):
- **O-1 두 카탈로그 무조건 선로드**: 변경 경로에 `.java` 가 **하나도 없어도** Java 카탈로그를 항상 로드 → 파일 부재 시 `approval_required`. **실증**: 무해 2줄 Python PR 이 두 정책 존재 시 `pass`/exit 0 ↔ Java 정책 부재 시 **exit 2**. **fail-closed 방향이고 킷은 preflight 가 먼저 막아 비차단**이나, D-079 가 지목한 "Java 무관 Python PR 전량 승인요구" 실패모드가 **파일 부재라는 다른 문으로 재진입**했다. AC#9 픽스처는 "두 정책 존재"만 봐서 못 잡는다. ⇒ **차기 AC**: 언어 카탈로그 **지연 로드**(해당 언어 경로 변경 시에만) + "Java 정책 부재 + 순수 Python PR → pass/exit 0" 회귀 픽스처 + 음성검증.
- **O-2 무정보 타입 바인딩이 정직성 신호를 억제**: `unresolved_dynamic` 은 `not root_type` 일 때만 기록되는데 `var` 선언이 타입명을 문자 그대로 `"var"` 로 바인딩(**실증**: `{'st': 'var'}`) ⇒ `var`·`Object` 같은 무정보 바인딩이 truthy 라 매칭도 실패하고 미해소 노출도 **억제**. **현재 실측 미탐 0**(카탈로그가 **획득 지점 정적 팩토리**를 걸어둬 `var` 수신자여도 획득 호출에서 잡힘 — `var st = c.createStatement()` 도 정상 포착)이라 비차단이나, **이 안전성이 게이트 코드가 아니라 카탈로그 작성 습관에 의존**한다. 획득 지점 없는 능력을 추가하는 순간 **조용한 미탐**. ⇒ **차기 AC**: 무정보 바인딩(`var`·`Object`)은 **미해소로 취급**해 `unresolved_dynamic` 노출 + 픽스처 + 음성검증.
- **O-3 AC#8 coverage 문구 미이행**(경미): override 무시 시 그 사실을 coverage 에 남기라는 부분 미구현(게이팅 동작 자체는 완전). ⇒ 차기 AC 에 포함.

**D-007 처리**: **통과 + 비민감**(하네스 자체 분석/추출 게이트 — 정산·인증/인가·암호화·DB migration·infra 무해당. TASK-029/030/031 과 동일 선례 D-072·D-074·D-078) ⇒ Claude 가 `claude/2026-07-21-review` 에서 `main` 머지(구현자 Codex ≠ 머지자 Claude).

**AC#11 승격 — 시도 후 단독 실행 불가 실측 ⇒ R-1 로 이월**: 승격을 실제 적용해 회귀를 측정했다. `java.layers.capabilities: supported` 로 올리면 dev 스위트가 **139/139 → 136/139** 로 떨어진다(`evidence-language-coverage`·`evidence-java-syntax-error-preauthorize`·`java-analysis-unavailable-evidence-coverage`). **원인은 결함이 아니라 정확성 개선**이다 — 세 케이스가 카드 coverage 문자열 `java .java layers not available: callgraph, capabilities` 를 단언하는데, 승격 후엔 `... not available: callgraph` 로 **좁아지는 게 맞다**(capabilities 가 실제로 available 해졌으므로). 즉 픽스처가 승격 전 문자열을 박아둔 것.
**그러나 승격 완결에는 3파일이 함께 움직여야 한다**: ① `policies/language-routing.yaml`(Claude 소유 ✅) ② `kit/policies/language-routing.yaml`(킷 sync — 현재 dev↔kit md5 동일 `41d4f3a9…`, 한쪽만 바꾸면 킷 동일성 파손) ③ `tests/cases.yaml` 기대문자열 3건. **②③ 은 Codex 소유**(CLAUDE.md §1)라 Claude 가 손대면 안 되고, **정책만 바꿔 머지하면 `main` 이 136/139 red 로 남는다**. ⇒ 이번 푸시에서 승격을 **의도적으로 보류**하고 **R-1**(후속 작업 지시, **반려 아님**)로 Codex 에 넘긴다. AC#11 이 "승격 주체 = Claude" 라고만 정하고 **Codex 소유 파일 동반 수정 필요를 설계에서 빠뜨린 공백**을 여기 명시 기록한다.
**R-1 절차**: Codex 가 (a) `tests/cases.yaml` coverage 기대 3건을 `... not available: callgraph` 로 갱신 + (b) `kit/policies/language-routing.yaml` sync 를 **한 커밋**으로 올리면, Claude 가 (c) `java.layers.capabilities: supported` 를 얹어 **함께 머지**한다. `java.status` 는 **`stub` 유지**(`callgraph` stub ⇒ D-076 under-claim: 전 층 supported 일 때만 승격). 검증 = dev 139/139 복귀 + dev↔kit md5 동일 + 승격 문자열 음성검증.

**멱등성**: `b2f847e`·`42bdce4` 재처리 금지. **MVP-3 J 라인(TASK-029~032) 완결** — 다음은 W1(프론트) 또는 X(콜그래프→간접영향) AC 정밀화.

## D-081 (2026-07-21) TASK-032 R-1 Java capabilities 층 승격 재리뷰 → **보정요청 · merge 보류** (Claude)

**대상**: `codex/2026-07-21-java-capabilities-routing-r1` — `fa45ccb`(test/policy) · `eda00f5`(handoff). 상세 `collab/answers/A-0038.md`.

**판정: 보정요청 (반려 아님 = 재작업 지시).** R-1 의 **dev 측은 정확·검증 통과**, 그러나 **킷 sync 불완전**으로 킷의 지원 자체시험 `kit/selftest.sh --quick` 이 **RED(4건)** 라 머지 보류.

**dev 측 실증 (Claude 가 (c) 정책 승격을 얹은 합동 상태)**: dev `tests/run-tests.sh` **139/139**(승격 전 136 → 복귀) · dev↔kit `language-routing.yaml` **md5 동일** `fe496593…`(승격 후에도 바이트 동일) · **음성검증 A**(정책만 stub 로 되돌림 + 승격 문자열 유지 → 대상 3케이스 정확히 단독 FAIL 139→136 ⇒ 문자열이 정책에 load-bearing) · **음성검증 B**(기대 하나만 옛값 변조 → 1케이스만 FAIL 139→138 ⇒ 항상-PASS 아님) · `mutation-check` PASS · coverage 문자열 정합(`documented_layers` 정렬상 `capabilities` unavailable→available ⇒ `not available: callgraph` 로 정확히 좁아짐, `java.status` stub 유지로 D-076 under-claim 준수) · `.java`+`coverage_not_checked` 단언 = 정확히 3케이스뿐(모두 갱신, 놓친 dev 케이스 0).

**🔴 결함 — 킷 sync 불완전(배포 킷 RED)**: 킷은 dev 전량 미러(policies **와** tests 미러 모두 vendoring)인데 R-1 은 `kit/policies/language-routing.yaml` 만 승격하고 **킷 테스트 미러 2개를 sync 안 함** ⇒ 킷 정책(supported)과 킷 기대값(승격 전)이 내부 모순:
- `kit/tests/cases.yaml` L153·L455·L1170 → 여전히 `... callgraph, capabilities` ⇒ **cases 3건 FAIL**
- `kit/tests/run-entrypoint-tests.sh:138` grep → 여전히 `... callgraph, capabilities` ⇒ **진입점 1건 FAIL(21/22)**

**실증**: `bash kit/selftest.sh --quick` → 3 cases FAIL + `Entrypoint summary: 21/22` + `✗ selftest FAIL`. 킷이 **정확한 출력(`callgraph`)** 을 내는데도 옛 기대값이 이를 거부한다.

**§2B — 비차단 아님**: 킷=실사용 배포 최전선, `selftest.sh`=킷의 지원 무결성 게이트. RED 채 머지=깨진 아티팩트 배포 ⇒ "후속 책임"으로 못 미룸. CLAUDE.md ★★ 킷 지침 (4)sync 빠짐없이·(5)selftest 전량 재현에 정확히 해당.

**보정 지시(Codex — 킷 test 미러는 Codex 소유)**: ① `kit/tests/cases.yaml` 3줄 → `callgraph` (dev 와 동일) · ② `kit/tests/run-entrypoint-tests.sh:138` grep → `callgraph`(킷 전용 파일 = dev 대응물 없음, 직접 갱신) · ③ **`kit/selftest.sh --quick` → 139/139 + 22/22 를 반드시 재현**. R-1 은 `tests/run-tests.sh`(dev)만 돌리고 **`kit/selftest.sh` 를 안 돌려** 이걸 놓쳤다.

**재제출**: 보정 커밋만 재리뷰(멱등). **재제출 전 `origin/main` merge 필수**(§5.1 — 리뷰 기록은 main 에만). 재제출되면 Claude 가 킷 selftest 재현 + (c) 정책 승격을 얹어 합동 머지.

**설계 공백 기록(재발 방지)**: D-080 R-1 절차가 킷 sync 대상을 `kit/policies/language-routing.yaml` 단일로만 적었다. dev `tests/cases.yaml` coverage 문자열 변경은 킷 테스트 미러(`kit/tests/cases.yaml` **및** `kit/tests/run-entrypoint-tests.sh`)까지 동반해야 한다 ⇒ **"dev tests/cases.yaml 변경 = 킷 tests 미러 동반 변경"** 을 승격·문자열 변경 태스크 킷 sync 체크리스트에 명시.

**멱등성**: `fa45ccb`·`eda00f5` 재처리 금지(보정 커밋만 재리뷰). D-080 승격 완결은 킷 보정 후로 이월.

## D-082 (2026-07-21) TASK-032 R-1 킷 미러 보정 재제출 → **통과 · AC#11 승격 합동 머지** (Claude)

**대상**: `codex/2026-07-21-java-capabilities-routing-r1` — 재리뷰(멱등) = 보정 커밋 `6e2126d`·`41284ca` 만. 선행 `fa45ccb`/`eda00f5`/`015a4e3` 는 D-081 에서 dev 측 통과 확정분(재처리 아님, 머지로 반입). 상세 `collab/answers/A-0039.md`.

**판정: 통과 — Claude 가 (c) `policies/language-routing.yaml` 의 `java.layers.capabilities: supported` 를 얹어 합동 머지.** `java.status` 는 **`stub` 유지**(callgraph stub ⇒ D-076 under-claim 계약; AC#11 "status 하한 재평가" 결과 = 변경 없음이 정답). dev↔kit 정책 **바이트 동일** md5 `fe496593…`.

**⚠️ 환경 상한 고지(정직 보고)**: 이 머신은 Python **3.9.6** 단일 인터프리터라 `requirements.txt` pin(`tree-sitter==0.26.0`·`tree-sitter-javascript==0.25.0`)이 **3.9 용으로 PyPI 에 없다**(실측 최신 0.23.2/0.23.1) ⇒ `tree-sitter-smoke` 1건이 **환경 사유**로 FAIL, 스위트 상한 **138/139**. `main`(621980d) 무변경 기준선도 **동일하게 138/139 + 진입점 22/22** 임을 대조 실행으로 확인했다 ⇒ 이 실패는 브랜치와 무관한 선재 환경 제약. (Codex 가 보고한 138/139 도 같은 원인.)

**실증(합동 상태)**: dev `tests/run-tests.sh` **138/139**(실패집합 = 기준선과 동일 1건) · 킷 `selftest.sh` cases **138/139** + **진입점 22/22** + `mutation-check` **PASS**(Expectation mutations checked **234**) · D-081 의 킷 RED(cases 3 FAIL·진입점 21/22) **해소**.

**적대 검증**:
- **rig-and-revert(R1)**: 킷 4곳을 옛값으로 되돌리면 **cases 135/139 + 진입점 21/22** 로 D-081 RED 정확 재현 ⇒ 보정 4곳 전부 **load-bearing**.
- **정책 회귀 rig(R2)**: 킷 정책만 `stub` 으로 되돌리면 cases 3건이 **잡는다**(135/139). 단 진입점은 22/22 통과 → O-1.
- **fresh 적대입력**(픽스처 밖 새 repo · `Runtime.exec` + `Class.forName`/`Method.invoke`): 2층 `command_exec`·`reflection` 감지 → **exit 2**, 카드 실물 `layers available: capabilities, gov_level, inventory` / `not available: callgraph` = **사실 일치**.
- **fail-closed 전 경로 fresh 재현**: 분석기 부재(ImportError 심) → `fail_closed` exit 2 · 카탈로그 손상(`--policies` 오버라이드) → `fail_closed` exit 2 · `HAS_RANGE=0` → 3층 전부 `range_required` exit 2 · `language-routing.yaml` 부재 → preflight exit 2 · 정책 디렉터리 부재 → preflight exit 2. **승격이 fail-closed 를 어느 것도 약화시키지 않음**.
- **킷 sync 완결성(개수 아닌 실작동)**: 합동 상태에서 `kit/sync-from-dev.sh` 재실행 → 게이트 20/20·**추가 드리프트 0**.
- **하류 영향**: `language-routing` 소비처는 `generate-change-evidence.language_coverage()` 하나뿐이고 `check-new-capabilities` 는 라우팅을 읽지 않는다(확장자로 Java 추출기 선택) ⇒ 승격의 blast radius = **카드 coverage 문구 1줄**, 판정 로직 무변경.

**🔴 왜 "합동" 머지여야 하는가(실증)**: dev 정책을 stub 인 채로 `sync-from-dev.sh` 를 돌리면 `kit/policies/language-routing.yaml` 이 **stub 으로 조용히 원복**된다(실측). 브랜치 단독 머지 시 다음 sync 에서 킷 승격이 사라지고 킷 기대값과 다시 모순 ⇒ **(c) 동반 머지는 필수**. (D-080/D-081 이 계획한 절차가 실증으로도 옳았음.)

**비차단 관찰 → 차기 AC 가드(명시)**:
- **O-1**: `kit/tests/run-entrypoint-tests.sh:138` 의 grep 이 **접두 부분일치**라 `...callgraph, capabilities` 회귀도 매치 ⇒ 진입점 단독으로는 층 회귀 맹점(R2 실증: 22/22 통과). 차기 AC = 양성 문자열(`layers available: capabilities, gov_level, inventory`)까지 단언하거나 종단 고정 매치. *(킷 자체시험 전체로는 cases 가 잡아 거버넌스에 직접 구멍은 아님.)*
- **O-2**: **D-076 trace 계약 비대칭** — 런타임에 Java 능력 추출이 실패해도 카드에는 capabilities 측 흔적이 없고(2층 결과는 카드 밖) 층은 available 로 표기된다. gov_level 은 `java gov_level analysis unavailable for <path>` 를 남긴다. 판정은 `run.sh` 2층 `fail_closed`(exit 2)로 **안전**하나, 차기 Java/카드 태스크 AC 로 **capabilities 실패 흔적을 카드 coverage 에 추가**(gov_level 대칭)를 요구한다.
- **O-3**: `kit/manifest.yaml` 의 `version: 0.3.2-mvp3-j2`·`reflects_mvp` 가 **J3 미반영**(D-080 머지 시점부터 선재). 게이트 목록은 20/20 완전이라 실행 영향 없음. `sync-from-dev.sh` 가 manifest 를 갱신하지 않는 게 원인 ⇒ 차기 킷 태스크 AC = sync 가 manifest 갱신 또는 selftest 가 선언↔반입 불일치 가드.
- **O-4(사소)**: `language-routing.yaml` 의 `status: stub  # ... capabilities/callgraph not implemented` 주석이 스테일. dev↔kit 바이트 동일 우선(킷은 Codex 소유)이라 이번엔 미수정 — 차기 킷 sync 때 dev·kit 동시 갱신.
- D-080 의 O-1(카탈로그 무조건 선로드)·O-2(`var` 바인딩)·O-3(AC#8 coverage 문구)는 **여전히 유효**.

**보수적 개발(§1)**: 킷 미러 **4줄**(cases 3 + 진입점 grep 1) = A-0038 지시 범위와 정확히 일치. 게이트·정책 로직 무접촉, 무관한 리팩터 0, Claude 소유 `policies/language-routing.yaml` 은 Codex 무접촉(AC#11 준수). scope-creep·over-reach 없음.

**머지 판정(D-007)**: 변경 성격 = 분석 층 커버리지 **선언 갱신 + 테스트 기대값 동기화**. 정산·인증/인가·암호화·DB migration·infra 무관, 판정 임계·차단 권한 무변경, 하네스 자기적용(dogfood) 실행에서 메타 게이트 `check-policy-change` 도 **완화·우회 미감지(PASS)**. 게이트 계열 Claude 머지 선례(D-039 §머지 판정) 동일 범주 ⇒ **비민감 → Claude 가 `main` 합동 머지·push**(구현자 Codex ≠ 머지자 Claude).

**멱등성**: `6e2126d`·`41284ca` 재처리 금지. **TASK-032(J3) 완결 — AC#11 승격까지 종료. MVP-3 J 라인(TASK-029~032) 전 구간 완결.** 다음은 W1(프론트) 또는 X(콜그래프→간접영향) AC 정밀화.

## D-083 (2026-07-21) MVP-3 X 단계 설계 — Java 간접영향(L3) + 잔손질 + 킷 (TASK-035~038)

**발단(형 지시)**: "둘 다 해줘, 일단 자바까지 하고 킷을 업데이트할거야." = J 라인 잔손질 + Java L3(간접영향) 완성 → 킷 반영.

**상태 검증(2026-07-21)**: MVP-3 J 라인 029~032 전부 통과·머지 확인(D-072/074/078/080·082). TASKS.md 체크박스 스테일(☐)이던 것 ☑ 로 정리. 미머지 잔재 `codex/2026-07-20-task031-java-gov-level`(+2)는 **문서-only blocker 브랜치**(D-076 정책질문·D-078로 코드 머지되며 폐기됨) = 실작업 아님.

**핵심 판단 — Java L3(X)가 W1(프론트)보다 먼저**: parity(D-062 최우선)에서 Python 은 L3(sink 역도달성·MVP-2)를 갖는데 **Java 는 `callgraph: stub`** = parity 구멍. 프론트 얹기 전에 이 구멍부터 닫아 Java↔Python parity 회복(형 "자바까지" 지시와 정합).

**현행 코드 사실 확인**: `check-indirect-impact.py`·`extract-callgraph.py`·`extract-sinks.py` 는 **아직 `.py` 하드코딩**(라인 55·76 등, `import ast`). `language-router` 는 `callgraph` 층을 선언하나 `java.layers.callgraph=stub`. → X = **Java 콜그래프/sink 추출기 신설 + 간접영향 게이트 언어중립화**(Python 골든패스 무회귀 최우선).

**태스크 설계(4건·Codex-ready AC)**:
- **TASK-035** 잔손질 7건(D-080 O-1~3·D-082 O-1~4) — **O-1 지연 로드**(변경에 `.java` 없으면 Java 카탈로그 미로드 → 순수 Python PR 과차단 제거)가 실판정 영향·최우선. 나머지는 정직성/위생. W1 복제 전 폐쇄.
- **TASK-036** Java 콜그래프 추출기(tree-sitter→IR#4) — **보수적 과대근사**(설계 §5: 인터페이스→모든 구현·`@Autowired`→모든 구현·프록시 직접엣지 = superset·놓침 없음 = 안전방향 parity). 미해소는 coverage 노출. TASK-023 대응.
- **TASK-037** Java sink 추출 + `check-indirect-impact` **언어중립화**(`.py` 하드코딩→어댑터 분기·Python 무회귀 #1) + Java 배선 + **parity 픽스처**(MVP-2 Python 간접영향 케이스 == Java 등가). 통과 시 **Java L3 완결 = parity 회복**. TASK-022/024/025 대응.
- **TASK-038** 킷 반영(sync·manifest·selftest·Java 간접영향 rig-and-revert). `java.layers.callgraph` stub→supported 승격은 Claude(D-076 계약). TASK-026/028 선례.

**순서**: 035 → 036 → 037 → 038 → (그 다음 W1 프론트 AC 정밀화). 게이트/추출기 코드 = **Codex 저자**(Claude 미작성·상호견제). 정책·AC·language-routing 승격 = Claude.

**역할 경계 재확인**: 본 결정·TASKS.md AC 는 Claude 정책면. Java 추출기·게이트 언어중립화 = Codex 구현·Claude 리뷰(비민감 분석/추출층·L3 승인상한 → Claude 머지 D-007).

---

## D-084 (2026-07-21) TASK-035 J 라인 잔손질 7건 리뷰 → **보정요청 · merge 보류 · AC#7 은 Claude 완료** (Claude)

**대상**: `codex/2026-07-21-task035-java-j-line-cleanup` (`b677220` 구현 · `fe4008f` handoff). 상세 = `collab/answers/A-0040.md`.

**결론**: 7 AC 중 **AC#1·2·4·6 통과 + AC#3 게이트단 통과**, **AC#7 은 Claude 가 직접 완료**(Q-0008 회신).
**AC#5 는 기능 동작하나 그 구현(`run.sh --json` 전환)이 킷 운영자 화면에 회귀 2건을 새로 만들어 보정요청**.

**기준선 대조(회귀 0)**: `main`(e3a006b) dev **138/139** · 킷 cases **138/139** · 진입점 **22/22** ↔
브랜치 dev **140/141** · 킷 cases **140/141** · 진입점 **24/24** · mutation-check PASS(237).
실패집합이 **양쪽 동일**(`tree-sitter-smoke` 1건 = 이 머신 Python 3.9.6 pin 부재, D-082 §2 와 동일 원인). dev↔kit 게이트 `cmp` 전량 일치.

**AC#1(위험 최대·D-080 O-1) 결정적 실증** — 픽스처 밖 fresh repo(`app/service.py` + `app/Acct.java` 공존, 정책 dir 은 repo 밖):
Python-only PR + Java 정책 부재 → `main` **exit 2 과차단** ↔ 브랜치 **exit 0 PASS**.
같은 repo `.java` PR → **exit 2 fail-closed**. `.java` 삭제만 · `.java`→`.txt` rename → 둘 다 **exit 2**(안전방향).
`run.sh`(`--name-only`, rename 검출 on)와 게이트(`--no-renames`)의 diff 의미 차이는 **양방향 모두 fail-closed** 로 흡수됨을 확인.
⇒ D-079 실패모드의 "파일부재 문 재진입"이 실제로 닫혔고 구멍은 생기지 않았다.

**rig-and-revert 6/6 load-bearing**: 지연로드 revert→`new-java-capabilities-python-benign-missing-java-policy` FAIL ·
`run.sh` preflight revert→`java-policy-lazy-python-pass` FAIL · `UNINFORMATIVE_RECEIVER_TYPES=set()`→`java-capabilities-uninformative-bindings` FAIL ·
`override_coverage` no-op→`java-inventory-override-ignored-without-test-flag` FAIL ·
정확일치 grep→부분일치 revert→`language-routing-exact-layer-negative` FAIL ·
`append_capability_trace` no-op→`missing-gate-card-trace`·`gate-timeout-card-trace` FAIL.

**🔴 보정 2건(둘 다 `--json` 전환 부작용 · 킷=배포 최전선)**:
- **R-1 2층 운영자 화면 정보 손실**: `--json` 은 게이트의 사람용 렌더러를 **대체**한다(`main()` if/else).
  실증 — `main` `protected: app/net.py::outbound_network` ↔ 브랜치 `"id": "outbound_network"`(**경로·등급 소실**).
  `level: watched` 로 바꿔도 브랜치 출력은 **동일** ⇒ protected/watched/shadow **구별 불가**.
  8개 파일이 능력 도입 시 `sort_keys=True` + `head -8` 이 **`"verdict":` 줄을 잘라먹어** 승인요구 사실조차 안 보임.
  **exit·verdict 는 무손상**(rc=2 확인) — 손상된 건 사람이 읽는 증거면이고 **2층은 카드 밖이라 대체 창이 없다**.
- **R-2 카드가 유효 YAML 아니면 `append_capability_trace` 크래시 → AC#5 의 trace 조용히 소실**:
  `yaml.safe_load` 무방비. `run.sh:223` 이 `generate-change-evidence` 출력을 성공·실패 무관하게 카드에 쓰므로
  그 게이트가 예외를 던지면 카드 자리에 traceback 텍스트가 들어가고 → `ParserError` 미포착.
  실증: 킷 콘솔에 **PyYAML traceback ~25줄** 노출 + **`capabilities analysis unavailable` 노트 미기록**.
  `run_gate` 의 traceback 감지기는 **게이트 출력만** 보므로 분석실패 집계도 안 됨.
  (블록 스타일 절단 카드는 유효 YAML 이라 정상 동작함을 별도 확인 — 트리거는 "카드가 유효 YAML 아닐 때".)

**§2B 필수질문**: 탐지·판정·exit 는 두 건 모두 무손상이라 *탐지* 구멍은 아니다. 그러나 통제 모델이
"민감하면 사람에게 라우팅"이고 2층은 설계상 카드 밖이라 **콘솔이 사람의 유일한 2층 증거창**이다.
그 창을 `main` 대비 축소한 것 + AC#5 가 새로 약속한 trace 가 실패경로에서 소실되는 것은
승인 단계 실효를 깎으므로 **비차단 금지 → 보정요청**(수정은 각각 수 줄).

**§1 보수적 개발**: scope-creep 없음(20파일 전부 AC 사정권), 무관 리팩터 없음, 판정 로직 변경은 AC#1 1건뿐(과차단 제거=안전).
**over-reach 는 R-1 이 해당** — AC#5 는 "카드에 trace"였지 "2층 렌더러 교체"가 아니었다.

**AC#7 = Claude 완료(Q-0008 회신)**: Codex 가 `policies/` 소유권을 지켜 손대지 않고 Q-0008 로 요청한 것은 **정확한 판단**.
Claude 가 dev·kit 동시 수정(드리프트 0) — `# deprecated floor — callgraph not implemented (capabilities supported since J3/TASK-032)`.
**`status: stub` 값은 유지**(D-076 보수적 하한 — `callgraph` 미구현). 검증: dev 138/139 · 진입점 22/22(기준선 동일).

**비차단 → 차기 AC 가드 4건**: **O-1** AC#3 새 `coverage` 키를 읽는 소비자 0건 ⇒ 정직표기가 감사카드 미도달
(게이팅은 완전 + D-080 이 "경미" 명시 ⇒ 비차단; 차기엔 카드 `coverage_statement` 전파) ·
**O-2** `sorted(set(...))` 가 기존 `not_checked` 큐레이션 순서를 알파벳 재배열(실패경로 한정) ·
**O-3** `HAS_JAVA_CHANGE` 가 git 종료코드를 파이프에 삼켜 git 실패=“Java 없음”(순 판정은 fail-closed) ·
**O-4 (선재·본건 무관)** 3점 range `A...B` → BLOCKED(exit 1) 로 튐, **`main`·브랜치 동일** ⇒ 별건 태스크.

**머지**: 코드 브랜치 **보류**(D-007). 리뷰 기록 + AC#7 정책 주석(Claude 소유·주석 1줄·dev/kit 동기)만 `main` 반영.
**Codex 다음 할 일**: R-1·R-2 보정 + 회귀 픽스처 2건 → 재제출(보정 커밋만 재리뷰). AC#7 은 재수정 금지(이미 닫힘).

---

## D-085 (2026-07-21) TASK-035 A-0040 보정 재제출 재리뷰 → **R-1·R-2 해소 · 통과 · `main` 머지** (Claude)

**대상**: `codex/2026-07-21-task035-java-j-line-cleanup` — 재리뷰 커밋 **`b2a9c91`(보정)·`82530a9`(handoff)**.
멱등성상 `b677220`·`fe4008f` 통과분(AC#1·2·4·6 + AC#3 게이트단)은 재처리하지 않음. 상세 = `collab/answers/A-0041.md`.

**결론**: A-0040 의 머지 보류 사유 **2건 모두 해소 ⇒ 통과 · 비민감 ⇒ Claude 가 `main` 머지**(D-007).
**TASK-035 AC 7개 전부 종결**(AC#5 = 본 보정, AC#7 = Claude 가 Q-0008 회신으로 이미 완료).

**R-1(2층 콘솔) 해소 — fresh repo 문자열 대조**: protected → `protected: app/service.py::outbound_network`,
`level: watched` 로 바꾸면 `watched: …` 로 **`main` 과 문자열 동일**. 11파일 케이스는 **8줄 + `… 외 3건`** 으로
`main` 의 무고지 절단(`head -6`, 5줄)보다 **개선**. A-0040 실증 ①②③ 전부 재현 불가.

**R-2(비-YAML 카드) 해소 — 적대검증에서 실패가 두 갈래임을 새로 규명**:
**V1(콜론 없는 예외 → dict 로 파싱)** 은 보정 전에 크래시가 아니라 **traceback 위에 `change_evidence.coverage_statement` 를
덧붙여 감사카드를 위조**했고(재현 확인), `isinstance(card.get("change_evidence"), dict)` 가드가 이를 막는다 —
**A-0040 지시보다 강한 가드이고 방향이 옳다**. **V2(콜론 포함 → `ScannerError`)** 는 PyYAML traceback **14줄 → 0줄**.
두 형태 모두 **`분석 실패: generate-change-evidence: traceback` + exit 2 로 판정 무손상**, 카드 주입 불가 상황에서도
`fail_closed: …` 가 **콘솔에 표시**되어 AC#5 trace 가 실질 회복.

**회귀 0 · 판정 무변화**: exit 코드 **6경로**(정상 protected·`HAS_RANGE=0`·정책 dir 부재·3점 range·무변경·repo 부재)
= 브랜치 ↔ `main` **전량 동일**. dev **140/141** · 킷 cases **140/141** · 진입점 **26/26** · `mutation-check` **PASS(237)** ·
dev↔kit `cmp` **드리프트 0**(20/20). 유일 실패 `tree-sitter-smoke` 는 이 머신 Python 3.9.6 **환경 실패**로 `main` 과 동일.
**킷 sync 실작동**: `sync-from-dev.sh` 재실행 후에도 `run.sh` 보정·신규 픽스처 2건 **생존** + 진입점 **26/26** 재통과.
**정직 고지**: `kit/tests/mutation-check.sh` **직접 호출**은 0/3 FAIL 이나 이는 미지원 호출(계약 = `selftest.sh` 가
`.harness/gates → kit/gates` 심볼릭 루트에서 실행)이며 **`main` 도 동일** ⇒ 브랜치 귀속 아님.

**rig-and-revert**: 사람용 요약 제거 → `capability-console-path-and-level`·`java-capability-approval` **2건 FAIL** ·
`isinstance` 가드 제거 → `evidence-exception-capability-fail-closed` **단독 FAIL** ⇒ 각각 load-bearing.

**🟡 신규 발견 → 차기 AC 가드(TASK-038 AC#5 로 명시 고정 · §2B 필수질문 통과 = 판정 구멍 아님)**:
**G-1** `try/except` 가드가 **어떤 픽스처에도 고정되지 않음** — 그것만 제거해도 진입점 **26/26 PASS**(신규 픽스처의 리그가
V1 형태라 `safe_load` 가 예외를 안 던짐). 같은 리그에 V2 입력을 주면 **traceback 14줄 재발** ⇒ 실제로는 load-bearing 인데
테스트가 증명하지 못함. (Codex 요약의 "각 보정 코드 각각 FAIL" 은 **가드 블록 단위로는 참·가드 단위로는 과대주장** — 사실 정정.)
**G-2** 게이트 stdout 이 JSON 으로 안 파싱되면(`2>&1` 로 stderr 혼입 시) **2층 블록이 헤더만 남고 완전 무출력** —
카드 파싱 실패엔 "주입 불가" 고지를 넣었으면서 게이트 출력 파싱 실패엔 고지가 없는 **비대칭**(판정은 fail-closed 유지·현재 휴면).
**G-3** shadow 렌더러가 `main` 의 `level=` 을 잃음(비집행·동봉 카탈로그에 shadow 없어 휴면).

**A-0040 이월(여전히 열림)**: O-1 `coverage` 소비자 0건 · O-2 `sorted(set())` 순서 파괴 ·
O-3 `HAS_JAVA_CHANGE` 가 git 종료코드 삼킴 · O-4(선재) 3점 range → BLOCKED(**이번에도 `main` 동일** 재확인).

**민감도·머지**: 정산·인증/인가·암호화·DB migration·infra 무해당. dogfood 결과 메타층 `check-policy-change` **PASS**,
카드 `frozen_touched`·`protected_touched` 없음 · `reviewer_required: [dev-reviewer]` ⇒ **비민감**.
변경 성격 = 킷 콘솔 출력 + 방어 가드 + 테스트. ⇒ **Claude 가 `main` 머지**(구현자≠머지자). 선례 D-074·D-078·D-080·D-082.

## D-086 TASK-036 Java 콜그래프 리뷰 — **보정요청 · merge 보류** (A-0042) — 2026-07-21

대상 `codex/2026-07-21-task036-java-callgraph` (`74b3857` 구현 · `c483b97` handoff).

**🔴 R-1 (반려 사유) — AC#2 superset 계약 위반**: `method_targets()` 의
`owners.difference_update(interface_names)` 가 수신자가 인터페이스면 **인터페이스 자신을 타깃에서 무조건 제외**한다.
Java 8+ 인터페이스는 본문 있는 메서드(`default`·`static`·`private`)를 직접 소유하므로,
**그 본문으로 가는 실제 엣지가 통째로 소실**된다. fresh 적대입력 4종 중 **구현체가 오버라이드한 경우만 동작**하고
①`default`(구현 0개) ②인터페이스 `static` ③인터페이스 본문 내 무수식 자기호출 은 전부 `unresolved` 로 흘러간다.
구조 동형인 **추상클래스 대조군은 정상 동작** ⇒ 설계 의도상 버그.

**§2B 필수질문 = 예(직접 구멍)**: `check-indirect-impact` 를 실제 import 해 실증 —
sink `AuditPort.settle` 역도달성이 1/2/3홉 모두 **NONE**, 실제 2홉 경로가 보이지 않아 변경함수가 미탐지.
**`coverage.unevaluated` 는 구제 못 함** — 254–256 에서 통과 출력될 뿐 `fail_closed_records`·verdict 에 무기여이고,
fail-closed 트리거는 `callgraph["errors"]` 뿐(197–199). ⇒ 엣지가 빠지면 그냥 `verdict: pass` = **탐지 구멍**.
따라서 비차단 관찰 금지 → **보정요청**.

**픽스처가 결함을 고정**: 위 제외 로직을 제거하면 `java-callgraph-conservative` 가 FAIL(143→142) —
기대 엣지 집합에 `PaymentPort.pay` 가 없어 현재 테스트가 오동작을 정답으로 못박음. 보정 시 기대값도 수정 필요.

**통과 확인(실증)**: 결정론 md5 2회 동일 · 오버로드 합집합 병합 · **노드 line 이 어노테이션 첫 줄**(데코레이터-라인범위
상설 관심사 충족) · 파싱실패 → `errors` → 하류 fail-closed 승격 · 빈 repo 무크래시 · IR#4 키·정렬 Python 추출기와 일치 ·
스위트 브랜치 **143/144** ↔ `main` **140/141**(회귀 0, 유일 실패 `tree-sitter-smoke` 는 `main` 동일 = 환경) ·
**rig-and-revert**: 팬아웃 `owners.update(implementations…)` 제거 → 대상 케이스 단독 FAIL ⇒ load-bearing.

**§1 보수성**: `extract-callgraph.py` **무개조**(의존조건 준수) · `policies/`·`kit/`·Claude 소유 무접촉 ·
무관 리팩터 0 · dogfood `check-policy-change` PASS ⇒ scope-creep·over-reach 없음.

**비차단 관찰(A-0042 §3)**: O-1 `owners = set()` 무효 코드(제거해도 무변화) · O-2 조상확장 무보호(제거해도 143/144) ·
O-3 픽스처의 `@Autowired`/`@Transactional` **무기능**(삭제해도 PASS — 구현은 순수 타입 기반, handoff 서술이 과대) ·
O-4 익명 내부클래스 유령 노드 · O-5 파서 파일마다 재생성 · O-6 제네릭 `[-1]` 자의적 선택 · O-7 parity 픽스처가 1홉 최소치.

**D-007 처리**: 코드 브랜치 **머지 보류**, 리뷰 기록만 `main` 머지. 재제출은 **보정 커밋만** 재리뷰(멱등성).

## D-087 TASK-036 A-0042 보정 재제출 재리뷰 — **R-1 해소 · 신규 R-2 로 재보정요청 · merge 보류** (A-0043) — 2026-07-21

대상 `codex/2026-07-21-task036-java-callgraph` — **`c71a5b0`(보정)·`c362e79`(handoff)** 만 재리뷰(멱등성: `74b3857`·`c483b97` 재처리 안 함).

**✅ R-1 종결**: 보정이 A-0042 §2.5 의 두 번째 대안(인터페이스 소유자를 아예 제외하지 않음)을 채택하고
무효 코드(O-1)까지 함께 제거. 적대입력 4종(①`default`·구현0 ②구현체 오버라이드 ③인터페이스 `static`
④인터페이스 본문 자기호출) **전부 엣지 복원**, `unresolved`·`errors` 공히 비어 미해소로 새지 않음.
**하류 verdict 실증**: `check-indirect-impact` 직접 import — sink `Caller.run` forward 2홉에서
`AuditPort.settle` **탐지 True**(`pass` → `approval_required`) ⇒ 탐지 구멍 폐쇄.
**RIG-1**: 제외 로직 복원 시 `java-callgraph-conservative` **단독 FAIL(142/144·adversarial 7/8)** —
Codex 보고 수치와 정확히 일치. 검증기가 엣지 리스트 **완전일치**를 보므로 신규 4시나리오가 **기대값 단위로 load-bearing**.

**🔴 R-2 (반려 사유 · 신규이자 선재) — `interface … extends …` 미인식**: `declaration_supertypes()` 가
`superclass`·`interfaces` **두 필드만** 조회하는데, tree-sitter-java 에서 `interface B extends A` 의 상위타입은
**`extends_interfaces` 자식 노드**로 와 두 필드 어느 쪽으로도 노출되지 않는다(직접 덤프 확인).
⇒ 인터페이스→인터페이스 상속이 `implementations`·`ancestors` 양쪽에서 **완전 비가시**
(픽스처 실제 맵에 인터페이스 간 링크 **0건**). AC#2 ① 이 명시한 "`implements`/**`extends`** 열거"의
**`extends` 절반이 미구현** ⇒ 수용기준 실효 미달.

**§2B 필수질문 = 예(직접 구멍)**: fresh 입력 — `interface PaymentPort extends BasePort` ·
`class PaymentImpl implements PaymentPort` · `BasePort` 타입 수신자 호출 →
산출 엣지가 `Caller.go → BasePort.settle` **뿐**, 실제 타깃 `PaymentImpl.settle` **소실**.
**구조 동형 추상클래스 대조군은 두 엣지 정상** ⇒ 의도상 버그(R-1 과 동일 논법).
end-to-end: 서브인터페이스 케이스 **미탐지 → `pass`** / 추상클래스 대조군 **탐지 → `approval_required`**.
`coverage.unevaluated`·`errors` **양쪽 다 빈 배열**이라 하류 fail-closed 로도 구제 불가 —
미해소 목록에조차 안 남아 **R-1 보다 은닉성이 높다**. ⇒ 비차단 금지 → **보정요청**.

**보정 비용 실증**: `declaration_supertypes` 에 `extends_interfaces`/`super_interfaces` 자식 처리 **3줄** 추가 시
소실 엣지 복원 + **전체 스위트 143/144 유지 = 회귀 0**(Claude 가 직접 패치해 확인) ⇒ 대규모 리팩터 아님.

**자기정정 2건**: ① A-0042 §2.3 의 "역도달성" 표기는 방향 오류 — `reachable_paths` 는 sink 에서
`caller→callee` **전진** 탐색(TASK-037 AC#3 "forward N홉"). 당시 엣지가 literally NONE 이라 **결론은 유효**, 표기만 정정.
② R-2 는 `74b3857` 에도 동일하게 존재한 **선재 결함으로 A-0042 에서 놓쳤다**(보정이 만든 회귀 아님).

**통과 확인**: 결정론 md5 2회 동일 · 리플렉션 `unresolved` 무회귀(AC#3) · `enum implements` 정상 ·
`A.super.f()` 해소 · 스위트 **143/144**(보정 전과 동일·회귀 0, `main` 140/141, 유일 실패 `tree-sitter-smoke` 는 `main` 동일 환경건).

**§1 보수성**: 보정 커밋 변경 = 게이트 1·`cases.yaml`·픽스처 1·handoff·summaries **뿐**.
`extract-callgraph.py`·`check-indirect-impact.py` **바이트 무변경** · `policies/` 무접촉 ·
**`kit/` `main` 과 완전 동일**(킷 반영은 TASK-038 = 스코프 정확) · Claude 소유 무접촉 · 무관 리팩터 0 ·
`py_compile`·`bash -n`·`diff --check` PASS ⇒ scope-creep·over-reach 없음.

**비차단(A-0043 §5)**: **O-8(신규)** `interface_names` 완전 死파라미터(강제 공집합화해도 143/144 무변화) ·
**O-2(이월·미해소)** 조상확장 여전히 무보호 · **O-9(신규)** 픽스처가 "인터페이스 소유자 무조건 유지" ↔
"본문 가진 것만 유지"를 구별 못함(심각도는 R-1·R-2 보다 한 단계 아래) · **O-3(이월)** `@Autowired`/`@Transactional`
무기능 서술 과대 미정정 · O-4~O-7 이월 무변화.

**D-007 처리**: 코드 브랜치 **머지 보류**, 리뷰 기록만 `main` 머지. 재제출은 **보정 커밋만** 재리뷰(멱등성).
AC#5 고정 세트에 서브인터페이스 계층 4항목(구현체 `extends` 체인 · `default` 오버라이드 · 음성검증 · 추상클래스 대조군) 추가 요청.

## D-088 TASK-036 A-0043 보정 재제출 재리뷰 — **R-2 해소 · 리뷰 통과 · `main` 머지** (A-0044) — 2026-07-21

대상 `codex/2026-07-21-task036-java-callgraph` — **`beb4c6a`(보정)·`d2469f7`(handoff)** 만 재리뷰(멱등성).

**✅ R-2 종결 · TASK-036 AC 5개 전부 종결. 재제출 불필요.**
`declaration_supertypes()` 가 `node.children` 에서 `extends_interfaces` 계열을 수집하도록 **3줄** 확장 —
A-0043 §3.4 가 제시한 패치 그대로. 반환 계약(정렬 simple name)·`method_targets`·IR 형상 무변경,
엣지는 **추가 방향으로만** 움직인다.

**픽스처 밖 fresh 적대입력 14종 전량 복원**: R-2 정확재현(`PaymentPort extends BasePort`) · 3단 체인 ·
다중 `extends A, B` · 제네릭 `extends Repo<String>` · 다이아몬드 · `enum`/`record` 서브인터페이스 구현 ·
`default` 오버라이드 체인 · 중첩(`Holder.Inner`) · 스코프명 · **추상 전용** 서브인터페이스 · 추상클래스 대조군 —
전부 구현체 엣지 복원, `unresolved`·`errors` 공히 빔.
**오염 없음**: 타입파라미터 바운드(`<T extends Number>`)·`sealed…permits`·어노테이션 modifier 가
가짜 상위타입으로 새지 않음(repo 밖 타입은 `unresolved` 로 정직하게 남음).
**병리·스케일**: 순환 `extends`(Cy1↔Cy2)·자기 `extends` **고정점 수렴·무한루프 없음** ·
300단 체인 **0.14s** · 1023 인터페이스 이진트리 **0.03s** ⇒ 새 계층 그래프 폭주 없음.

**하류 end-to-end**: `check-indirect-impact` 직접 import — sink `Caller.go` forward 2홉에서
`PaymentImpl.settle` **탐지 True**(`approval_required`), 같은 입력에 패치만 제거하면 **False**(`pass`).
A-0043 이 지적한 **조용한 `pass` 폐쇄 실증**.

**rig-and-revert 4종(음성검증)**: **RIG-A**(3줄 전체 제거) `java-callgraph-conservative` **단독 FAIL 142/144·adversarial 7/8** ·
**RIG-B**(`extends_interfaces` **만** 제거) **도 단독 FAIL** ⇒ 신규 능력이 **원소 단위로 load-bearing**(A-0041 G-1 교훈 적용) ·
**RIG-D**(조상확장 제거) **이번엔 FAIL** ⇒ **O-2(조상확장 무보호) 폐쇄 확인**(직전 리뷰까진 제거해도 PASS) ·
**RIG-E**(구현체 팬아웃 제거) FAIL(기존 가드 무회귀). **RIG-C**(`super_interfaces`·`superclass` 원소 제거)만 무변화 = 중복(O-10).
Codex 보고 수치(143/144·adversarial 7/8)는 **자기 환경 기준선 144** 기준이라 이 머신(기준선 143)의 142/144 와 **정합**.

**AC#5 요청 4항목 전부 이행**: ①구현체 `extends` 체인 ②`default` 오버라이드 양쪽 소유자 ③음성검증 ④추상클래스 대조군.
검증기가 엣지 **완전일치** 비교라 **기대값 단위로 load-bearing**.

**AC 무회귀 실증**: 결정론 md5 2회 동일 · **파일순서 무관** · **교차파일** 계층 해소 · 동명 오버로드 합집합(AC#4) ·
리플렉션 `unresolved` 유지(AC#3) · dev **143/144**·`tests/mutation-check.sh` **PASS**
(유일 실패 `tree-sitter-smoke` = 이 머신 Python 3.9.6 환경건·`main` 동일 ⇒ 브랜치 귀속 아님).

**§1 보수성**: 보정 커밋 = 게이트 1·`cases.yaml`·픽스처 1·handoff·summaries **뿐**.
`extract-callgraph.py`·`check-indirect-impact.py`·`extract-java-inventory.py`·`extract-sinks.py` **바이트 무변경**
(TASK-036 "Python 추출기 무개조" 의존조건 준수) · `policies/`·`kit/` **무접촉**(킷은 TASK-038 = 스코프 정확) ·
무관 리팩터 0 · `py_compile`·`git diff --check` PASS ⇒ scope-creep·over-reach 없음.

**🟡 차기 AC 가드 → TASK-037 AC#6 신설 (자기정정)**: A-0042·A-0043 에서 **O-4 익명 내부클래스를
"과대근사 방향=안전"이라 적은 것은 오판**이다. 실측 —
`p = new Port(){ public void run(){ new Ledger().settle(); } }` 의 본문이 `Caller.run` 이라는 **연결 안 된 유령 노드**로
오귀속되고 `Caller.go → Port.run`(본문 없는 추상 선언)은 **막다른 길** ⇒ sink forward **4홉까지 미탐지** = **누락 방향**.
`coverage.unevaluated` 에 `new Port` 가 남지만 그 필드는 **verdict 무기여**(A-0042 §2.3 확립).
**선재이며 `beb4c6a` 와 무관**(패치 유무로 산출 완전 동일 확인) ⇒ **이번 반려 사유 아님**.
TASK-036 은 판정 미연결이라 지금은 구멍이 아니나 **TASK-037 이 소비하는 순간 R-2 와 같은 모양의 실구멍** ⇒
§2B 원칙대로 비차단으로 흘리지 않고 **TASK-037 AC#6 으로 명시 고정**.

**비차단 이월**: O-8 `interface_names` 死파라미터(정리 권장) · O-9 추상 전용 인터페이스 픽스처 부재(반쪽 구현 미구별·저심각) ·
O-3 `@Autowired`/`@Transactional` 서술 과대 · O-5~O-7 무변화. **신규 O-10**: 세트의 `super_interfaces`·`superclass` 는
필드조회와 중복이나 **문법버전 드리프트 방어**로 읽어 유지 무해(결함 아님).

**정책 상태**: `language-routing.yaml` `java.layers.callgraph` 는 **`stub` 유지**.
`check-indirect-impact` 가 아직 `.py` 하드코딩이라 Java 콜그래프 **소비자 0명** — 지금 승격하면
못 하는 분석을 광고하는 셈. 승격은 **TASK-037 통과 후(dev)·TASK-038 AC#3(킷)**, D-076 계약대로 Claude 가 한다.

**민감도·머지**: 정산·인증/인가·암호화·DB migration·infra **무해당** · dogfood 메타층 `check-policy-change` **PASS**
⇒ **비민감** ⇒ **Claude 가 `main` 머지**(구현자≠머지자). 선례 D-074·D-078·D-080·D-082·D-085.
**정직 고지 + 사실 정정**: 자기보호 zone(`.harness/**`·`tests/cases.yaml`·`tests/run-tests.sh` — D-028)에 걸려
감사카드는 `verdict: approval_required`·`required_approval: security-reviewer` 를 낸다.
**D-085 에 적은 "카드 protected_touched 없음" 은 틀렸다**(TASK-035 도 같은 zone 을 건드렸다).
현행 해석 = repo 내부에선 Claude 적대적 리뷰 + 구현자≠머지자가 그 역할을 하고 D-007 의 "민감"은
CLAUDE.md §3 **도메인 목록**을 뜻한다 — 다만 명문화된 적이 없어 **H-0001** 로 형 확인 요청(**머지 보류 사유 아님**).

---

## D-089 — TASK-037 (Java sink + 간접영향 언어중립화) **보정요청** · 코드 머지 보류

**대상**: `codex/2026-07-21-task037-java-indirect-impact` — `c670753`(구현) · `67c3422`(인계) · `origin/main`=`d2c21cc` 대비.
**판정**: **보정요청**. 코드 브랜치 **머지 보류**, 리뷰 기록만 `main` 머지(D-007).

**잘 된 것**: AC#1(Java sink 3출처 = frozen zone·`@Gov(sink=true)`·registry, 그리고 `@Gov`(sink 없음)·`protected` 는 sink 아님 = 음성조건까지)
· AC#4(홉 1/2 경계가 정책값 · shadow → `shadow_hits`+`pass`, registry 재등록 시 enforcing 승격) · 분석실패 fail-closed(문법 깨진 `.java` → 양 게이트 `parse_error`)
· 중첩클래스/생성자 id 정합(`Outer.<init>`·`Outer.Inner.deep` 이 inventory·콜그래프·registry 3자 일치) · 결정론(md5 3회 동일) · 성능(실diff 1.4s)
· 픽스처 회귀 0(**143/144 → 151/152**) · mutation **PASS(255)** · §1 보수성 통과(`policies/`·`kit/`·`docs/` 무접촉, 무관 리팩터 0).
**rig 6종** 중 A·B·C·D·F 는 단독 FAIL = 신규 가드 load-bearing.

**🔴 R-1 (AC#6 미충족) — 람다 dispatch 가 익명클래스와 동일 구조인데 조용히 `pass`.**
`wire()` 한 줄만 다른 fresh 입력 A/B: `new Port(){...}` → `approval_required`(exit 2) / `() -> new Ledger().settle()` → **`pass`(exit 0)·`fail_closed` 없음·`coverage` 무표식**.
둘 다 런타임엔 `Flow.sink → port.run() → Ledger.settle` 로 실제 도달하고 바뀐 함수는 enforcing sink 1~2홉 안이다 ⇒ **누락 방향**,
AC#6 이 명문으로 금지한 **"조용한 `pass`"** 이자 MVP-3 공통 "놓침 = parity 위반".
픽스처의 `lambdaWire()` 줄은 **장식**임을 실증(**RIG-G**: 익명만 빼고 람다만 남기면 해당 케이스 **단독 FAIL** 하고 게이트가 `pass`).
인계기록의 "람다는 엣지 보존 확인" 은 **정의부 엣지**일 뿐 dispatch 도달성이 아니어서 **긍정 오인을 유도하는 서술** — AC#6 이 요구한 "명시" 아님.

**🔴 R-3 (fail-open · `main` 대비 회귀) — 라우팅 정책이 어댑터를 못 내면 3층이 통째로 꺼진다.**
`active_languages` 가 비면 콜그래프도 sink 도 만들지 않고 `pass`/exit 0. **정책 파일이 없으면** 예외 → fail-closed(정상)인데
**있는데 퇴화하면**(`{}` 또는 `extensions` 드리프트) **`fail_closed`·`coverage` 공히 빈 채 조용히 통과** — 최악의 비대칭.
그 상태에서도 `changed_functions` 는 그대로 출력된다 = **바뀐 걸 알면서** 도달성 분석을 건너뛰고 clean pass 를 선언한다.
**부분 드리프트가 더 위험**: `.py` 만 라우팅에서 빠지면 verdict 는 `approval_required`(java 발견) 그대로라 겉보기 정상인데 **Python 발견과 `py-reviewer` 라우팅만 소실** — 사람이 알아챌 방법이 없다.
**자기무력화 경로**: 킷 `run.sh` 는 `cd "$REPO"` 후 `--repo .` 로 부르는데 새 `--language-routing` 기본값이 **CWD 상대**라 **분석 대상 repo 안**을 가리킨다.
대상 repo 가 `policies/language-routing.yaml` 에 `adapters: {}` 를 심으면 정산 sink 1홉 상류 변경이 **`pass`**.
동일 repo·동일 인자로 **`main` 게이트는 `approval_required`+`money`(settlement-reviewer)** 를 낸다 ⇒ **명백한 회귀**.
AC#3 "분석실패 → fail-closed" 와 설계 "unsupported 는 coverage 정직 노출·조용한 통과 금지" 위반.

**🟠 R-2 — 다국어 repo 에서 거짓 `unresolved_registry_function` → `fail_closed` 상시 점등.**
함수 수집만 언어 게이팅하고 registry 검증은 전역이라, `.java` 만 바꾸면 Python sink 가·`.py` 만 바꾸면 Java sink 가 "해소 불가" 로 찍힌다(둘 다 바꾸면 사라짐 = 거짓 증명).
방향은 안전(과대)하나 **멀쩡한 registry 를 깨졌다고 감사출력에 적고**, MVP-3 표적인 다국어 repo 에서 **모든 단일언어 커밋이 상시 fail_closed** 라
진짜 분석실패를 알리는 마지막 채널의 신호가 죽는다 — R-1·R-3 같은 사고를 덮는다.

**§2B 적용**: 세 건 모두 비차단 판정 전 필수질문("거버넌스 목적에 직접 구멍을 내나?")에 **예** 다.
R-1·R-3 은 실제 sink 도달 변경을 `exit 0` 으로 통과시키고, R-2 는 fail-closed 채널을 무력화한다 ⇒ **비차단 금지 · 보정요청**.
이는 A-0044 에서 O-4 를 "TASK-037 이 소비하는 순간 실구멍" 이라며 AC#6 으로 고정한 판단의 **일관된 연장**이다.

**비차단 이월**: O-1 익명 fail-closed 가 repo 전역이라 무관 변경도 상시 `approval_required`(dogfood 에서도 점등) — R-1 을 **AC#6(a) 노선(익명·람다 본문을 인터페이스 구현체로 등록)** 으로 닫으면 동시 해소되므로 (a) 권장
· O-2 신규 parity 6케이스가 `group: parity` 밖이라 `TEST_CASE_GROUP=parity` 가 MVP-3 핵심기준을 하나도 안 돌린다(그룹이 `main`·브랜치 공히 9/9 불변)
· O-3 Java id 패키지 비한정(`a.pkg1.Flow`↔`a.pkg2.Flow` 붕괴) — 과대=안전이나 감사필드로 패키지 식별 불가 + Python(`app.flow.helper`) 대비 parity 비대칭
· O-4 map 경로 java 분기가 load-bearing 아님(RIG-E 무변화 — classify 경로가 단독 공급).

**정책 상태**: `language-routing.yaml` `java.layers.callgraph` **`stub` 유지** — TASK-037 이 통과해야 소비자가 생긴다.
승격은 D-076 계약대로 **통과 후 Claude 가**(킷 반영은 TASK-038 AC#3).

**TASKS.md 반영**: **TASK-038 AC#6 신설** — 킷 `run.sh` 가 `--language-routing "$POL/language-routing.yaml"` 을 명시 전달하고,
대상 repo 가 동명 파일을 심어도 무영향임을 진입점 케이스로 고정(R-3 §3.4 대응).

**환경 고지**: 유일 실패 `tree-sitter-smoke` 는 이 머신 tree-sitter 0.23.2(pin 0.26.0 은 Python 3.9 휠 부재) 환경건으로 **`main` 동일** — 브랜치 귀속 아님.
킷 selftest 도 `main`·브랜치 **동일하게 140/141 + 같은 사유** (킷 무접촉 확인).

**머지**: 코드 브랜치 **보류**. 리뷰 기록(`A-0045`·본 항목·`review-notes.md`·`TASKS.md`·handoff·summaries)만 `main` 머지 — 다음 세션·Codex 가 보도록(D-007).
상세 `collab/answers/A-0045.md`.

---

## D-090 — TASK-037 A-0045 보정 재제출 재리뷰 — **R-1·R-2·R-3 해소 · 신규 R-4·R-5 로 재보정요청** · 코드 머지 보류 (A-0046)

**대상**: `codex/2026-07-21-task037-java-indirect-impact` — 보정 커밋 `7f4859a`·`0cb241b`. `origin/main`=`d399435` 대비.
멱등성: `c670753`·`67c3422` 는 A-0045 에서 처리 완료 — 재처리하지 않음.
**판정**: **재보정요청**. 코드 브랜치 **머지 보류**, 리뷰 기록만 `main` 머지(D-007).

**✅ A-0045 지적 3건 전부 종결 — 재작업 불필요**
- **R-1(람다 dispatch)**: 권장했던 **(a) 노선**(익명·람다 본문을 함수형 인터페이스 구현체로 등록)으로 닫혔다. fresh ADV-1/ADV-1b 재현 결과 익명·람다 **양쪽 모두** 실 발견 1건(`path: [Flow.sink, Port.run, Ledger.settle]`·`hops 2`·`settlement-reviewer`) — 차선(b) 의 fail-closed 가 아니라 **진짜 탐지**다. **O-1(익명 fail-closed 전역 소음)도 동시 해소** 확인: 무관 변경 → 보정 전 `approval_required` → 보정 후 `pass`.
- **R-3(라우팅 fail-open)**: A-0045 §3.5 요구대로 **킷 배선이 아니라 게이트 레벨**에서 막았다(`kit/` 무접촉). 퇴화 `adapters: {}`·`extensions` 드리프트 공히 `pass`(0) → **`approval_required`(2)** + `errors`·`coverage`·`fail_closed` **3채널 동시 노출**. 부분 드리프트는 누락 파일 경로(`app/flow.py`)를 정확히 지목. **§3.4 자기무력화(`main` 회귀)도 폐쇄** — 판정 근거가 `routing["changed_files"]`(git name-status 산출, **정책 무의존**)라 정책이 자기 감시를 끌 수 없다.
- **R-2(거짓 registry 오류)**: 다국어 repo 단일언어 커밋에서 `errors` **빔**. **과잉억제 아님(음성검증)** — 실재하지 않는 registry 함수는 여전히 `unresolved_registry_function` 을 낸다.
- **O-2(parity 라벨)**: `TEST_CASE_GROUP=parity` **9/9 → 15/15**. MVP-3 최우선 합격기준이 실제로 돈다.

**🔴 R-4 (신규 · 보정이 만든 회귀 — AC#6 미충족)**: 보정이 `nested_in_deferred_body` 로 중첩 본문을 `collect_calls` 에서 제거했는데,
대체 처리기 `subtree_call_targets()` 에는 **`lambda_expression` 분기도 중첩 익명 처리도 없다**(깊이 1 전용).
결과 **익명-in-람다**에서 엣지가 `Flow.sink→Port.run→Inner.go` 로 **막다른 길**이 되고 `coverage` 는 **완전히 빔** ⇒ **보정 전 `approval_required`(exit 2) → 보정 후 `pass`(exit 0)**.
실제 런타임 도달 경로(`port.run()`→람다 본문→`in.go()`→익명 본문→`Ledger.settle`)를 **보정 전에는 잡던 것을 이제 놓친다**.
람다-in-람다도 `coverage` 1건 → **`[]`** 로 퇴화(정직성 회귀). **AC#6 이 만든 `anonymous_class`→fail-closed 가드가 자기 스킵 때문에 발동하지 못하는 구조**다.

**🔴 R-5 (신규 — A-0045 §2 (b) 요구의 반쪽)**: A-0045 는 "`kind: lambda_dispatch` 로 남기고 **익명과 같은 fail-closed 승격 경로에 편입**" 을 못박았는데,
보정은 **`kind` 만 만들고 승격을 배선하지 않았다**(승격 필터가 여전히 `kind == "anonymous_class"` 단일 비교).
⇒ dispatch 대상 타입을 못 정하는 두 **최빈 형태**가 조용한 `pass`: ① **람다 인자전달**(`set(() -> …)` = `executor.submit`/`forEach`/빌더 콜백) ② **`default` 메서드 보유 함수형 인터페이스**(`functional_method_targets` 의 `len(methods)==1` 이 `default`·`static` 까지 계수).
**수정 비용 1줄 실증**: 승격 필터를 `in {"anonymous_class", "lambda_dispatch"}` 로 바꾸면 두 형태가 `approval_required` 로 전환되고 정상 탐지는 유지, **스위트 157/157 불변**. 대규모 리팩터 아님.

**구조적 원인**: 보정이 dispatch 를 잇기 위해 **보수적 fallback(정의부 귀속 엣지)을 제거**했는데(그 자체는 정확도 개선 — 람다를 저장만 하고 호출 안 하는 repo 에서 과탐 1건 소멸 실증),
대체 처리가 **① 깊이 1 · ② 직접대입 · ③ 메서드 정확히 1개인 인터페이스** 만 커버한다. 그 밖은 과탐이 아니라 **누락**으로 떨어져 MVP-3 공통규칙 "**항상 과탐 쪽으로 반올림 · 과소탐 금지**" 와 반대 방향이다.
⇒ 방향(a 노선)은 옳다. **fallback 을 걷어낸 만큼 dispatch 미확정을 전부 fail-closed 로 회수**해야 등가가 성립한다.

**§2B 적용**: R-4·R-5 모두 필수질문("거버넌스 목적에 직접 구멍을 내나?")에 **예** — 실제 sink 도달 변경을 `exit 0` 으로 통과시키고, R-4 는 **보정 전보다 나쁘다** ⇒ **비차단 금지 · 재보정요청**.

**통과 확인(실증)**: 회귀 0 — dev `origin/main` **144/144** → 브랜치 **157/157**(신규 실패 0, adversarial 8→15 · parity 9→15) · mutation **PASS(265)** · 결정론 md5 3회 동일 · 실diff **0.53s**(`main` 0.85s — `extract-sinks` 가 항상 Java 를 파싱해도 폭주 없음) · dogfood `check-policy-change` **PASS**.
**rig-and-revert 9종 전부 대상 케이스만 단독 FAIL** — 특히 라우팅 fail-closed 의 `errors`/`coverage`/`fail_closed` **3채널이 각각 단독으로 load-bearing**(5a·5b·5c) ⇒ A-0041 G-1 이 요구한 **원소 단위** 기준 충족, 장식 없음.

**환경 고지 · A-0045 자기정정**: A-0045 가 환경건으로 보고한 `tree-sitter-smoke` 실패는 **소멸**했다 — 이 머신 tree-sitter 가 pin 값 **0.26.0**/`tree-sitter-java` **0.23.5** 로 맞춰져 `main`·브랜치 공히 실패 0. 이번 수치(144/144·157/157)에는 **환경 예외가 없다**.

**§1 보수적 개발 — 통과**: 보정이 건드린 파일 = 게이트 3 · `cases.yaml` · 픽스처 29 · handoff · summaries **뿐**.
**`kit/` 는 `origin/main` 과 diff 0 바이트**(TASK-038 스코프 정확 준수) · `policies/`·`docs/`·Claude 소유 **무접촉** · 무관 리팩터 0 · 커밋 형식 준수. A-0045 §6 이 지적한 커밋 문구 과장도 정정됨. **반려 사유는 순수 논리 결함이며 §1 위반이 아니다.**

**비차단 이월/신규**: **O-6(신규)** 메서드 레퍼런스 `::` 가 람다·익명과 같은 dispatch 모양인데 **완전 무표식**(보정 전·후 동일 = 선재이므로 반려 사유 아님 — R-4/R-5 와 **같은 자리에서** 함께 닫기 권장, 아니면 차기 J-태스크 AC 로 고정)
· **O-7(신규)** `java-indirect-anonymous-fail-closed` 케이스 이름이 바뀐 기대값(실 indirect impact)과 불일치 = 오도, 개명 권장
· **O-8(신규)** `functional_method_targets` 가 `default`/`static` 까지 계수 — 추상 메서드만 세면 ADV-6 이 fail-closed 가 아니라 **실 탐지**로 상승(정확도)
· **O-3·O-4(이월)** 미해소
· **O-5** 는 TASK-038 AC#6 으로 이미 신설됨. 킷 285행은 여전히 `--language-routing` 미전달이나 `LANGUAGE_ROUTING` 변수가 27·57행에 이미 있어 **1줄 배선**이며, **R-3 이 게이트 레벨에서 닫혔으므로 이제 이중방어**다.

**킷 노출 고지(운영)**: `kit/gates/` 의 3개 게이트는 **보정 전 스냅샷**(`language_routing_missing_adapter` 0건) ⇒ **배포 킷에는 R-1·R-3 구멍이 아직 살아 있다**. TASK-038 sync 까지가 노출 구간 — 스코프상 정상이나 명시해 둔다.

**브랜치 동기화(반복 지적)**: 브랜치가 `origin/main` 에 뒤처져 `d399435`·`211b627`(A-0045 기록)이 없다. **재제출 전 `origin/main` 머지**를 관행으로 고정할 것(collab-protocol §5.1).

**정책**: `language-routing.yaml` `java.layers.callgraph` **`stub` 유지** — 소비자(TASK-037)가 아직 미통과. 승격은 D-076 계약대로 **통과 후 Claude 가**(킷 반영은 TASK-038 AC#3).

**머지**: 코드 브랜치 **보류**. 리뷰 기록(`A-0046`·본 항목·`review-notes.md`·handoff·summaries)만 `main` 머지 — 다음 세션·Codex 가 보도록(D-007).
민감(정산·인증/인가·암호화·DB migration·infra) 변경 없음 ⇒ 형 승인 요청(H-XXXX) 불필요.
상세 `collab/answers/A-0046.md`.

---

## D-091 — TASK-037 A-0046 재보정 재제출 재리뷰 — **R-4·R-5 해소 · 리뷰 통과 · `main` 머지** (A-0047) — 2026-07-21

**대상**: `codex/2026-07-21-task037-java-indirect-impact` head `ae9aaa0`, 재리뷰 커밋 **`66c5133`·`ae9aaa0`** (멱등성: `c670753`·`67c3422`·`7f4859a`·`0cb241b` 재처리 안 함). 기준선 `origin/main`=`607572b`, 보정 전 대조군 `0cb241b`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**.

**판정**: **리뷰 통과 · 비민감 ⇒ Claude 가 `main` 머지**(D-007 구현자≠머지자). 머지 커밋 `3527edb`.

**🔴 R-4·R-5 해소 실증(픽스처 밖 fresh 입력 9형태 · 보정 전↔후 대조)**: 7형태가 **`pass`(0) → `approval_required`(2)** 로 전환 —
익명-in-람다-in-람다(깊이 3) · 람다 인자전달(`runner.submit(() -> …)`) · `default`+`static` 보유 함수형 인터페이스 · **익명-in-익명** · **익명-in-익명-in-익명** · **익명 본문 속 람다**(뒤 3형태는 A-0046 이 지명조차 안 한 것 = 덤) · 무관변경 소음 1형태.
**무회귀 대조군 2형태 불변**: 직접대입 람다 실탐지(`path: [Gateway.entry, Task.exec, Vault.transfer]`·hops 2)와 **Python 골든패스**(`app.flow.helper`·hops 1)는 보정 전과 **동일**. A-0046 §3.1 이 "보정 전보다 나쁜 유일 지점" 이라 못박은 exit 2→0 회귀는 **소멸**했고 상설 픽스처로 고정됐다.

**통과 확인(무발견 ≠ 통과)**: 스위트 157→**161/161**(adversarial 15→19 · parity 15/15 · default 121 불변) · mutation **PASS(273)**(+8 = 신규 4케이스 기대값 전부 뮤테이션 민감) · 결정론 md5 3회 동일 · dogfood `check-policy-change` **PASS**(`policy_loosening`·`enforcement_bypass` 공히 빔) · verdict 조립 재확인(`approval_required(2)`/`pass(0)` 2갈래뿐 = **2·3층 자동차단 금지 불변식 유지**) · Codex 신고 수치(161/161·273) **독립 재현 일치**(과장 없음).
**rig-and-revert(원소 단위 · A-0041 G-1)**: **E1**(승격 필터) 158/161 = 3케이스만 · **E4**(subtree 람다 기록) 160/161 단독 · **E5**(subtree 익명 기록) 160/161 단독 ⇒ **load-bearing**. **E2·E3**(중첩본문 기록)는 **161/161 무변화 = 픽스처 공백**이나, 구조상 중첩이 성립하려면 바깥 deferred body 가 이미 E4/E5 로 승격되므로 **verdict 를 뒤집을 수 없는 정직성(coverage) 전용 원소** — 결함이 아니라 회귀 픽스처 공백으로 분류(O-11).

**§1 보수적 개발 — 통과**: 델타가 건드린 파일 = 게이트 2(4줄·12줄) · `cases.yaml` 4케이스 · 신규 픽스처 4세트 12파일 · handoff · summaries **뿐**. **`kit/` 는 `main` 과 diff 0 바이트**(TASK-038 스코프 준수 ⇒ 킷 심층리뷰는 **변경분 부재로 해당 없음**) · `policies/`·`docs/`·Claude 소유 무접촉(merge-base 3-dot 확인) · 무관 리팩터 0 · 커밋 형식·문구 정확. scope-creep·over-reach 없음.

**🔴 신규 관찰 → TASK-039 신설(비차단 아님·명시 가드)**: §2B 필수질문에 **예**인 2건을 규정대로 **차기 AC 로 고정**한다(반려하지 않는 이유 = 이번 델타의 회귀가 아니고 `main`(Java L3 부재) 대비 후퇴도 아니며, A-0045·A-0046 두 번의 리뷰에서 내가 지명하지 못한 **선재 결함**이라 뒤늦은 골포스트 이동을 피함).
- **O-9 메서드 본문 *밖* dispatch 무표식**: `collect_calls` 가 `method_declaration`·`constructor_declaration` 본문만 순회 ⇒ **필드 이니셜라이저·static 블록**의 호출은 엣지도 coverage 도 없다. `Task task = () -> new Vault().transfer();` / 필드 초기화 **익명**(= AC#6 이 지명한 바로 그 모양) / `static { … }` 3형태 전부 **`pass`·coverage 빔**, 같은 코드를 **생성자**에 두면 정상 탐지 = 원인이 순회 범위임을 증명.
- **O-10 승격이 repo 전역·무조건 ⇒ 과탐 소음**: 승격 필터가 `coverage.unevaluated` 전량을 보고 **sink 존재 여부조차 안 본다**. **등록 sink 0개** repo 에서 `rows.forEach(r -> log(r))` 한 줄 때문에 무관 변경이 `approval_required`. 실 Java repo 면 사실상 상시 승인요구 = 경보 피로. **자기정정**: 이 소음은 A-0046 §4.2 에서 **내가 1줄 수정을 지시하며 "회귀 0" 만 확인하고 소음 영향을 검증하지 않은 결과** — 지시 책임은 리뷰어(Claude)이고 Codex 의 §1 위반이 아니다. **내가 짠다면**: sink 전방폐쇄 안에 **본문 없는 추상/인터페이스 메서드(막다른 길)** 가 있을 때만 승격 — fresh 세트에서 실구멍 6형태는 승격 유지, 소음 2형태만 `pass` 로 정확히 갈린다.
- **O-6(이월)** 메서드 레퍼런스 `::` 여전히 무표식 · **O-11** E2/E3 픽스처 공백 · **O-8** `default`/`static` 계수 · **O-7** 케이스 개명 · **O-3·O-4** 이월.

**정책 조치(Claude 소유 · D-076)**: `policies/language-routing.yaml` `java.layers.callgraph` **`stub` → `partial`**. `supported` 는 O-9·O-6 때문에 **과대주장**이며 정책 자신의 "under-claim, never over-claim"·D-074 O-5/D-075(false card 금지) 에 어긋난다. `partial` 은 어댑터 활성화(확장자 기준)에 무관해 Java 간접영향 판정은 정상 작동하고, 카드에는 `layers not available: callgraph` 로 한계가 계속 노출된다(기존 3케이스 기대값과 일치 = 무회귀, 161/161 재확인). legacy `status: stub` 은 보수적 floor 로 유지. `supported` 승격은 **TASK-039 후 재검토**.

**킷**: 이번 델타 무접촉. `kit/gates/` 는 아직 Java L3 **부재**(구멍이 아니라 미탑재) — TASK-038 sync 시 **TASK-039 를 먼저** 처리해 구멍째 스냅샷되지 않게 할 것(TASK-038 AC#3·의존 절에 명시).

**브랜치 동기화(3회째)**: 이번에도 브랜치가 `origin/main` 에 뒤처진 채 재제출 — 재제출 전 `origin/main` 머지를 관행으로(collab-protocol §5.1).

민감(정산·인증/인가·암호화·DB migration·infra) 변경 없음 ⇒ 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0047.md`.

---

## D-092 — TASK-039 리뷰 — **보정요청** (Java L3 deferred dispatch: 승격 정밀화가 JDK 인터페이스에서 과소탐) (A-0048) — 2026-07-22

**대상**: `codex/2026-07-21-task039-java-l3-coverage` head `b2d7cd8`, 리뷰 커밋 **`e54a30f`(구현)·`b2d7cd8`(인계)**. 기준선 `origin/main`=`b56c62a`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**.
**판정**: **보정요청**. 코드 브랜치 **머지 보류**, 리뷰 기록만 `main` 머지(D-007).

**✅ 닫힌 것 (재작업 불필요)**: **AC#2** `::` 폐쇄(`task = vault::transfer` → 실 엣지 `Flow.sink→Task.exec→Vault.transfer`) · **AC#4** 중첩 기록 픽스처 공백 — **A-0047 의 E2·E3 가 이제 단독 FAIL**(rig 167/169·168/169) ⇒ **O-11 종결** · **AC#5** 개명 · **O-8** 추상 메서드만 계수(rig E-G 단독 FAIL) · **AC#6** 무회귀. **AC#1 의 필드·static·instance 초기화 3형태**도 닫힘(rig E-A·E-B).

**🔴 R-1 (차단 · 이 델타가 만든 회귀 · AC#3 불변식 위반)**: 승격 판별식이 "막다른 길" 을 **`nodes[].bodyless`(= repo 안에 선언된 메서드)** 로만 정의한다. dispatch 대상이 **JDK/외부 함수형 인터페이스**면 노드가 없어 `sink_dead_ends` 가 비고 ⇒ **`java_deferred` 가 아무리 많아도 fail-closed 가 발동하지 않는다**. 정밀화가 "무관한 dispatch 를 거른다" 가 아니라 **"대상이 repo 밖이면 판정을 포기한다"** 로 동작 ⇒ 실 Java repo 에선 L3 fail-closed 대부분이 꺼진다.
**fresh 입력(픽스처 밖·별도 repo) `main`↔브랜치 대조 — 3형태가 `approval_required`(2) → `pass`(0)**: ① `schedule(() -> new Vault().transfer())` + `void schedule(Runnable r){ r.run(); }` ② 같은 자리 **익명 `new Runnable(){…}`** ③ `pool.submit(() -> …)`(`ExecutorService`, sink 전방폐쇄 안 helper). 세 형태 모두 **coverage 엔 정직히 찍히고 판정만 조용히 통과**. (+ `rows.forEach(v::transfer)` 는 회귀는 아니나 같은 원인의 잔존 구멍.)
**대조군 불변**: repo 선언 인터페이스 직접대입 람다 실탐지(`[Flow.sink, Task.exec, Vault.transfer]`)·**Python 골든패스**(`app.flow.sink→app.flow.helper`) 양쪽 동일 ⇒ 정상 탐지 무손상 = 과잉 반려 아님.
**§2B 필수질문에 예**: 실 sink 도달 변경이 `exit 0` · **`main` 보다 나쁨** · AC#3 이 🔴 불변식으로 명문화한 "과소탐 금지" 와 MVP-3 공통("과탐 반올림·과소탐 금지") 정면 위반 ⇒ **비차단 금지**.

**🔴 자기정정 (근본원인은 리뷰어 지시)**: 이 판별식은 **A-0047 §4.2 에서 내가 못박은 문구**("sink 전방폐쇄 안에 본문 없는 추상/인터페이스 메서드가 있을 때만 승격")이고, 내가 검증한 fresh 세트를 **repo 선언 인터페이스로만** 구성한 탓에 외부 인터페이스 축이 통째로 빠졌다. **Codex 는 지시를 정확히 구현했다 — §1 위반도 구현 품질 문제도 아니다.** A-0047 이 O-10 에서 한 자기정정과 같은 유형의 실수를 **연속 2회** 냈다 ⇒ 앞으로 판별식을 지시할 때는 **"repo 밖 심볼" 축을 fresh 세트에 필수 포함**한다.

**수정 실증(8줄 · 스크래치 사본)**: 막다른 길 정의에 **`kind: unresolved` coverage 를 가진 함수**를 더하고(게이트가 이미 기록 중), 전방폐쇄에 **sink 자신**을 포함 ⇒ **X1·X3·X5 전부 `approval_required` 복구 + `::` 잔존 구멍까지 폐쇄**, **대조군 불변**, **스위트 169/169 그대로**(AC#3 이 요구한 소음 `pass` 2케이스 유지). ⇒ **경보 피로 제거와 과소탐 금지는 양립**하며 대규모 리팩터가 아니다.

**🔴 R-2 (차단 · AC#1 미완)**: `collect_initializer_deferred` 가 타입 `body` **직속 자식**만 보므로 **enum(`enum_body_declarations` 아래)·인터페이스 상수(`constant_declaration`)·익명클래스 본문 필드**가 여전히 **엣지도 coverage 도 없이 조용한 `pass`**. **원인 격리 대조군**: `enum Reg { A; static Task task = () -> new Vault().transfer(); }` = **`pass`·coverage 빔** vs **바이트 단위 동일 코드의 `class Reg` 판** = `approval_required` ⇒ 컨테이너 종류만으로 판정이 갈린다 = AC#1 이 지목한 **동일 결함의 미완**(회귀는 아님 — `main` 도 `pass`). 익명 본문 람다는 `subtree_call_targets` 미해소 분기에 `lambda_expression` 갈래가 없는 것이 원인.

**통과 확인(무발견 ≠ 통과 · 전부 독립 재현)**: 스위트 **169/169**(adversarial 25/25·default 121/121·metamorphic 3/3·negative 5/5·parity 15/15) — **Codex 신고와 정확히 일치, 과장 없음** · mutation **PASS(289)** 일치 · 결정론 md5 3회(fresh 3종) · **모든 입력의 exit 가 0/2 뿐**(3층 자동차단 0건 = 불변식 유지) · Python 골든패스 불변.
**rig-and-revert 원소 단위(A-0041 G-1)**: load-bearing 8종(E-A 167·E-B 168·E-E 168·E-G 168·E-H 167·E-I 168·E-J 167·E-K 157) · 원복 후 169/169 재확인. **미고정 3종**(E-C instance 블록·E-D 초기화 `::`·E-F deferred body 안 `::`) → O-12.
**환경 자기정정**: 첫 실행의 124/169 는 **내가 감싼 `timeout`(Homebrew x86_64) 이 프로세스 트리를 Rosetta 로 내려 arm64 `tree_sitter` `.so` 를 깨뜨린 계측 아티팩트** — `main` 에서도 동일 재현. `timeout` 제거 후 169/169. **이 건으로 감점하지 않는다.**

**§1 보수적 개발 — 통과**: 델타 = 게이트 2 · `cases.yaml` · 픽스처 8세트 · handoff · summaries **뿐**. **`kit/`·`policies/`·`docs/`·Claude 소유 = 3-dot diff 0 바이트**(⇒ **킷 심층리뷰는 변경분 부재로 해당 없음**) · 커밋 §3 형식·문구 정확 · `git diff --check` clean. **브랜치가 최신 `main` 기반 — 3회 연속 지적한 미동기화 재제출 해소 ✅**. scope-creep·over-reach 없음(잔티 O-16 뿐).

**비차단 관찰**: **O-12** rig 미고정 3원소 — O-11 과 달리 **E-C 는 verdict 를 실제로 뒤집는다**(fresh 인스턴스 초기화 블록 `pass`→`approval_required`) ⇒ 픽스처만 추가 · **O-13** `nodes[].bodyless` 는 신규 출력 스키마인데 직접 단언 케이스 0(rig E-K 로 간접 고정) — **TASK-038 킷 sync 시 노드 스키마 동반 필수** · **O-14** 승격이 여전히 repo 전역 all-or-nothing(결제 sink 의 막다른 길 때문에 무관한 UI 콜백까지 승인요구) · **O-15** `Vault::new` 는 해소 대신 fail-closed(안전한 방향 = 결함 아님) · **O-16(§1 잔티)** `direct_field_bindings` → 모듈레벨 승격이 호출부 1곳·신규 소비자 0 = 불필요한 순수 리팩터 diff 노이즈(감점만) · **O-6 부분 해소**(외부 인터페이스 `::` 는 R-1 과 함께 닫힘) · **O-3·O-4 이월** · **O-7·O-8·O-11 종결**.

**보정 지시(TASKS.md TASK-039 AC#7·#8·#9 로 고정)**: **AC#7** 막다른 길 정의를 `bodyless` **또는** `kind: unresolved` 로 확장 + 전방폐쇄에 sink 자신 포함 · JDK 3형태 + `::` 픽스처 신설 · **소음 `pass` 2케이스와 기존 픽스처 전량 유지를 회귀로 고정** · 음성검증. **AC#8** enum 본문·인터페이스 상수(+익명 본문 람다) 순회 확장 · **enum 판/class 판 쌍 픽스처**로 컨테이너별 비대칭 재발 즉시 FAIL. **AC#9** E-C·E-D·E-F 픽스처 고정(각각 단독 FAIL).

**정책**: `java.layers.callgraph` **`partial` 유지** — R-1·R-2 잔존이라 `supported` 승격은 AC#7~#9 통과 후(D-076).
**킷**: 이번 델타 무접촉. **TASK-038 sync 는 계속 대기** — 지금 sync 하면 **R-1 회귀를 배포 킷에 그대로 싣는다**(현행 킷은 Java L3 부재 = 구멍이 아니라 미탑재).
민감(정산·인증/인가·암호화·DB migration·infra) 변경 없음 ⇒ 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0048.md`.

---

## D-093 — TASK-039 A-0048 보정 재제출 재리뷰 — **리뷰 통과 · `main` 머지** (A-0049) — 2026-07-22

**대상**: `codex/2026-07-21-task039-java-l3-coverage` head `1a3f0d0`, **보정 커밋 `ed2d221`(구현)·`1a3f0d0`(인계)**. 기준선 `origin/main`=`662d972`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**(나머지 전량 머지완료), handoff 최상단이 `Codex → Claude` ⇒ 리뷰 차례.
**멱등성**: `e54a30f`·`b2d7cd8` 는 A-0048 처리 완료 — **보정 델타만 재리뷰**(머지 판단은 브랜치 전체 기준).
**판정**: ✅ **통과 · 머지**. **TASK-039 종결 — 재제출 불필요.**

**🔴 R-1 종결 (A-0048 의 차단 사유)**: 막다른 길 정의를 `nodes[].bodyless` **∪ `kind: unresolved` coverage 보유 함수** 로 확장 + 전방폐쇄에 **sink 자신 포함**. **픽스처 밖 fresh 입력 4형태가 `pass`(0) → `approval_required`(2) 복구**: ① `schedule(() -> new Vault().transfer())`+`void schedule(Runnable r){r.run();}` ② 같은 자리 익명 `new Runnable(){…}` ③ `pool.submit(() -> …)`(`ExecutorService`) ④ `rows.forEach(v::transfer)`(A-0048 이 남긴 `::` 잔존 구멍까지 폐쇄). `fail_closed` detail 에 `dead_ends=<함수>` 가 찍혀 **원인이 카드에 드러난다**(감사카드 정직성↑).
**왜 이제 누락이 없나 (구조적 논증)**: 지연 dispatch 가 실제 호출되려면 그 지점은 (a) repo 선언 인터페이스 추상 메서드 = `bodyless`, (b) 외부(JDK) 타입 호출 = `unresolved`, (c) 외부 프레임워크 콜백 등록 = (b) 중 하나다 — **셋 다 확장 판별식에 포함**. 이를 깨려 만든 fresh 8형태에서 반례 없음.
**대조군 불변**: repo 인터페이스 직접대입 람다 실탐지(`[Flow.sink, Task.exec, Vault.transfer]`·hops 2·`settlement-reviewer`) 3자(`main`·`e54a30f`·브랜치) 동일 · **Python 골든패스 16케이스 목록 `main` 과 문자 단위 동일** ⇒ 승격 확대가 정상 탐지를 삼키지 않음 = 과잉 반려 아님.

**🔴 R-2 종결**: `scan_initializer_members` 가 `enum_body_declarations`·`class_body_declarations` 로 재귀하고 `constant_declaration` 을 처리, 익명 클래스 본문 필드는 `collect_calls` 의 신규 `elif` 로 회수. **A-0048 의 원인격리 대조군 재현 — enum 판과 class 판의 coverage 원소가 이제 문자열 단위로 동일**(`Reg.<clinit>|lambda_dispatch|lambda`), 인터페이스 상수·익명 본문 필드도 기록. 쌍 픽스처로 비대칭 재발 시 즉시 FAIL. `record`·`static` 중첩 클래스·**if 블록 안 local class**(고정 적대세트 "조건부·중첩 정의")도 정상 기록.

**AC#9 부분 (→ O-17)**: E-C(instance 블록·RIG-7 단독 FAIL)·E-D(초기화 `::`·RIG-8 단독 FAIL)는 고정. **E-F 는 미고정** — 신규 픽스처가 `::` **해소** 경로(`coverage_unevaluated: []`)를 단언해 해소 분기만 잡고(RIG-10 단독 FAIL), **미해소 fallback 은 제거해도 180/180 무변화**(RIG-9). 이 원소는 **verdict 를 실제로 뒤집는다**(fresh: 해소 가능 람다 본문 안 `Ext::run` → `approval_required` ↔ 분기 제거 시 `pass`) ⇒ A-0041 G-1 미충족이나 **가드 자체는 실재·작동**하므로 회귀보호 공백에 그침 = 비차단, 차기 AC.

**🟠 O-14 실측 (AC#3 실효범위 축소 · 비차단)**: `kind: unresolved` 는 **JDK 호출 전부**에 붙으므로(`extract-java-callgraph.py:525`) 판별식이 사실상 "sink 전방폐쇄가 외부 호출을 하나라도 한다" 로 완화됐다. **fresh 실증(변경 대상은 sink 와 무관)**: **N4**(폐쇄에 `rows.size()` 1개) `main` 승인요구 / `e54a30f` **`pass`** / 브랜치 **승인요구** ↔ **N5**(그 JDK 호출만 제거) 브랜치 **`pass`**. ⇒ 소음 억제가 살아남는 조건이 "폐쇄 전체가 외부 호출 0회" 로 좁아졌다.
**비차단 근거**: ① 방향이 **과탐**이라 MVP-3 "과탐 반올림·과소탐 금지" 와 동방향 — §2B 필수질문에 **아니오** ② **`main` 보다 나쁘지 않음**(main 은 무조건 전역 승격 ⇒ N4·N5 둘 다 승인요구; 브랜치는 N5 를 정확히 `pass`) ⇒ 탐지·소음 **두 축 모두 main 이상** ③ AC#3 이 명문화한 실증 케이스(sink 0개·무관 sink)는 여전히 `pass` = AC 문언 충족.
**🔴 자기정정 (3회 연속)**: 이 확장은 **A-0048 §"방향" 에서 내가 8줄 프로토타입까지 붙여 못박은 지시**이고, 그때 나는 **소음 축을 검증하지 않았다**(A-0046→A-0047 O-10, A-0047→A-0048 R-1 에 이어 같은 유형 3회째). **Codex 는 지시를 정확히 구현했다 — §1 위반도 구현 품질 문제도 아니다.** ⇒ 앞으로 판별식을 지시할 땐 **탐지축과 소음축을 같은 fresh 세트로 동시에** 실측한 뒤에만 문구를 확정한다.
**내가 짠다면(차기 AC · 실패모드 동봉)**: 지금은 **막다른 길 쪽만** sink 관련성을 보고 `java_deferred` 는 여전히 repo 전역이다. 스크래치 프로토타입("deferred 의 `caller` 가 폐쇄 안일 때만 승격")은 **N4 를 `pass` 로 고치고 R-1·AC#8·대조군 전부 유지**했으나 **`java-indirect-lambda-argument-fail-closed` 단독 FAIL**(179/180) — 람다 **생성 지점**(`Flow.wire`)이 폐쇄 밖이기 때문. ⇒ **caller 축은 틀렸고 dispatch 대상 축이 옳다**: coverage 항목에 dispatch 대상(예: `Port.run`)을 기록해 **그 대상이 `sink_dead_ends` 에 있을 때만** 승격. **이 방향은 아직 미실증이므로 Codex 는 착수 전 7축 fresh 세트로 먼저 검증할 것**(A-0049 §3에 목록).

**통과 확인(무발견 ≠ 통과 · 전부 독립 재현)**: `main` **161/161** → 브랜치 **180/180**, 신규 실패 0(adversarial 19→**36** · negative-corpus 3→**5** · default 121·metamorphic 3·parity 15 불변) — **Codex 신고와 정확히 일치, 과장 없음** · mutation **PASS(311)** 일치 · 결정론 md5 3회 · **모든 입력 exit 0/2 뿐**(3층 자동차단 0 = §4 불변식 유지) · `py_compile`·`git diff --check` PASS · **`cases.yaml` 은 순수 추가**(삭제·수정 0줄, 기존 verdict 변경 0건, 신규 11케이스 전량 `adversarial`·`approval_required`) = 기대값 약화 없음.
**rig-and-revert 원소 단위(A-0041 G-1)**: RIG-1(unresolved 확장) 174/180·6건 · RIG-2(sink 자신) 177/180·3건 · RIG-3(enum 재귀)·RIG-4(constant)·RIG-5(익명 본문 필드)·RIG-7(instance 블록)·RIG-8(초기화 `::`)·RIG-10(해소 `::`) **각각 단독 FAIL** · RIG-6(`has_static_modifier`) 2건(쌍 픽스처 작동) · **RIG-9 만 무변화 → O-17**. 원복 후 180/180 재확인 ⇒ 신규 가드 9/10 load-bearing, 장식 없음.

**§1 보수적 개발 — 통과**: Codex 커밋 4개가 건드린 것은 게이트 2(12줄·94줄)·`cases.yaml`·픽스처 11세트·handoff·summaries **뿐**. **`kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·Claude 소유 전부 무접촉** ⇒ **킷 심층리뷰(형 지시 ★★)는 변경분 부재로 해당 없음**. 무관 리팩터·포맷·이름변경 0, scope-creep·over-reach 없음. `collect_calls` 의 `continue`→`if/elif` 재구성은 기존 갈래 동작 보존한 순수 확장(RIG-5 로 확인).
**브랜치 동기화**: 브랜치가 `main` 보다 2커밋 뒤처져 재제출(4회째) — `handoff-log.md`·`summaries/2026-07-22.md` add/add 충돌을 Claude 가 양측 보존으로 해소. collab-protocol §5.1(재제출 전 `origin/main` 머지) 계속 관행화 요망.

**비차단 관찰 → 차기 AC (TASK-040 신설)**: **O-17**(E-F 미해소 `::` fallback 미고정 · verdict-bearing 실증) · **O-18**(`has_static_modifier` 가 `modifiers` 노드 전체 텍스트를 `"static"` 과 완전일치 비교 ⇒ **`static final`·`private static`·어노테이션 동반**이면 caller 가 `<clinit>`→`<init>` 오표기. **판정 무영향**(초기화 레코드는 `java_bodyless` 에 안 들어가고 합성 id 는 그래프 노드도 아님) = 조용한 `pass` 없음, 그러나 인계기록의 "static field/constant caller를 `<clinit>`로 표기했다" 는 **상수 표준형 `static final` 에서 사실이 아니고** 감사카드가 클래스 로드 시점을 인스턴스 생성 시점으로 오도. 수정 1줄) · **O-19**(`enum Reg { A { … } }` 상수 본문 coverage 무표식 — 구조적 논증상 verdict 누락은 재현 안 됨, 정직성 결손) · **O-14**(위) · **O-13 이월**(`nodes[].bodyless` 직접 단언 0 — TASK-038 킷 sync 시 노드 스키마 동반 필수) · **O-3·O-4·O-15·O-16 이월**.
**종결**: O-6 · O-9 · O-10(부분 — 잔여는 O-14) · O-11 · O-12 의 E-C·E-D.

**정책**: `java.layers.callgraph` **`partial` 유지**. 승격 근거는 늘었으나(초기화·`::`·JDK 인터페이스 전부 폐쇄) 정책 자신의 **"under-claim, never over-claim"**(D-074 O-5·D-075) 기준에서 `supported` 는 아직 과대주장 — **O-19**(정직성 결손)·**O-14**(정밀도)·**O-3**(id 패키지 비한정) 잔존. **승격 조건 명문화: TASK-040 AC#1(O-14) + O-19 폐쇄 후 재검토**(D-076).
**킷**: A-0048 의 sync 차단 사유(R-1 회귀)는 **해소** ⇒ TASK-038 착수 가능. 단 **TASK-040 AC#1 을 먼저 권고** — 현 상태로 스냅샷하면 실 Java repo 의 거의 모든 PR 이 `approval_required` 라 **경보 피로로 3층이 무력화**(AC#3 이 지목한 바로 그 실패모드). 순서를 바꾼다면 킷 README·`manifest.yaml` 에 **이 소음 특성을 명시**할 것.

**머지**: 변경은 하네스 게이트 로직 + 테스트뿐 — 정산·인증/인가·암호화·DB migration·infra **해당 없음**(CLAUDE.md §3 🔴🟠 아님, 선례 D-088·D-091) ⇒ **비민감**. 구현 Codex ≠ 머지 Claude ⇒ 자기머지 아님. **Claude 가 `main` 머지**, 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0049.md`.

---

## D-094 — TASK-040 리뷰 — **보정요청** (Java L3 정밀화가 지연 dispatch 등록지점 기준으로 과소탐) (A-0050) — 2026-07-22

**대상**: `codex/2026-07-22-task040-java-l3-precision` head `ea0191c`, 구현 커밋 `4573b51`. 기준선 `origin/main`=`265ba18`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**, handoff 최상단이 `Codex → Claude` ⇒ 리뷰 차례.
**판정**: 🔴 **보정요청 · 코드 브랜치 머지 보류.** **새 태스크 아님 — TASK-040 의 보정 커밋만 재제출.** 멱등성: `4573b51`·`ea0191c` **처리 완료 — 재리뷰 없음.**

**🔴 R-1 (차단 · 이 델타가 만든 과소탐 회귀 · `main` 보다 나쁨)**: `sink_relevant_deferred_records` 가 `dispatch_targets` 가 빌 때 **`caller ∈ sink_reachable`** 로 판정한다. 그런데 `collect_calls` 의 lambda `else` 갈래는 **`dispatch_targets` 가 항상 `()`** 이므로(`if dispatch_targets:` 의 else), **함수형 인터페이스가 repo 밖(JDK·외부)이면 판정이 통째로 `caller` 축**으로 넘어간다 — **A-0049 §3 이 "틀렸다" 고 명시 배제한 그 축**이다. **픽스처 밖 fresh 6형태가 `approval_required`(2) → `pass`(0)** (전부 별도 임시 repo · sink `Flow.sink` hops 4 · 변경 = `Vault.transfer` 본문): **F1** `Runnable task;`+`wire(){task=()->new Vault().transfer();}`+`sink(){task.run();}` · **F2** 익명 `new Runnable(){…}` · **F3** `pool.submit(() -> …)` · **F4** `task = vault::transfer` · **F7** `static { task = () -> …; }` · **F8** `static Runnable task = () -> …;`. **대조군 F5**(등록 지점이 sink 함수 자신 안) 는 `approval_required` 유지 ⇒ 탐지가 통째로 죽은 건 아니나, **실 Java 표준형인 "`wire()`/`init()` 가 등록하고 다른 함수가 호출" 이 전부 구멍**이다. **F7·F8 은 구조적 100% 드롭** — `<clinit>`·`<init>` 은 합성 id 라 그래프 노드가 아니어서 `sink_reachable` 에 **절대** 들어오지 않는다(A-0049 §3 검증축 ⑤). §2B 필수질문 **예**(과소탐 · `main` 보다 나쁨 · MVP-3 "과탐 반올림·과소탐 금지" 정면 위반) ⇒ **비차단 금지.**
**보정 방향은 실증됨**: fallback 을 `if not dispatch_targets and sink_dead_ends:` 로 교체해 브랜치 워크트리에 직접 적용 → **F1~F4·F7·F8 전부 복구 · F5 불변 · 스위트 183/184 로 유일한 FAIL 이 N4** · TASK-039 신규 11케이스 전량 `approval_required` 유지 · 소음 `pass` 2케이스 유지 · Python 골든패스 불변(원복 후 184/184 재확인).

**🔴 R-2 (차단 · AC#1 핵심 축의 회귀보호 0)**: **RIG-F** — `dispatch_targets.intersection(sink_dead_ends)` 를 `dispatch_targets and sink_dead_ends`(교집합 무시)로 바꿔도 **184/184 무변화**. AC#1 이 요구한 정밀화("대상이 `sink_dead_ends` 에 있을 때만 승격")가 **한 건도 단언되지 않는다** — N4 를 `pass` 로 만드는 것은 전적으로 R-1 의 잘못된 `caller` 축이고 **옳은 축은 장식 상태**다. 축 자체는 작동함을 fresh 로 확인(**F6**: `interface Other` 로 dispatch 대상을 sink 막다른 길과 분리 → 브랜치 `pass` / `main` `approval_required`) ⇒ **F6 형태 픽스처 + 음성검증이 없다** = A-0041 G-1 미충족.

**🔴 O-20 (신규 · AC#3 이 만든 반대편 오탐)**: `has_static_modifier` 가 `node.children` **전체**(타입·declarator 포함)를 토큰화해 `"static"` 을 찾는다 ⇒ **초기화식 텍스트에 `static` 토큰이 있으면 instance 필드가 `<clinit>` 로 오표기**. fresh 실증: `Task task = () -> log("static");` → `main` `Flow.<init>` ✅ / 브랜치 `Flow.<clinit>` ❌. 원 결함(`static final`·`private static`·어노테이션)은 닫혔으나(RIG-A 단독 FAIL) **AC#3 이 고치려던 것과 동종·동급의 오표기를 새로 만들었다.** 판정 무영향이라 차단은 아니나 **이번 보정에서 함께 닫는다**(`child.type == "modifiers"` 한정 + 토큰 분해).

**✅ 통과한 AC**: **AC#2(O-17)** — `subtree_call_targets` 미해소 `::` fallback 이 `java-indirect-deferred-body-method-reference-unresolved` 로 고정, **RIG-C 단독 FAIL** ⇒ **A-0041 G-1 이 요구한 마지막 원소 종결**. **AC#4(O-19)** — enum 상수 본문 coverage 표식, **RIG-B 단독 FAIL**. **AC#5** 무회귀. 부수 강화 2건도 load-bearing 확인: `invocation_parameter_type`(RIG-D), `class_direct_field_bindings` 의 `constant_declaration` 확장(RIG-E).

**🔴 자기정정 (4회 연속 — 지시 결함)**: **AC#1 의 "N4 를 `pass` 단언 케이스로 신설" 불변식이 근본원인이다.** N4 의 sink 막다른 길은 `rows.size()`(외부 호출)이고 그것이 콜백을 되부를 수 있는지는 정적으로 알 수 없다 ⇒ **대상 불명 지연 콜백은 보수 판정이 유일하게 건전한 답**이다. 게다가 N4 픽스처는 변경 함수에 지연 람다 본문이 호출하는 `Flow.log` 를 포함해 대안 축으로도 `pass` 가 안 나온다. ⇒ **AC#1 은 "caller 축 금지 + N4 pass" 라는 서로 모순된 두 요구를 동시에 걸었고, 그 둘을 모두 만족시키는 유일한 형태가 지금 코드다. Codex 는 지시를 정확히 구현했다 — §1 위반도 구현 품질 문제도 아니다.** A-0046→A-0047(O-10) · A-0047→A-0048(R-1) · A-0048→A-0049(O-14) 에 이어 **4회째**. **재발 방지(이번엔 실행함)**: A-0050 의 보정 방향은 **워크트리 직접 패치 → fresh 탐지축 → fresh 소음축 → 스위트 전량 → 원복** 을 모두 측정한 결과다. 앞으로 판별식 지시는 이 절차를 밟은 뒤에만 문구를 확정한다.
**O-14(소음)의 위치**: 보정하면 N4 는 다시 `approval_required` ⇒ **O-14 는 닫히지 않는다. 의도된 후퇴**(과소탐보다 과탐 = MVP-3 계약). 건전한 폐쇄는 **막다른 길 쪽 축소**(미해소 호출의 수신자 선언 타입 ↔ 지연 레코드 대상 타입 일치)로만 가능하며 **미실증** ⇒ TASK-041 로 분리.

**통과 확인(무발견 ≠ 통과 · 전부 독립 재현)**: 스위트 **184/184 PASS**(adversarial 39·default 121·metamorphic 3·negative-corpus 6·parity 15) — `main` 180/180 대비 신규 실패 0, **Codex 신고와 정확히 일치, 과장 없음** · `mutation-check.sh` **PASS(Expectation mutations checked: 317)** 일치 · 결정론 md5 3회(fresh F1) · **시험한 전 입력 exit 0/2 뿐**(3층 자동차단 0 = §4 불변식 유지) · `git diff --check` clean · **Python 골든패스 불변**(비-Java 케이스 **113건**이 `main` 과 문자 단위 동일). **rig-and-revert 6종**: A~E 각각 **단독 FAIL = load-bearing**, **F 만 무변화 → R-2**(원복 후 184/184 재확인). **기대값 변경 3건 검토**: `java-indirect-lambda-argument-fail-closed` 는 fail-closed → **실 엣지 탐지**(`[Flow.sink, Port.run, Ledger.settle]`)로 **강화**(약화 아님), enum 2건의 `unresolved` 원소 삭제는 필드 바인딩 확장으로 **해소되어 사라진 것**이며 두 케이스 다 `approval_required`·`fail_closed_present: true` 유지.
**계측 자기정정**: 프로토타입을 `.git` 없는 스크래치 사본에서 먼저 돌렸을 때 `expected-present`·`expected-none` 2건이 FAIL — **`.git` 제거 아티팩트**였고 실 워크트리 재측정으로 **183/184(N4 단독)** 로 정정. **Codex 귀책 아님.** (별건 기지의 함정: `run-tests.sh` 를 `timeout` 으로 감싸면 Rosetta 강등으로 Java 전량 가짜 FAIL — 이번엔 감싸지 않았다.)

**§1 보수적 개발 — 통과**: 델타 = 게이트 2(`check-indirect-impact.py` +26/-4 · `extract-java-callgraph.py` +301/-52)·`cases.yaml`·`run-tests.sh` 검증자 2블록·픽스처 4세트·handoff·summaries **뿐**. **`kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·Claude 소유 3-dot diff 0 바이트** ⇒ **킷 심층리뷰(형 지시 ★★)는 변경분 부재로 해당 없음.** 무관 리팩터·포맷·이름변경 0, scope-creep·over-reach 없음. 3-튜플→4-튜플 확장은 기존 갈래 동작 보존한 순수 확장(RIG-A~E 로 확인). **브랜치 동기화 5회째 미이행**(base 가 `265ba18` 이전) — collab-protocol §5.1 관행화 요망.

**🔴 보정 지시 (TASKS.md TASK-040 에 AC#6·#7·#8 로 고정)**: **AC#6**(R-1) `caller` 축 fallback 제거 → `dispatch_targets` 가 비면 `sink_dead_ends` 존재 시 승격 · **F1·F2·F3·F4·F7·F8 회귀 픽스처 6건 신설**(전부 `approval_required`) · **N4 기대값을 `approval_required` 로 정정**(리뷰어 지시 정정분 — Codex 귀책 아님) · 불변식(TASK-039 11케이스·소음 2케이스·Python 골든패스) · 음성검증. **AC#7**(R-2) **F6 형태 픽스처 1건** + 음성검증(교집합→truthiness 치환 시 단독 FAIL). **AC#8**(O-20) `has_static_modifier` 를 `modifiers` 자식 한정 + 토큰 분해 · instance 필드 `<init>` 픽스처 · 음성검증.
**비차단 관찰**: **O-21**(`java-indirect-lambda-argument-fail-closed` 이름/내용 불일치 + 이 시나리오의 fail-closed 경로 회귀보호 소실) · **O-22**(`fail_closed` detail 이 `dead_ends=` 는 전체를, 개수는 relevant 만 세어 카드에서 어긋남 · 1줄) · **O-23**(enum 상수 본문 caller 가 `Reg.<init>` — 실제로는 클래스 초기화 시점이고 익명 하위타입이 `Reg` 로 뭉개짐) · **O-13·O-3·O-15·O-16 이월**.

**정책**: `java.layers.callgraph` **`partial` 유지** — R-1 로 승격 근거가 오히려 후퇴. `supported` 승격은 **AC#6·#7 통과 후**(D-076 계약 유지). 정책 파일 무접촉.
**킷(TASK-038)**: **sync 계속 차단** — 지금 sync 하면 **R-1 놓침을 배포 킷에 그대로 싣는다**(현행 킷은 Java L3 부재 = 구멍이 아니라 미탑재). AC#6 통과 후 재개. D-093 의 "TASK-040 먼저" 권고는 유효하되 **근거가 소음 → 놓침으로 바뀌었다.** 킷 README·`manifest.yaml` 한계 명시에 **O-14 소음 특성**(sink 전방폐쇄가 외부 호출을 하나라도 하면 지연 dispatch 승격)을 반드시 포함할 것 — O-14 는 닫히지 않은 채 남는다.
**머지**: **코드 브랜치 보류.** 리뷰 기록만 `main` 머지(D-007). 변경은 하네스 게이트 로직 + 테스트뿐 — 정산·인증/인가·암호화·DB migration·infra **해당 없음**(선례 D-088·D-091·D-093) ⇒ **비민감**, 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0050.md`.

---

## D-095 — TASK-040 A-0050 보정 재제출 재리뷰 — **보정요청** (AC#6·#7 충족 · 해소된 dispatch 대상 갈래에서 과소탐 회귀 2건 신규) (A-0051) — 2026-07-22

**대상**: `codex/2026-07-22-task040-java-l3-precision` head `64e7777`, 보정 커밋 `1164ce0`. 기준선 `origin/main`=`ef9d39c`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**이고 handoff 최상단이 `Codex → Claude`(보정 재제출) ⇒ 재리뷰 차례.
**멱등성**: `4573b51`·`ea0191c` 는 A-0050 에서 **처리 완료 — 재리뷰하지 않았다.** 재리뷰 범위 = `ea0191c..64e7777`.
**판정**: 🔴 **보정요청 · 코드 브랜치 머지 보류.** **새 태스크 아님 — 보정 커밋만 재제출.**

**✅ 지시분은 전부 충족(재작업 불필요)**
- **AC#6 (R-1 · 종결)**: `caller ∈ sink_reachable` fallback → `if not dispatch_targets and sink_dead_ends:` 로 교체, `sink_reachable_functions` 완전 제거(`grep` 잔존 0). **RIG-1**(fallback 무력화) → **175/192**, 신규 6건 전부 FAIL = load-bearing. **픽스처 밖 fresh 재실증**: A-0050 §1.2 의 **F1·F2·F3·F4·F7·F8 6형태 + 대조군 F5 가 전부 `main` 과 동일한 `approval_required`(2)** 로 복구. N4 는 지시대로 `java-indirect-deferred-jdk-noise-fail-closed` 로 개명·`approval_required` 정정 + 사유 주석.
- **AC#7 (R-2 · 종결)**: `java-indirect-dispatch-target-intersection-pass`(F6) 신설. **RIG-2**(교집합→truthiness 약화) → **191/192 이 케이스 단독 FAIL** ⇒ A-0050 의 "184/184 무변화" 공백이 정확히 닫혔다. 픽스처 설계도 건전 — deferred 레코드 1건·대상 비지 않음이라 **교집합 축만 단독 단언**한다.
- **AC#8 (O-20)**: `child.type == "modifiers"` 한정으로 원 결함 폐쇄. **RIG-3** → 191/192 단독 FAIL. **단 잔여 1형태(O-24) → AC#11 로 이월.**
- **무회귀**: **192/192**(adversarial 47·default 121·metamorphic 3·negative 6·parity 15) · **mutation PASS(332)** · 결정론 md5 3회 · 전 입력 exit **0/2 뿐**(3층 자동차단 0) · **Python 골든패스 113건 `main` 과 문자 단위 동일** · `git diff --check` clean. **Codex 신고와 전부 일치 — 과장 없음.**
- **§1 보수적 개발 통과**: 보정 델타 = `check-indirect-impact.py`(+4/−14 순수 축소)·`extract-java-callgraph.py`(+1)·`cases.yaml`·픽스처 8세트·handoff·summaries **뿐**. **`kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·Claude 소유 3-dot diff 0 바이트** ⇒ **킷 심층리뷰(형 지시 ★★)는 변경분 부재로 해당 없음.** 무관 리팩터 0. 기대값 변경 1건(N4)은 리뷰어 지시 정정분이며 방향이 **강화**.

**🔴 R-3 (차단 · 과소탐 회귀 · `main` 보다 나쁨) — 해소된 dispatch 대상 + 불투명 sink 호출지점**: 교집합 축은 **양쪽이 다 해소될 때만** 건전하다. sink 쪽 호출지점이 미해소면 막다른 길이 대상(`Task.exec`)이 아니라 **미해소 호출의 caller(`Flow.sink`)** 로 기록되므로 교집합이 **구조적으로 항상 공집합** ⇒ 조용히 드롭. 배제의 근거가 "타입이 실제로 무관"(F6=건전)이 아니라 **"분석이 sink 쪽을 못 풀어서"(불건전)** 인 갈래가 통째로 열려 있다. **픽스처 밖 fresh 실증(`main` 2 → 브랜치 0)**: **G1** `Task task = () -> new Vault().transfer();` + `List<Task> tasks;` + `sink(){ tasks.get(0).exec(); }` · **G2** 게터 반환 호출 `sink(){ get().exec(); }` · **H1** `hops: 1` 경계(대상이 폐쇄 안이어도 hops 밖이면 동일 드롭 — A-0049 검증축 ⑦). **대조군 G3(파라미터 타입)·G4(지역변수 타입) 는 `approval_required` 유지** ⇒ 탐지가 통째로 죽진 않았으나 **`tasks.get(k).exec()`·`get().exec()`·`registry.find(k).handle()` = 콜백 레지스트리/디스패처 표준형이 전부 구멍**이다. G1 coverage 는 정직히 찍히고(`dispatch_targets: [Task.exec]` + `Flow.sink` unresolved) **판정만 조용히 통과**한다. §2B 필수질문 **예** ⇒ **비차단 금지.**

**🔴 R-4 (차단 · 과소탐 회귀 · 흔적조차 없음) — 인자전달 람다가 해소되면 fail-closed 표식이 통째로 증발**: `collect_calls()` 의 **필드 초기화 경로**(`scan_deferred`)는 대상이 해소돼도 deferred 레코드를 남기지만, **메서드 본문 경로**(`:700-707`)는 해소되면 **엣지만 만들고 레코드를 남기지 않는다**(`else` 갈래에서만 생성). ⇒ sink 가 그 인터페이스를 **불투명하게** 부르면 엣지도 안 닿고 레코드도 없어 **`java_deferred` 가 비고 fail-closed 가 아예 발동하지 않는다.** **fresh 실증 G6**(레지스트리 표준형: `Registry.put(String,Task)` 로 람다 등록 + `sink(){ reg.find(k).exec(); }`) → `main` **`approval_required`(2)** ↔ 브랜치 **`pass`(0)** 이고 `coverage.unevaluated` 에 `lambda_dispatch` **0건**·`fail_closed: []`·`errors: []` = **완전히 깨끗한 통과**(R-3 보다 나쁘다 — 흔적조차 없다). `Task.exec → Vault.transfer` 엣지는 존재하는데 `Flow.sink → Task.exec` 만 없어 경로가 끊긴다.

**🔧 보정 방향 — 리뷰어가 탐지축·소음축 모두 실측**(A-0050 §4 약속 절차 이행 · 프로토타입 2블록 전부 `check-indirect-impact.py` 안, 추출기 무접촉): **(a)** `sink_dead_ends` 중 **`kind: unresolved` caller 유래(불투명)** 가 있으면 교집합 정밀화를 적용하지 않고 보수 승격 → R-3 폐쇄. **(b)** 불투명 호출지점에서 **람다로 구현된 `bodyless` 노드**로 보수적 인접 추가 → R-4 폐쇄. **측정(원복 후 192/192 재확인)**: G1·G2·H1·G6 **전부 `approval_required` 복구** · **F6 `pass` 유지(정밀화 보존)** · **N3(무관 변경 + 람다가 변경함수에 안 닿음) `pass` 유지 = 소음 개선 보존**(⇒ `main` 으로의 단순 회귀가 **아니다**) · F1~F5·F7·F8·N2 불변 · **스위트 192/192 무변화** · 결정론 md5 3회. **(a) 단독으로는 G6 가, (b) 단독으로는 G1·G2·H1 이 안 고쳐진다 ⇒ 둘 다 필요.** **대가**: N1(F6+sink 에 JDK 호출) 은 `main` 수준 소음으로 복귀 = **의도된 후퇴**(O-14 는 A-0050 §4 대로 미폐쇄, TASK-041). **하류 정직성 요구**: (b) 는 관측되지 않은 홉을 인접그래프에 넣으므로 카드가 `path: [Flow.sink, Task.exec, Vault.transfer]` 를 **실경로처럼** 렌더한다 ⇒ **보수 추정 홉 표식 필수**(무표식이면 정직성 위반으로 재반려).

**🔴 자기정정(5회 연속 — 지시·검증 결함)**: **R-3** 은 A-0050 §2 가 교집합 축을 **F6(양쪽 해소) 하나로만** 확인하고 "축 자체는 작동한다" 고 통과시킨 결과다 — **sink 쪽 미해소 대칭 케이스를 안 만들었다.** **R-4** 는 A-0050 §5 가 `invocation_parameter_type` 을 **RIG-D 단독 FAIL** 만으로 load-bearing 처리한 결과다 — **rig 는 *추가된* 단언만 검증하고 *사라진* 커버리지는 검증하지 못한다.** ⇒ **교훈: 판별식을 좁히는 변경은 좁힘의 *반대 조건*(여집합)을 fresh 입력으로 반드시 쳐본다.** A-0047→A-0051 5회 모두 이 자리에서 났다. **Codex 귀책 아님** — AC#6·#7·#8 은 문언대로 정확히 구현됐고 §1 위반도 없다. R-3·R-4 는 A-0050 이 통과시킨 **1차 제출분의 잔여**이나, **브랜치 전체가 아직 `main` 에 없으므로 지금 막는 것이 맞다.**

**🟡 O-24(신규 · AC#11 로 승격)**: `has_static_modifier` 가 `modifiers` **노드 텍스트를 정규식 토큰화**하므로 **어노테이션 인자 문자열**의 `static` 에 걸린다 — `@SuppressWarnings("static") Task task = () -> log("x");` → `main` `Flow.<init>` ✅ / 브랜치 **`Flow.<clinit>`** ❌. **판정 무영향(정직성)** 이나 AC#8 과 동종·동급. **측정된 수정**: `modifiers` 자식 중 **텍스트가 정확히 `static` 인 키워드 노드** 판정 — 5형태(어노테이션 문자열·`static final`·`private static`·`@Deprecated private static`·수식어 없음) 전부 정답 확인.

**보정 지시(TASKS.md TASK-040 AC#9·#10·#11)**: **AC#9**(R-3 · 차단 — 불투명 막다른 길이 있으면 교집합 정밀화 미적용 · 픽스처 G1·G2·H1 + 대조군 G3·G4·F6 불변 + 음성검증) · **AC#10**(R-4 · 차단 — 해소된 람다/`::` 도 fail-closed 회수 대상 유지 · G6 픽스처 + **보수 추정 홉 표식** + 음성검증 · §6 7입력 표 재현) · **AC#11**(O-24 · 🟡). **무회귀**: 스위트·mutation·결정론·**정책·킷 무접촉**.

**비차단 관찰**: **O-21**(`java-indirect-lambda-argument-fail-closed` 이름/내용 불일치 — **AC#10 을 닫으면 fail-closed 경로가 되살아나므로 그때 함께 정리**) · **O-22**(`fail_closed` detail 의 `dead_ends=` 전체 ↔ 개수 relevant 불일치) · **O-23**(enum 상수 본문 caller `Reg.<init>` 표기) · **O-14·O-13·O-3·O-15·O-16 이월**.

**정책**: `java.layers.callgraph` **`partial` 유지** — R-3·R-4 로 승격 근거가 다시 후퇴. `supported` 재검토는 **AC#9·#10 통과 후**(D-076 계약). 정책 파일 무접촉.
**킷**: **TASK-038 sync 계속 차단** — 지금 sync 하면 R-3·R-4 놓침을 배포 킷에 그대로 싣는다. 현행 킷은 Java L3 **미탑재**(구멍 아님)이므로 대기가 안전. AC#9·#10 통과 후 재개하며 README·`manifest.yaml` 한계 명시에 **O-14 소음 특성**을 반드시 포함.
**브랜치 동기화**: 재제출 브랜치가 `main` 보다 2커밋 뒤처짐 — **5회째**. collab-protocol §5.1 관행화 요망.
**머지**: **코드 브랜치 보류.** 리뷰 기록만 `main` 머지(D-007). 변경은 하네스 게이트 로직 + 테스트뿐 — 정산·인증/인가·암호화·DB migration·infra **해당 없음**(선례 D-088·D-091·D-093·D-094) ⇒ **비민감**, 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0051.md`.

## D-096 — TASK-040 A-0051 보정 재제출 재리뷰 — **보정요청** (AC#9·#10·#11 기능 충족 · 과소탐 회귀 0 · 그러나 회귀보호 0 갈래 1건 + 카드 표식 왜곡 1건) (A-0052) — 2026-07-22

**대상**: `codex/2026-07-22-task040-java-l3-precision` head `661225f`, 보정 커밋 `7daee0c`. 기준선 `origin/main`=`2cc372e`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**이고 handoff 최상단이 `Codex → Claude`(보정 재제출) ⇒ 재리뷰 차례.
**멱등성**: `4573b51`·`ea0191c`(A-0050) · `1164ce0`·`64e7777`(A-0051) 은 처리 완료 — **재리뷰하지 않았다.** 재리뷰 범위 = `64e7777..661225f`.
**판정**: 🔴 **보정요청 · 코드 브랜치 머지 보류.** **새 태스크 아님 — 보정 커밋만 재제출.**

**✅ 지시분은 기능적으로 전부 충족(재작업 불필요) — 그리고 과소탐 회귀는 0이다**
- **AC#9 (R-3 · 종결)**: 불투명 막다른 길(`kind: unresolved` caller 유래)을 `java_opaque_dead_ends` 로 분리하고 **교집합 정밀화보다 앞에서** 보수 승격. 논리 정합 확인 — 옛 `sink_dead_ends` = 신 `sink_dead_ends` ∪ `opaque_sink_dead_ends` 이고, 후자가 비면 **정확히 동일**, 비지 않으면 조기 반환이 먼저 걸린다 ⇒ **판별식이 약해지는 갈래 없음.** 불투명 집합을 **인접 변조 전에** 계산하는 순서도 옳다(피드백 루프 방지). **RIG-1**(조기 반환 3줄 제거) → **183/199, 15건 FAIL**(신규 3건 전부 + F 계열 11건) = 강하게 load-bearing. **픽스처 밖 fresh**: G1(`tasks.get(0).exec()`)·G2(게터)·H1(`hops:1` 경계) + **리뷰어 신규 G1b(`Map.get(k).handle()`)·G1c(배열 인덱스)** 전부 `main` 과 동일한 `approval_required` 로 복구, 대조군 G3·G4 불변, **F6 `pass` 유지(AC#7 정밀화 보존)**.
- **AC#10 (R-4 · 기능 종결)**: 추출기 `owner_from_invocation` 로 **인자전달 람다/`::` 는 해소돼도 deferred 레코드 유지**, 판정 게이트는 불투명 호출지점 → 람다구현 `bodyless` 노드로 **보수 인접** 추가. **fresh G6 복구** + 카드가 `path: [Flow.sink, Task.exec, Vault.transfer]` 로 승격. **리뷰어 신규 G6b(`::`)·G6c(익명 클래스)·P3(지역변수 람다)** 중 **G6c·P3 은 `main` 이 `pass` 인데 브랜치가 `approval_required` = 강화**. **RIG-2**(인접 추가 제거) → 197/199 단독 FAIL, **RIG-3**(람다 레코드 제거) → 196/199 2건 FAIL = load-bearing. **O-21 부수 해소**(`…lambda-argument` 기대값이 `fail_closed_present: true` 로 정정돼 이름·내용 재일치).
- **AC#11 (O-24 · 종결)**: `modifiers` 자식 중 **텍스트가 정확히 `static` 인 키워드 노드** 판정으로 교체. **fresh 5형태 전량 정답**(어노테이션 인자 문자열·`static final`·`private static`·`@Deprecated private static`·수식어 없음) — **`main` 은 3형태 오답**이므로 순수 개선. **RIG-5** 단독 FAIL = load-bearing.
- **무회귀**: 브랜치 **198/199** · `main` **179/180** — 유일 FAIL `tree-sitter-smoke` 은 리뷰 환경의 `tree_sitter_javascript`·`tree_sitter_typescript` 미설치 탓으로 **양쪽 동일 ⇒ 브랜치 귀책 아님**. **`comm -23 main.pass br.pass` = 차집합 0** ⇒ `main` 통과 케이스가 브랜치에서 깨진 것 **하나도 없음**. **mutation PASS(345)** · 결정론 md5 3회 동일 · 전 입력 exit **0/2 뿐**(3층 자동차단 0). **총 25개 fresh 입력에서 `main` `approval_required` → 브랜치 `pass` 인 과소탐 회귀 0건** — 다이버전스 3건은 강화 2건 + 승인된 정밀화 1건(F6). **성능**: 보수 인접이 |불투명|×|람다 bodyless| 카티션이라 폭주를 의심해 **120×120 합성 repo 실측 → 0.2s(`main` 동일)**, 문제 없음. **Codex 신고(199/199·mutation 345·음성검증 3종)는 실질적으로 정확 — 과장 없음.**
- **§1 보수적 개발 통과**: 델타 = 게이트 2 · `cases.yaml` · 픽스처 6세트 · `run-tests.sh`(`inferred` 통과 1블록, 순수 가산) · handoff · summaries **뿐**. **`kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·Claude 소유 3-dot diff 0 바이트** ⇒ **킷 심층리뷰(형 지시 ★★)는 변경분 부재로 해당 없음.** 무관 리팩터 0. 기대값 약화 0(유일 변경은 `false→true` 로 **강화**).

**🔴 R-5 (차단 · 회귀보호 0 · A-0051 R-2 와 동종) — `method_reference` 인자전달 갈래가 무방비**: 추출기에 **쌍둥이 블록 2개**(람다 / `::`)가 추가됐는데 람다 쪽만 픽스처 2건이 고정한다. **RIG-4**(`method_reference` 갈래의 `if owner_from_invocation: unresolved.add(...)` 9줄만 제거) → **198/199, FAIL 0건 = 스위트 완전 무발견.** 그런데 fresh 입력은 뚫린다 — `hops: 1` 로 보수 인접을 굶기면 이 레코드가 **유일 방어선**이다: `Registry.put(String,Task)` 에 **`reg.put("pay", vault::transfer)`** 등록 + `mid(k){ reg.find(k).exec(); }` + `sink(k){ mid(k); }` → `main` **`approval_required`(2)** · 브랜치 **`approval_required`(2)** · **RIG-4 `pass`(0)·`fail_closed: []`·레코드 증발**. 코드는 옳으나 **다음 편집 한 번에 조용히 되돌아간다** ⇒ §2B 상설 회귀 픽스처 원칙 위반, 비차단 금지(A-0051 이 동일 사유로 AC#7 을 만들었다).

**🔴 R-6 (차단 · 감사카드 정직성) — `inferred: true` 가 완전히 관측된 경로에도 찍힌다**: AC#10 은 *"보수 추정으로 추가된 홉은 **실제 관측 호출과 구분 표시**"* 를 요구했는데, `inferred_edges.add((caller, callee))` 가 `if callee not in adjacency[caller]:` 블록 **밖**이라 **이미 관측된 엣지도 추정으로 등록**된다. **fresh 실증(P6)**: sink 안에 관측 호출 `direct.exec()` + 불투명 `reg.find("x").exec()` 를 함께 두면, 추출기 `edges` 가 `Flow.sink→Task.exec`(`direct.exec`)·`Task.exec→Vault.transfer`(lambda) 를 **둘 다 실제 호출로** 기록하는데도 카드가 `inferred: true` 로 렌더한다 — **추정 홉 0개인 완전 관측 경로**를 추정으로 표시. verdict 는 안전하나 감사카드는 사람이 30초에 판단하는 물건(§2C)이고, 표식의 존재 이유가 *"확실치 않으니 감안하라"* 이므로 **실제 관측된 민감 경로를 후순위로 밀 근거를 준다** = AC#10 이 금지한 방향의 거울상. **수정 = 1줄 들여쓰기**(리뷰어 실측: P6 표식 소멸 + 스위트 198/199 유지 + `…registry-lookup-lambda` 의 진짜 `inferred: true` 보존). **표식 정확성도 회귀보호 0** — 올바른 구현과 버그 구현이 **둘 다 198/199** ⇒ 스위트는 표식의 *존재* 만 고정하고 *정확성* 은 고정하지 않는다.

**🟡 O-25 (신규 · AC#14 로 승격) — `fail_closed` detail 의 `dead_ends=` 가 빈 문자열**: 불투명 caller 를 `sink_dead_ends` 에서 분리했는데 detail 문자열은 그대로 `sink_dead_ends` 만 출력한다 ⇒ **이번 보정이 겨냥한 모든 시나리오에서 카드가 `dead_ends=` 로 끝난다**(G1·H1·G6: `main` 은 `dead_ends=Flow.sink`/`Flow.mid` 를 보여줬다). 판정 무영향이나 **`main` 대비 카드 정보 회귀**이고 하필 주력 시나리오 전부에 걸린다. 이미 이월 중인 **O-22 와 동종·동급이며 같은 3줄 안**이라 함께 닫는 편이 싸다. **`grep dead_ends tests/` = 0건** ⇒ detail 을 단언하는 케이스가 아예 없다.

**🔵 자기정정 없음(6회 만에)**: A-0047~A-0051 은 매번 리뷰어 **지시 자체**의 결함을 자기정정했으나, 이번 델타는 A-0051 의 (a)·(b) 방향과 7입력 표를 그대로 재현했고 리뷰어 신규 fresh 형태(G1b·G1c·G6b·G6c·P1~P6 · 총 25입력)에서도 과소탐이 나오지 않았다 — **지시가 처음으로 정확했다.** 다만 A-0051 §5 의 교훈이 이번엔 구현 쪽에서 재발했다(쌍둥이 블록 중 하나만 고정 · 표식은 존재만 고정). ⇒ **교훈 갱신: 대칭 코드를 두 갈래로 추가하면 픽스처도 각 갈래를 *굶겨서*(다른 갈래가 덮지 못하게) 단독 단언해야 한다.**

**보정 지시(TASKS.md TASK-040 AC#12·#13·#14)**: **AC#12**(R-5 · 차단 — `::` 인자전달 갈래 픽스처 + `hops:1` 설계 + 음성검증 단독 FAIL) · **AC#13**(R-6 · 차단 — `inferred_edges.add` 1줄 이동 + P6 형태 픽스처로 "관측 경로에는 표식 없음" 단언 + 음성검증) · **AC#14**(O-25 · 🟡 — detail 에 불투명 집합 합산 + O-22 개수/집합 불일치 정리 + detail 단언 케이스 신설). **무회귀**: 스위트·mutation·결정론·**정책·킷 무접촉**.

**정책**: `java.layers.callgraph` **`partial` 유지** — R-3·R-4 가 닫혀 승격 근거는 실질 회복됐으나 **R-5(회귀보호 0) 폐쇄 전에는 승격하지 않는다.** 보호 없는 탐지는 승격 근거가 못 된다(D-076). 정책 파일 무접촉.
**킷**: **TASK-038 sync 계속 차단** — 차단 근거가 A-0051 의 "놓침을 배포 킷에 싣는다" 에서 **"보호 없는 탐지를 싣는다"** 로 완화됐으나, AC#12·#13 이 1줄/1픽스처 규모라 **먼저 닫고 sync 하는 편이 명백히 싸다.** README·`manifest.yaml` 의 **O-14 소음 특성 명시** 요구는 그대로 유효.
**브랜치 동기화**: 재제출 브랜치가 `main` 보다 2커밋 뒤처짐 — **6회째.** collab-protocol §5.1 관행화 요망.
**환경 관찰(형 참고 · 브랜치 무관)**: 리뷰 환경에 `tree_sitter_javascript`·`tree_sitter_typescript` 미설치로 `tree-sitter-smoke` 가 `main` 에서도 FAIL. `requirements.txt` 반영 또는 스킵 조건이 있으면 리뷰 재현성이 좋아진다.
**머지**: **코드 브랜치 보류.** 리뷰 기록만 `main` 머지(D-007). 변경은 하네스 게이트 로직 + 테스트뿐 — 정산·인증/인가·암호화·DB migration·infra **해당 없음**(선례 D-088·D-091·D-093·D-094·D-095) ⇒ **비민감**, 형 승인(H-XXXX) 불필요. 상세 `collab/answers/A-0052.md`.

---

## D-097 — TASK-040 A-0052 보정 재제출 재리뷰 — **리뷰 통과 · `main` 머지** (AC#12·#13 폐쇄 · AC#14 주 증상 폐쇄 · O-22 이월) (A-0053) — 2026-07-22

**대상**: `codex/2026-07-22-task040-java-l3-precision` head `0fb882b`, 보정 커밋 `e6c975f`. 기준선 `origin/main`=`ec39a2a`. `fetch --prune` 후 **미머지 codex 브랜치는 이 1개뿐**이고 브랜치 handoff 최상단이 `Codex → Claude`(보정 재제출) ⇒ 재리뷰 차례.
**멱등성**: `4573b51`·`ea0191c`(A-0050) · `1164ce0`·`64e7777`(A-0051) · `7daee0c`·`661225f`(A-0052) 는 처리 완료 — **재리뷰하지 않았다.** 재리뷰 범위 = `661225f..0fb882b`.
**판정**: ✅ **리뷰 통과 · 비민감 ⇒ Claude 가 `main` 머지**(D-007, 구현자≠머지자). **TASK-040 종결.**

**✅ AC#12 (R-5 종결 · 회귀보호 신설)**: `hops: 1` 로 보수 인접을 **굶긴** 픽스처 `java-indirect-registry-lookup-method-reference-hop`(`reg.put("pay", vault::transfer)` + `mid(k){reg.find(k).exec();}` + `sink(k){mid(k);}`)가 `verdict`·`exit_code`·`coverage_unevaluated` 원소(`Flow.wire|method_reference|vault::transfer`)를 단언한다. **RIG-C**(`method_reference` 갈래 `if owner_from_invocation:` 9줄만 제거) → **200/202, 이 케이스 단독 FAIL.** A-0052 시점 동일 rig 는 **FAIL 0** 이었으므로 회귀보호 0 → 단독 load-bearing 으로 정확히 전환. **쌍둥이 재확인 RIG-3**(람다 쪽 제거) → 3건 FAIL ⇒ **두 갈래 각각 고정 완료**(A-0052 §6 교훈 이행). **픽스처 밖 fresh 변형**(`Bus.subscribe(String,Job)`+`ledger::post`, 이름·구조 전부 다름)도 `main` 과 동일 `approval_required` + 동일 coverage 레코드.

**✅ AC#13 (R-6 종결 · 카드 표식 정직성)**: `inferred_edges.add((caller, callee))` 를 `if callee not in adjacency[caller]:` 블록 **안으로** 이동(1줄) ⇒ **실제로 새로 삽입한 엣지만** 추정 등록. **과잉억제 없음을 두 축으로 실증** — ① 같은 `(caller,callee)` 가 관측이면 표식 없음이 정답이고 루프가 caller×callee 를 1회만 방문하므로 이전 반복 오염 경로 없음 ② `path_has_inferred_edge` 가 **any** 라 **부분추정도 표식 유지**. **픽스처 밖 fresh 3형태**: **B**(관측 `direct.run2()` + 불투명 공존) `prev` `inferred: true` ❌ → 브랜치 **표식 없음** ✅ / **C**(순수 추정) `inferred: true` **유지** ✅ / **D**(관측 1홉 + 추정 1홉 혼합) `inferred: true` **유지** ✅. 세 형태 다 **verdict 불변**(표식만 변경 = 설계 의도). **RIG-A**(들여쓰기 원복) → **200/202 단독 FAIL.** `cases.yaml` 의 `inferred` 단언이 **존재 1 + 부재 1 = 양방향** 으로 고정됐다(`impact_summary()` 가 truthy 일 때만 키를 넣으므로 기대값에 키 부재 = 표식 부재 단언).

**⚠️ AC#14 — 주 증상 폐쇄 · O-22 미이행(이월)**: `relevant_dead_ends = sink_dead_ends.union(opaque_sink_dead_ends)` 로 **빈 `dead_ends=` 회귀 폐쇄** — fresh A·H·C 에서 `dead_ends=Svc.mid`·`Svc.entry` 복구(`prev` 는 전부 공백). **정합성**: 불투명 집합이 비면 합집합 = 기존 집합(동작 불변), 비지 않을 때만 이름 추가 ⇒ **새 부정확 없음**, `sorted()` 로 결정론 유지. **회귀보호 신설**: `run-tests.sh` `fail_closed_details` 단언(순수 가산) + `java-indirect-opaque-dead-end-detail` 이 detail 문자열 직접 단언 ⇒ A-0052 의 `grep dead_ends tests/` = 0건 해소. **RIG-B**(union 원복) → 단독 FAIL. **다만 O-22(개수=relevant / 집합=전체)는 손대지 않았다** — fresh probe 로 잔존 확인(`dispatch_targets={Job.run2}` 인데 detail 은 `dead_ends=Job.run2,Other.go`). **§2B 필수질문 = 아니오**(방향이 **과대열거** · verdict 무영향 · `prev`·`main` 과 동일하므로 이 델타의 회귀 아님 · 대상 불명 레코드에서는 전체 열거가 오히려 정확) ⇒ **비차단 이월.**

**🟡 O-26 (신규 · 기록 정정)**: `summaries/2026-07-22.md` 가 *"O-25/O-22를 닫았다"* 고 적었으나 **O-22 는 닫히지 않았다**. `handoff-log.md` 본문은 *"관련 opaque/bodyless dead-end 합집합을 이름으로 기록"* 으로 **정확**하므로 은폐 아님 = 요약문 1문장 과장. 판정·코드 무영향이라 비차단, **기록은 A-0053·`review-notes.md`·TASKS.md 로 정정**한다. **교훈**: 관찰 ID 를 "닫았다" 고 쓸 때는 **그 ID 의 정의 문장이 그대로 재현되는지** 확인할 것 — ID 는 세션을 건너 인용되므로 요약문 과장이 다음 세션의 오판이 된다.

**무회귀·결정론**: 브랜치 **201/202** · `main` **179/180** — 유일 FAIL `tree-sitter-smoke` 은 리뷰 환경의 `tree_sitter_javascript`·`tree_sitter_typescript` 미설치 탓으로 **양쪽 동일 ⇒ 브랜치 귀책 아님**. **`comm -23 main.pass br.pass` = 차집합 0.** **mutation PASS(351)**(345 → +6 = 신규 3케이스분) · fresh 8케이스 출력 md5 **3회 동일** · 전 입력 exit **0/2 뿐**(3층 자동차단 0) · `parity 15/15`·`default` `main` 동일(Python 골든패스 무접촉) · **선행 RIG-1 재확인 → 184/202, 코드 17건 FAIL**(A-0052 시점 15건 → 신규 케이스 2건이 추가로 걸림) = 기존 보호 약화 없음. `git diff --check` clean · `py_compile` PASS. **Codex 신고(mutation 351 · "코드 관련 201건 PASS, `tree-sitter-smoke` 1건만 환경사유") 그대로 재현 — 과장 없음**(O-26 문장 1건 제외).

**§1 보수적 개발 통과**: **3-dot diff 에 `kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·`TASKS.md`·Claude 소유 파일 0 바이트** ⇒ **킷 심층리뷰(형 지시 ★★)는 변경분 부재로 해당 없음**(run.sh 배선·verdict 조립·sync·selftest·`--policies` 오버라이드 전부 이번 델타에 없음). **이번 델타 = 게이트 2줄 · `run-tests.sh` +7줄(순수 가산) · `cases.yaml` +66줄(삭제 0) · 픽스처 3세트 · handoff · summaries 뿐.** 무관 리팩터·포맷·이름변경 0, 기대값 약화 0(기존 케이스 수정 0). 커밋 §3 5절 형식 완비·문구 정확. **잔티**: 브랜치 미동기화 재제출 **8회째**(`handoff-log.md`·`summaries` 충돌을 Claude 가 양측 보존으로 해소) — 재제출 전 `origin/main` 머지 관행화 요망(collab-protocol §5.1).

**내가 짠다면(대안 검토)**: `inferred_edges` 집합 대신 **엣지에 출처 태그**(`source: observed|inferred`)를 달면 같은 쌍이 두 출처를 가질 때도 정확하다. 다만 현행 병합 규칙(**관측 우선**)이 **안전 방향**(카드가 덜 겁주지 않음)이고 7줄 vs 추출기 스키마 변경이라 **현행이 옳은 균형** — 대규모 리팩터 강요 안 함.

**하류 영향(TASK-038 킷)**: `inferred` 키는 **카드 렌더에 노출돼야** 의미가 있다 ⇒ 킷 README·`manifest.yaml` 에 **표식의 뜻**("보수 추정 홉 포함 — 실제 호출 관측 아님")을 적지 않으면 배포 킷 사용자에겐 무의미한 키다. **TASK-038 AC 에 추가.** `dead_ends=` 에 **무관한 이름이 섞일 수 있음(O-22)** 도 README 한 줄로 고지 권고.

**정책**: `java.layers.callgraph` **`partial` 유지.** D-093/D-076 의 승격 조건은 **AC#1(O-14 소음) + O-19 폐쇄**인데 **O-14 가 열린 채**다(A-0050 §4·A-0051 AC#10 에서 **"의도된 후퇴"** 로 명시 이월). 탐지·회귀보호·표식 정직성은 전부 회복됐으나 **`supported` 는 under-claim 원칙 위반**(D-074 O-5·D-075) ⇒ **승격 재검토 = TASK-041(O-14) 폐쇄 후.**

**킷**: **TASK-038 sync 차단 해제.** 차단 근거가 A-0051 "놓침 탑재" → A-0052 "보호 없는 탐지 탑재" 로 완화됐고 **AC#12·#13 폐쇄로 모두 소멸**. 착수 조건 4가지(README·`manifest.yaml` 의 **O-14 소음 특성** 명시 · **`inferred` 표식 뜻** 명시 · 정책 **`partial` 로 동기화**(`supported` 금지) · `nodes[].bodyless` 스키마 동반(O-13)).

**비차단 이월**: **O-22**(레코드별 관련 dead-end 만 열거) · **O-26**(요약문 과장 — 기록 정정으로 처리) · **O-23**(enum 상수 본문 caller 표기) · **O-14**(소음 → TASK-041) · **O-13·O-3·O-15·O-16 이월**.

**환경 관찰(형 참고 · 브랜치 무관)**: 리뷰 환경·Codex 환경 모두 Python 3.9 에서 `tree_sitter_javascript`·`tree_sitter_typescript` 설치 불가로 `tree-sitter-smoke` 가 **`main` 에서도** FAIL. `requirements.txt` 의 Python 버전 요구 명시 또는 스킵 조건이 있으면 리뷰 재현성이 좋아진다 — TASK 로 세울지는 형 판단.

**상세**: `collab/answers/A-0053.md`.

---

## D-098 — TASK-041 리뷰 — 🔴 **보정요청 · 코드 브랜치 머지 보류** (AC#1·#2·#3·#4 폐쇄 / R-1·R-2·R-3 차단) (A-0054) — 2026-07-22

**대상**: `codex/2026-07-22-task041-java-l3-noise` — `1f0c60b`(구현) · `0ed3c07`(인계기록). **범위 = `7916a7a` ↔ 브랜치 3-dot diff 전체**(TASK-040 계열은 D-097 처리 완료 — 재리뷰 없음).

**결정**: **보정요청.** 코드 브랜치는 `main` 에 머지하지 않는다. 리뷰 기록(`decisions.md`·`review-notes.md`·`collab/answers/A-0054.md`·TASKS.md AC#5~#7)만 `main` 에 머지한다(D-007). **새 태스크 아님 — 같은 브랜치에 보정 커밋만 재제출.**

**✅ 닫힌 것(재작업 불필요)** — **AC#1(O-14)**: N4 소음 폐쇄. `java-indirect-deferred-jdk-noise-pass` 신설(`adversarial`→`negative-corpus`), **RIG-1**(정밀화 4-분기 전체 원복) → **201/203 이 케이스 단독 FAIL** = load-bearing. **AC#2(O-22)**: `java-indirect-relevant-dead-end-detail` 신설, **RIG-2 단독 FAIL**, **fresh P14**(`Alpha`/`Beta`/`Ledger` — 이름·구조 전부 다름)에서 `main` `dead_ends=Alpha.fire,Beta.beam` → 브랜치 `dead_ends=Alpha.fire` ⇒ **D-097 이 적은 정의 문장이 그대로 재현**. **AC#3(O-23)**: **RIG-3 단독 FAIL**, **fresh E3**(상수 2개)에서 `main` 은 둘 다 `Reg.<init>` 로 뭉개고 브랜치는 `Reg.A.<clinit>`·`Reg.B.<clinit>` 로 **구분** = 표기 정정을 넘은 식별력 증가. **AC#4 무회귀**: 브랜치 **202/203** ↔ `main` **201/202**(유일 FAIL `tree-sitter-smoke` 은 파서 미설치 · 양쪽 동일 ⇒ 브랜치 귀책 아님) · mutation **PASS(353)** · md5 3회 동일 · `py_compile`·`diff --check` PASS · `parity 15/15` · Python 골든패스 무접촉 · 전 입력 exit **0/2 뿐**. **Codex 신고와 전부 일치 — 과장 없음**(O-28 문구 1건 제외).

**🔴 R-1 (차단 · `main` 보다 나쁨 · 흔적 없는 과소탐)**: 소음을 만드는 조건이 탐지 fallback 을 꺼버린다. `not opaque_receiver_types` 가 **전칭(all-미상)** 판정이라, 불투명 폐쇄에 타입 붙는 호출이 **하나라도** 섞이면(`rows.size()` 한 줄) 분기가 죽고 **타입 못 붙는 진짜 dispatch 가 흔적 없이 드롭**된다. 필요한 건 **존재(any) 판정**. **fresh 실증** — **P4**(`Runnable task` + `wire()` 등록 + `obtain().run()` + `rows.size()`) · **P6**(`pool.submit(()->…)`) · **P7**(`holder.task.run()`) 전부 `main` **2** → 브랜치 **0**, 출력은 `errors:[]`·`fail_closed:[]`·`indirect_impact:[]` **완전 무흔적**. **대조군 P5 = P4 에서 `rows.size();` 한 줄만 삭제 → 2 유지**, **P12**(직접 dispatch) **2 유지** ⇒ **무관한 JDK 호출 한 줄이 판정을 뒤집는다.** 실 repo sink 는 거의 항상 JDK 호출을 가지므로 **이 fallback 은 실전에서 사실상 항상 꺼져 있다.** §2B 필수질문 **예** ⇒ 비차단 금지. **근본원인**: `receiver_type()` 은 **호출 대상 탐색을 넓히려고** 만든 헬퍼라 체인의 **루트 식별자**로 추측한다 — 틀려도 예전엔 `unresolved` 로 안전하게 떨어졌다. 그 값을 **좁히는 근거**로 재사용하면서 **오차의 안전 방향이 뒤집혔다**(이제 잘못된 추측이 경보를 지운다). 실측 2건: `List<String> rows` → `receiver_type "String"`(컨테이너 아닌 **타입 인자** 누출 · N4 기대값에 그대로 박힘) · `holder.task.run()` → `"Holder"`(실제 수신자 `holder.task` 는 `Runnable`) = **P7 이 뚫리는 직접 원인**.

**🔴 R-2 (차단 · 탐지가 메서드 *이름* 화이트리스트 종속)**: `name.rsplit(".",1)[-1] in {"find","get","lookup"}` 는 근거 없는 매직 상수다. **RIG-4**(집합 무력화) → **199/203**, 3건 FAIL(그 중 `…method-reference-hop-boundary` 는 `approval_required`→**`pass`**) ⇒ 세 형태의 탐지가 오로지 이름에 달려 있다. **fresh 실증**: 머지된 픽스처를 **`find`→`resolve` 한 단어만** 바꾼 **P15** = `main` **2** → 브랜치 **0**, 대조군 **P16**(`find`) **2 유지**. `resolve`·`fetch`·`provide`·`create`·`of`… 어느 이름이든 조용히 통과 ⇒ **게이트 탐지범위가 팀 명명 취향에 종속**되고 우회가 자명하다. 게다가 이 축은 `call_text` 가 `split("(",1)[0]` 로 잘리는 **파싱 아티팩트**(바깥 호출 레코드 이름이 `reg.find` 가 됨)에 얹혀 있다 = 설계가 아니라 부수효과.

**🟠 R-3 (차단 · 닫힌 AC 의 회귀)**: `relevant_dead_ends` 가 불투명 dead-end 를 `dispatch_targets` 가 빌 때만 남겨, **레코드가 `dispatch_targets` 를 가진 채 불투명 분기로 승격되면 승격의 실제 이유가 detail 에서 빠진다.** **fresh P13**: `main` `dead_ends=Flow.sink`(정확) → 브랜치 **`dead_ends=`(빈 값)** — **D-097 AC#14 가 닫은 O-25 증상의 재발**. 판정 불변이라 🔴 는 아니나 감사카드 정직성(CLAUDE.md §2C)을 되돌리므로 **비차단으로 흘리지 않는다.**

**🟡 O-27 (신규 · 회귀보호 0)**: `synthetic_initializer` + `not opaque_receiver_types` **동시 rig**(단독 rig 는 분기끼리 서로 가림) → **200/203**, FAIL 은 `synthetic_initializer` 몫 2건뿐 ⇒ **`not opaque_receiver_types` 를 고정하는 케이스가 203 중 하나도 없다.** 그런데 실전 load-bearing 이다(같은 rig 에서 **P5 가 2→0**). **A-0051 R-2 와 같은 자리** — 보정 시 존재-판정으로 고친 뒤 **음성검증 픽스처 필수**.

**🟡 O-28 (신규 · 기록 정확도)**: handoff·summaries 의 *"**타입 미상**·불투명 조회·합성 초기화는 보수 판정을 유지한다"* 는 **구현과 다르다**(전부 미상일 때만 유지). 은폐 아닌 전칭/존재 혼동이나 다음 세션이 "타입 미상은 안전" 으로 읽으면 오판 ⇒ 재제출 시 문구를 실동작에 맞출 것. **O-26 의 교훈이 그대로 재적용**.

**🔧 보정 방향 — 리뷰어가 워크트리에 직접 패치해 탐지축·소음축을 모두 실측**(A-0050 §4 절차): **(a)** 추출기에 **레코드 기록 전용** `precise_receiver_type()` 신설 — 체인(`field_access`·`method_invocation`·배열·캐스트)은 **`None`(미상)**. **`receiver_type()` 자체는 불변**(엣지 탐색의 넓힘 근거라 좁히면 엣지를 잃는다). **(b)** 게이트에서 `not opaque_receiver_types` → **`opaque_untyped_dispatch`(존재 판정)** 교체. **(c)** 매직 이름 화이트리스트 **삭제**. **(d)** 불투명 분기로 승격했으면 그 dead-end 를 **`dispatch_targets` 유무와 무관하게 항상 열거**. **(e)** (a) 적용 시 체인 안팎 레코드가 6번째 필드만 달라 `set` dedup 이 풀리므로 `(caller,kind,name,line,dispatch_targets)` 로 dedupe 하되 **타입 미상 쪽을 남길 것**(보수 방향). **측정(원복 후 202/203 재확인)**: **P1·P3·P4·P5·P6·P7·P11·P12·P13·P14·P15·P16 12형태 전부 `main` 과 동일 복구** · **N4 `pass` 유지 ⇒ O-14 폐쇄가 살아 있다**(소음으로 되돌아간 게 아니다) · **O-22 케이스 PASS 유지** · **화이트리스트 동시 제거해도 verdict/exit FAIL 0** ⇒ (c) 안전 · 잔여 FAIL 3건은 전부 (d)·(e) 몫. **(a)만·(b)만으로는 P7 또는 P4 가 안 고쳐진다 — 둘 다 필요.**

**🔴 자기정정 (내 AC 결함)**: AC#1 이 축만 지목하고 **"수신자 타입을 못 구하면 어떻게 하라"** 를 안 적어 **미상 처리(전칭 vs 존재)가 구현자 재량**으로 남았다. 또 *"필수 fresh 검증축 ⑥ 불투명 dispatch 표준형"* 에 **"소음과 *동시에* 존재하는" 조합**을 명시하지 않았고 그 조합이 정확히 P4/P7 이다. **교훈(A-0051 확장)**: **기존 헬퍼를 정밀화 근거로 재사용하면 그 헬퍼가 원래 어느 방향으로 틀렸는지를 반드시 다시 따져라** — 넓히는 데 쓰던 근사는 틀려도 안전했지만 좁히는 데 쓰면 같은 오차가 곧 놓침이다. **미상값 처리 규칙은 AC 에 못박는다(존재-판정 = 보수).**

**§1 보수적 개발 통과**: 3-dot diff 에 **`kit/`·`policies/`·`docs/`·`templates/`·`AGENTS.md`·`TASKS.md`·Claude 소유 0 바이트** ⇒ **형 지시 ★★ 킷 심층리뷰는 변경분 부재로 해당 없음**(`run.sh` 배선·verdict 조립·co-located 의존·`HAS_RANGE`/정책부재/`--policies` 오버라이드·sync·selftest·진입점이 이번 델타에 한 줄도 없다). 델타 = 게이트 2개 · `cases.yaml` · `run-tests.sh`(+32 순수 가산) · 픽스처 1세트 · handoff · summaries **뿐**. 무관 리팩터 0. 기존 기대값 수정 2건은 **둘 다 AC 가 지시한 정정**(O-23 caller · N4 verdict) = 약화 아님. 커밋 §3 5절 완비. **잔티: `origin/main` 미동기화 재제출 9회째** — collab-protocol §5.1 관행화 요망.

**정책**: `java.layers.callgraph` **`partial` 유지** — O-14 주 증상은 닫혔으나 **R-1·R-2 로 승격 근거가 오히려 후퇴**했다. 승격 조건을 **AC#5+AC#6+AC#7** 로 갱신(D-076·D-097).

**킷**: 이번 브랜치는 킷 무접촉이라 **TASK-038 sync 차단 해제 상태 자체는 유지**된다. 단 **TASK-041 머지 전에는 sync 금지** — 지금 스냅샷하면 R-1·R-2 를 배포 킷에 싣는다(현행 킷은 Java L3 **미탑재** = 구멍 아님). D-097 의 README·`manifest.yaml` 4항목 요구는 그대로 유효.

**비차단 이월**: O-27(보정 시 함께 폐쇄) · O-28 · O-13 · O-3 · O-15 · O-16.

**상세**: `collab/answers/A-0054.md`.
