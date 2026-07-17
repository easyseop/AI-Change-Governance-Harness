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
