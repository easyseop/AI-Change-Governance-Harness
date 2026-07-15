# review-notes.md — Claude 리뷰 기록 (정책 의도 대비 검수)

> 게이트가 "도는지"가 아니라 "내가 의도한 위험을 잡는지"를 본다.
> 결과 승급은 `collab/decisions.md`. 여기는 근거·검증·비차단 관찰.

---

## TASK-022b R-1 재리뷰 (D-050) — 보정 재제출 **통과** · Claude main 머지 (TASK-022b 완결·킷 v0 수용)

**대상**: `claude/2026-07-15-kit-draft` 보정 델타 `f1bf533`(fix) + `39c2285`(docs). 멱등성(D-049): `00bde19`·`88a7d4e` 재처리 금지 — 통과분(판정 조립·우선순위·--policies·스냅샷 충실성)은 재론 없음, 델타만 재리뷰.

### 델타 한 줄씩
- `kit/run.sh` L87: `) & watcher=$!` → `) >/dev/null 2>&1 & watcher=$!` — **A-0016 처방 ①과 문자 단위 일치.** watcher 서브셸(과 그 자식 `sleep`)의 stdout/stderr 를 /dev/null 로 분리 → kill 후 고아 `sleep` 이 호출자 파이프 write end 를 더는 쥐지 않음. 타임아웃 감지 경로(마커파일 `$tmp.timeout` 기록·TERM/KILL)는 fd 와 무관해 무영향.
- `kit/tests/run-entrypoint-tests.sh`: `run_pipe_latency_case` 신설 — **파이프 캡처(`$(…)`)** 로 `ACGH_GATE_TIMEOUT_SECONDS=30` 명시(A-0016 처방 ②의 "큰 타임아웃값 명시" 준수 — timeout=1 우회 가림 차단) + `rc=0`(판정 정확성 동시 단언) + 벽시계 `<10s` 단언. FAIL 시 exit·elapsed·출력 tail 진단 출력. 케이스 `pipe-capture-no-timeout-delay` 를 harmless-change 픽스처 repo 로 등록. TOTAL/PASS 집계·요약 라인 `[ "$PASS" = "$TOTAL" ]` 게이팅에 정상 편입.

### 실증 (격리 worktree `39c2285`)
- **스위트 재현**: 진입점 **6/6 PASS**(전체 벽시계 4.2s — 신규 케이스 포함해 즉시 종료) · `selftest.sh` **PASS**(77 케이스+mutation 127, "킷 게이트 무결").
- **fresh 적대입력(픽스처 밖)**: 신규 합성 repo(lib/** intent·harmless 델타)에서 **기본 타임아웃(60s)** 파이프 캡처 `out=$(kit/run.sh HEAD~1..HEAD --repo …)` → **elapsed 0s · verdict pass · exit 0**. D-049 실측(동일 호출 60s)과 대비 = 회귀 소멸, R-1 원 증상 기준으로도 폐쇄.
- **음성검증(rig-and-revert)**: 사본에서 fd 분리만 원복 → `FAIL pipe-capture-no-timeout-delay (exit=0 elapsed=31s expected=<10s)` **단독 FAIL(5/6)**, 나머지 5케이스는 여전히 전부 PASS(=기존 스위트가 이 회귀를 못 보는 구조 재확인). 원복 해제 시 6/6. **신규 가드가 load-bearing 이고 정확히 이 회귀를 잡는 유일한 케이스임을 실증.** elapsed 31s ≈ timeout 30s = 지연이 타임아웃값 종속임도 재확인.
- **타임아웃 감지 보존**: 보정 코드에서 `gate-timeout` 케이스(slow gate·timeout=1 → `분석 실패: timeout`·exit 2 승인요구) PASS = fd 분리가 타임아웃 검출을 깨지 않음.

### 판정·하류·보수적 개발
- **하류**: 킷 1차 소비경로(CI 스텝·spine 의 명령치환)가 곧 이 파이프 캡처 — 가드가 소비경로 그대로를 상설 회귀로 고정. `<10s` 임계는 정상 실행(1~2s) 대비 여유 충분, 30s 회귀와는 3배 마진으로 분리 — 플레이크 위험 낮음.
- **보수적 개발(§1) OK**: 델타 = `kit/run.sh` 1줄 + 진입점 테스트 +21줄 + 공동소유(handoff·summaries)만. 판정 조립·우선순위·`--policies`·게이트 Python·정책·dev 트리 무접촉(A-0016 "손대지 마라" 준수). scope-creep 없음.
- **비차단 O-a~O-d**: 보정 커밋에 미동봉(A-0016 이 "차기로 미뤄도 좋음" 허용) — O-d 는 MVP-2 킷 재생성 AC 로 이미 채택, O-a/O-b/O-c 는 차기 킷 정비 시 반영 권장으로 유지.
- **참고**: A-0016 의 "⚠️ 재제출 전 origin/main merge" 는 미이행 — 병합 충돌(decisions/handoff/summaries 3건)은 머지자(Claude)가 해소, 내용 결함 아님이라 비차단.

**판정**: 통과 → **TASK-022b 완결, 킷 v0(kit/) main 수용**. 민감도: 신규 `kit/` 폴더 스냅샷·기존 게이트/정책/dev 트리 무변경(D-047 비민감 판정 유지)·정산/인증·인가/암호화/migration/infra 무관 → **비민감**, 구현자(Codex 델타)≠머지자(Claude)로 Claude `main` 머지(D-007). 멱등성: `f1bf533`·`39c2285` 재처리 금지.

## TASK-022b (D-049) — 킷 최종리뷰 · **보정요청**(watcher sleep 파이프 점유 회귀) · 코드 머지 보류

**대상**: `claude/2026-07-15-kit-draft` 헤드 `88a7d4e` — 리뷰 초점 = **Codex 보강 델타 `00bde19`**(역할역전: verdict-affecting 셸을 Codex 저자, D-047·D-048·A-0015). 킷 초안 `8269dda` 는 Claude 작성이므로 스냅샷 충실성·조립 구조를 별도 검증.

**검증 방법**: 워크트리 격리 체크아웃 → ①dev↔kit 파일별 diff ②run.sh 한줄씩 정독 ③선언 수치 전부 재실행 ④fresh 적대입력 8종(Codex 5종 픽스처 밖) ⑤음성검증 2종(사보타주→테스트 FAIL 확인).

**①스냅샷 충실성 — 통과**:
- kit/gates 13종 = manifest `gates:` 명시 13종(판정6+내부추출5+온보딩2). 12/13 dev 바이트 동일.
- `extract-gov-annotations.py` 드리프트(kit=pre-sink) + `extract-sinks.py` 부재(dev 14↔kit 13)는 **manifest 선언 범위 그대로**(`version: 0.1-mvp1.5`, `reflects_mvp: [MVP-0,1,1.5]` — TASK-022=MVP-2 는 미완 마일스톤). 결함 아님, MVP-2 완료 시 `sync-from-dev.sh` 재실행으로 해소되는 구조.
- 정책 5종·템플릿 = dev 바이트 동일.
- **selftest 의 오지시 여부 확인**: 번들 테스트는 `.harness/gates` 경로를 하드코딩하지만 selftest.sh 가 임시 작업디렉토리에 `ln -s "$KIT/gates" .harness/gates` 로 심볼릭 연결 → **킷 게이트를 검증함**(dev 를 잘못 가리키지 않음). 통과 = 13종 co-located 실증(하나라도 빠지면 내부 import 붕괴로 FAIL).

**②run.sh 한줄씩 — 통과 (강등/우회 구멍 탐색 결과)**:
- 최종조립: `ge_exit=1 ∨ cap_exit=1 ∨ pol_exit=1 → 1` / `∃2 → 2` / else 0. 차단>승인>통과 ✓.
- **적대 질문 "L2 가 정당한 exit 1 을 내면 allowed='0 2' 가 차단을 강등하나?"** → `check-new-capabilities.py`·`check-policy-change.py` 소스 확인: 방출 코드 = {0, 2}뿐(BLOCKED 상수 자체가 없음). 강등할 정당한 차단이 존재하지 않음 + 불변원칙 "2·3층 자동차단 금지"를 run.sh 가 구조적으로 재보장(비정상 exit 1 은 분석실패→승인). ✓
- **intent 부재 경로**: run.sh 는 `--change-intent` 를 생략 → 게이트 기본값 `change-intent.yaml` → `load_intent` FileNotFoundError → **게이트 내부 catch-all 이 fail-closed 차단 카드(verdict: blocked, exit 1) 방출**. run.sh 출력 문구 "의도이탈 층은 생략"은 오해 소지(O-a)나 실동작은 manifest 계약("없으면 blocked")과 일치 — ADV6 fresh 입력으로 exit 1 실증.
- `--policies` 오버라이드: POL 전체 치환 + 필수 3파일 검증(부분 혼합 없음), 부재 시 분석실패 exit 2. ✓
- 카드 파일은 분석실패 시 비-YAML(O-c). `--repo` cd 이후 상대경로 기록(spine 계약 draft 라 관찰만).

**③선언 수치 재현 — 전부 일치**: selftest **77/77** + 진입점 **5/5** + mutation **127건**(+policy/metamorphic/negative/원본불변) + 브랜치 dev 스위트 **80/80**(74+3+3).

**④fresh 적대입력 (Codex 5종이 안 덮는 면)**:
| ADV | 입력 | 기대 | 결과 |
|---|---|---|---|
| 1 | 게이트를 `raise RuntimeError` 로 교체(Traceback 경로 — 5종 미커버) | 분석실패·exit 2 | ✓ `traceback` 기록 |
| 2 | 비-range(`HEAD` 단일 ref) | 능력·정책 둘 다 `range_required`·exit 2 | ✓ |
| 3 | Traceback 없는 exit 1 게이트(차단 위장) | `abnormal_exit_1`→exit 2 (차단 아님) | ✓ |
| 4 | frozen 차단 + 동시 게이트 크래시 | **차단이 이김** exit 1 | ✓ |
| 6 | intent 없는 대상 repo | fail-closed **BLOCKED** exit 1 | ✓ |
| 7 | `/bin/bash` 3.2 + intent 부재 | — | ✗ `INTENT_ARGS[@]: unbound variable` 즉사(exit 1·카드 없음) → **O-b**. intent 있으면 3.2 정상 PASS |

**🟡 R-1 (블로킹 — `00bde19` 도입 회귀)**: watcher `( sleep $T; … ) & watcher=$!` — 게이트 조기 종료 시 `kill $watcher` 는 서브셸만 죽이고 자식 `sleep` 은 상속 stdout(호출자 파이프 write end)을 쥔 채 생존 → **명령치환/CI 로그 파이프의 EOF 가 sleep 종료까지 블록**. **실측**: 기본 타임아웃 60s 에서 파이프 캡처 소요 60s(게이트 실행 1~2s), `ACGH_GATE_TIMEOUT_SECONDS=3` 에서 4s(비례 실증), watcher 에 `>/dev/null 2>&1` 부착 사본에서 **0s + 타임아웃 감지 보존**(slow-gate 재검 통과). 진입점 테스트가 전 케이스 timeout=1 로 돌아 가려짐 — **회귀가드 부재**. 판정 무영향(거버넌스 구멍 아님)이나 킷 1차 사용경로(CI 파이프) 실측 열화라 보정요청: ①1줄 fd 분리 ②큰 타임아웃값 명시한 파이프-지연 회귀가드 1건. 상세 `collab/answers/A-0016.md`.

**⑤음성검증(load-bearing)**: run.sh 사보타주 ①정규화 제거(`[ "$RUN_FAILED" = 1 ] && RUN_EXIT=2` → true) → `gate-timeout` FAIL(4/5) ②차단 우선순위 무력화(`if false`) → `target-policy-frozen` FAIL(4/5). 진입점 테스트가 두 축 모두 실제로 잡음 ✓ — "항상 PASS" 아님 증명.

**보수적 개발(§1)**: 델타 = `kit/run.sh`·`kit/selftest.sh`·`kit/tests/run-entrypoint-tests.sh`·`kit/README.md` + 문서. dev 트리·게이트 Python·정책값 무접촉. scope-creep 없음.

**하류 영향**: R-1 은 spine/CI 가 킷을 파이프로 감쌀 때(1차 사용형태) 러너 스텝당 +60s — 대상 repo CI 타임아웃·"킷 느리다" 오인 유발 가능. O-d(sync 체크섬)는 MVP-2 킷 재생성 AC 로 채택해 하류 드리프트 방지.

---

## TASK-022 R-1 재리뷰 (D-046) — 보정 재제출 **통과** · Claude main 머지 (TASK-022 완결)

**대상**: 보정 델타 `f18cc32`(+docs `95b4399`). **재리뷰 범위 = 델타만**(멱등성 — A-0013 지시). 원 구현·`extract-sinks.py`·sinks 픽스처는 D-045 에서 fresh 적대입력으로 통과 확인·재론 안 함.

**델타 내용**: `merge_gov_annotations` 2줄 이동(sink 누적을 강도병합 `if/else` 밖 top-level if 로 분리) + 신규 회귀 픽스처 `tests/fixtures/gov-annotations/multi_sink.py` + 케이스 `gov-annotations-multi-sink-metadata`(harness 신규 단언 `annotation_metadata`) + 공동소유.

**R-1(D-045) 해소 — 한 줄씩 확인**:
```python
        if annotation.get("sink"):          # top-level if — 매 iteration 독립, sink 멤버십 정확성 유지
            merged["sink"] = True
        if annotation_is_stronger:          # 강도병합 (원래대로)
            ...
        else:                               # ← 이제 annotation_is_stronger 에 재결합 (backfill 복원)
            if annotation["reason"] and not merged["reason"]: merged["reason"] = annotation["reason"]
            if annotation["owner"] and not merged["owner"]:   merged["owner"] = annotation["owner"]
```
A-0013 요청 보정 ①(제어흐름 분리)·②(상설 회귀 픽스처) **정확히 이행**. sink 여부와 backfill 여부의 오결합 제거 → 약한 `sink=true` annotation 의 reason/owner 유실 폐쇄.

**적대 검증(무발견≠통과 — 능동적으로 깨봄)**:
- **전체 스위트 80/80 PASS**(머지 후 트리 재실행도 80/80).
- **음성검증(rig-and-revert)**: 픽스를 버그형태(sink 블록을 `if/else` 사이로 원복)로 되돌림 → `gov-annotations-multi-sink-metadata` **단독 FAIL(79/80)**, 게이트 픽스처 출력 `{reason:None, owner:None, sink:True}` = 원 R-1 결함 정확 재현. **신규 회귀 픽스처가 오결합을 잡는 load-bearing 실증**(항상-PASS 아님).
- **fresh 적대입력 3종(픽스처 밖, gate 직접 실행)**:
  - **ADV1**(3중 @gov, 최약 annotation 에만 `sink=true`+reason/owner) → `{level:frozen, reason:'export PII', owner:'sec-team', sink:True}` — 원 R-1 시나리오를 3-데코레이터로 확장했으나 전부 보존.
  - **ADV2**(최강 frozen 에 `sink=true`·reason 무, 약한 protected 에 reason/owner) → `{reason:'weak reason', owner:'weak-owner', sink:True}` — backfill 경로 정상.
  - **ADV3**(sink 전무 — 하위호환) → `{reason:'r', owner:'o', sink:False}` — 비-sink 경로 행동보존 무회귀.
- **하류 영향(§2B)**: 유실되던 owner(§5 라우팅 대상)·reason(감사카드)이 다중-@gov 에서 보존 → TASK-024 라우팅 fail-safe(tool_owner) 강등 구멍 폐쇄 확인.
- **harness 단언 vacuous 아님 확인**: `annotation_metadata` 검증은 name 매칭 dict 비교라 name 불일치/누락 시 `{}` vs 기대 → FAIL. 버그형태에서 실제 FAIL 로 실증.

**보수적 개발(§1)**: 델타 파일 경계 준수 — `policies/*`·Claude 소유·`extract-sinks.py`·sinks 픽스처 무접촉. 요청한 보정만 정확히. scope-creep/over-reach 없음.

**잔여(비차단·보정 불요)**: R-2(frozen-auto-sink 테스트의 라이브 `policies/sensitive-zones.yaml` 결합) → Codex 가 **TASK-023 G-sink-1 이월**(A-0013 허용). loud-fail·구멍 아님. **TASK-023 착수 시 G-sink-1 로 결정적 고정 처리 잊지 말 것.** O-1(이중 sink)·O-2(bool hops)는 TASK-024 AC 고려/인지.

**판정**: 통과·비민감 → Claude `main` 머지·push. **TASK-022 완결 → 다음 TASK-023.** 멱등성 `f18cc32`·`95b4399` 재처리 금지.

---

## TASK-022 (D-045) — sink 등록 스키마 · **보정요청**(@gov 병합 else 오결합) · 코드 머지 보류

**대상**: `codex/2026-07-15-task022-sink-registry` — 구현 `4651ea6`·헤드 `44380c0`. 신규 게이트 `extract-sinks.py` + `extract-gov-annotations.py` sink 파싱 확장 + `tests/fixtures/sinks/`. **MVP-2 첫 게이트(등록·판정무변경)** — 설계 §3.1(D-044).

**의도한 위험 (무엇을 잡아야 하나)**: 이 게이트는 판정을 안 한다 — 다음 층(TASK-023 콜그래프·TASK-024 역도달성)의 **입력(sink 목록·라우팅 메타)** 을 결정적으로 산출한다. 그러므로 리뷰 초점 = ① sink **멤버십**(옵트인/frozen 자동/registry, 비-sink 제외)이 설계 레벨차등(D-044a)과 정확히 일치하나, ② 하위호환 무회귀(기존 @gov 동작 불변), ③ 하류가 소비할 **메타(owner=라우팅·reason=감사·maturity=성숙도)** 가 정확·결정적인가.

**통과 (fresh 적대입력 실증)**: `run-tests.sh` 79/79.
- **멤버십 정확**: fixture `download_report`(@gov sink=True)→`gov:` sink / `direct_only`(@gov sink 미지정)→비발화 / `services/settlement/*`(frozen)→`frozen:` sink / `services/auth/login`(protected)→비발화. 설계 레벨차등 그대로.
- **하위호환 무회귀(실증)**: sink 미지정 annotation 은 `sink=False`. 비-sink 경로에서 병합은 행동보존 — stronger-branch 가 truthy reason/owner 를 먼저 채우고 backfill 은 empty 시에만 → 오결합 else 가 항상 실행돼도 non-sink 결과 동일(그래서 기존 테스트 무회귀·아래 결함은 sink 경로에만 발화).
- **registry 스키마(§3.1)**: missing 필드→`missing_required_field`, 미해소 function→`unresolved_registry_function`+드롭(**조용한 무시 아님**), invalid maturity→`invalid_maturity`+**enforcing 보수**, 빈/부재→정상. exit 0(추출기·판정없음)이나 오류는 `errors[]` 로 노출(조용한 green 아님).
- **결정성**: `os.walk` 정렬·`unique_sorted_sinks` 키정렬·오류 json-키정렬·`deterministic_stdout` 2회 동치.
- **보수적 개발**: 신규 게이트+gov-gate 확장(AC #1 인가)+`tests/*`+README+공동소유만. `policies/*`·Claude 소유 무접촉.

**🟠 R-1 결함 (블로킹) — else 오결합으로 sink owner/reason 유실**: `merge_gov_annotations` 에서 sink 블록이 기존 `if annotation_is_stronger: … else: …` **사이에 삽입**돼 `else` 가 `if annotation.get("sink")` 에 결합. → sink=True 인 **약한** annotation 의 reason/owner backfill 스킵. **적대 실증(픽스처 밖·다중 @gov 데코레이터)**: `@gov(level=frozen)` + `@gov(level=protected, reason="PII export", owner="security-reviewer", sink=true)` → 헤드 출력 `reason=None owner=None sink=True`. **음성검증(rig-and-revert)**: sink 라인을 if/else 밖으로 분리해 else 를 `annotation_is_stronger` 로 원복 → `reason="PII export" owner="security-reviewer"` 복원 = 오결합이 결함(우연 아님). **§2B 필수질문**: sink 멤버십은 항상 정확(top-level if)이라 누락/오탐 없음. 그러나 유실 `owner` 는 §5 라우팅 대상·`reason` 은 감사카드 필드 → 라우팅 fail-safe 강등 = 거버넌스 메타 손실. 명백한 제어흐름 버그(논리 비정합) → 비차단 불가. + §2B 상설 적대세트(데코레이터/오버로드) 범주인데 회귀 픽스처 없음. → **보정: sink 설정을 if/else 밖으로 분리 + 다중-@gov 회귀 픽스처 신설**(A-0013 R-1).

**🟡 R-2 (비차단·권장)**: `sink-registration-defaults` 가 `--sensitive-zones` 기본값(라이브 `policies/sensitive-zones.yaml`)에 결합 → frozen 자동 sink 기대값이 라이브 정책 settlement frozen 유지에 의존. **실증**: 대체 zones(auth=frozen) 주입 → frozen sink 가 `services.auth.login` 로 뒤바뀜(기대 셋이 fixture 아닌 라이브에서 나옴). TASK-021 G-broad-1(D-042/D-043) 이 닫은 라이브결합 부류 — loud-fail 이라 비차단. **권장**: fixture-local `sensitive-zones.yaml` 로 결합 끊기(또는 TASK-023 fixture 가드 G-sink-1 이월).

**비차단 관찰**: O-1 frozen+@gov(sink) 동시 = `gov:`·`frozen:` 이중 sink(maturity shadow vs enforcing) → TASK-024 강한 maturity 채택 고려. O-2 `normalize_hops` `isinstance(int)` 는 bool 통과(`hops:true`→1) 무해.

**머지(D-007)**: **보류** — R-1 은 논리결함이라 코드 브랜치 머지 보류, 리뷰기록(A-0013·decisions·review-notes·handoff)만 main 머지. 재제출은 보정 델타만 재리뷰(멱등성 `4651ea6`·`44380c0` 재처리 금지).

---

## TASK-021 G-broad-1 (D-043) — broad-intent 픽스처 라이브-repo 결합 제거 · 통과 · Claude main 머지

**대상**: `codex/2026-07-13-task021-broad-fixture` — `2395c6e`(test) · 헤드 `82d598b`(docs). 범위 = **테스트 하네스만**(D-042 비차단 차기 AC 가드 G-broad-1). 게이트 판단 로직·정책 무접촉(0-diff 확인).

**의도한 위험 (왜 이 follow-up 인가)**: D-042 에서 남긴 R-2/G-broad-1 — `broad-intent-coverage` 회귀가 라이브 repo 최상위 디렉토리 수(당시 8)에 결합돼 있어, repo 에 디렉토리가 하나 추가되면 7/8=87% → 7/9=77%<80 으로 뒤집혀 **회귀 테스트가 조용히 pass 로 깨질** 위험. 프로덕션(실 diff ref)은 결정적이라 구멍은 아니었지만 상설 회귀가 불안정.

**무엇을 잡는가 (설계 정합)**: 게이트 `repo_top_level_dirs()` 는 `git ls-tree -d <base_ref>` 를 **cwd 기준** 실행. 신규 하네스는 `fixture_dir` 케이스를 `prepare_function_mapping_fixture`(기존 헬퍼 재사용)로 **격리 git repo** 를 만들어 `cd work_dir` 안에서 `base..head` 로 게이트 실행 → **분모가 픽스처 base 트리(고정 8)에서 나온다.** 라이브 repo 변화에 불변. 실 CI 의 git-diff 경로를 그대로 태우므로 예전 name-status 파일(파일존재→HEAD 폴백=라이브트리) 대비 프로덕션 충실도도 향상.

**적대 검증(fresh·픽스처 밖)**: coverage 픽스처 repo 손수 빌드→게이트 실행: `top_level_dir_count:8`(셋에 **`app` 포함**·라이브엔 `app` 없음/`tests` 있음)·`coverage_percent:87`·`threshold:80`·exit 2·`changed_files:['docs/release-notes.md']`. 분모 dir 셋이 픽스처에서 나옴 실증 = **결합 소멸.** coverage 픽스처는 R-1 공격값 `broad_scope_threshold_percent:101`+중첩 보존 → R-1 회귀도 상설 유지.

**음성검증(rig-and-revert)**: `scope_coverage_percent` 87→88 → `broad-intent-coverage` 단독 FAIL / `scope_covered_top_level_dirs` `templates`→`BOGUS` → `broad-intent-root` 단독 FAIL / 원복 PASS = 신규 단언 load-bearing. 단언이 분자(covered)+분모(count)+percent 를 함께 고정 → 예전보다 엄격.

**보수적 개발**: `run-tests.sh`(fixture_dir 분기+검증 단언)·`cases.yaml`·신규 픽스처 트리·공동 handoff/summaries 만. 무관 리팩터/scope-creep 없음·헬퍼 재사용·Claude 소유 0-diff.

**비차단(O-1·신규)**: `tests/fixtures/broad-intent-*/name-status.txt` 3파일 이제 미참조(dead). 무해·구멍 아님 → 차기 정리 삭제 권장(보정 필수 아님).

**머지(D-007)**: CI 테스트-하네스 안정화·비민감 → 구현자(Codex)≠머지자(Claude) → Claude main 머지. G-broad-1 마감.

### 검증 로그 (D-043)
`bash tests/run-tests.sh` **77/77 PASS**(default 71·metamorphic 3·negative 3) · `git diff --check` clean · `py_compile`·`bash -n` OK — 격리 worktree 재현. fresh 결합-소멸 실증 1종 + 음성검증 2종 직접 실행. 게이트/정책 0-diff 확인.

---

## TASK-021 R-1 재리뷰 (D-042) — 보정 재제출 · 통과 · Claude main 머지

**대상**: `codex/2026-07-11-task021-broad-intent` — 보정 `1c08afa` · 헤드 `c4655ad`. 멱등성: 검출 엔진(`616ff43`/`1b954c3`)은 D-041/A-0012 에서 실증 통과 — **R-1 보정 델타만** 재리뷰.

**보정 델타 (한 줄 확인)**
```python
# 이전 (자기-무력화):
#   "broad_scope_threshold_percent": int(
#       intent.get("broad_scope_threshold_percent")
#       or intent.get("scope_policy", {}).get("broad_scope_threshold_percent")
#       or DEFAULT_BROAD_SCOPE_THRESHOLD_PERCENT),
# 보정 후 (line 61):
    "broad_scope_threshold_percent": DEFAULT_BROAD_SCOPE_THRESHOLD_PERCENT,
```
→ **권장 보정(오버라이드 제거)** 채택. author 가 임계값을 통제하던 두 조회 키를 모두 제거. `grep` 으로 threshold 세팅점이 line 61(상수 80) **유일**하고 소비점(164·180·190)이 전부 이 상수 참조임을 확인 → 신뢰경계 복구(author→상수).

**적대 재검증 (fresh·픽스처 밖·라이브트리 결합 차단)**
D-041 의 ADV1 을 **합성 8-디렉토리 git repo** 에서 재현(라이브 repo 트리 의존 제거):
```
change_intent: broad_scope_threshold_percent: 101 + scope_policy.…: 101
allowed_paths: 8개 최상위 디렉토리 개별 나열(리터럴 */** 회피)
→ threshold 80 (공격값 101 무시) · coverage 100% · reasons [top_level_coverage]
→ verdict approval_required · exit 2   ✅ 공격 차단
```
자기-무력화 스위치(임계값 오버라이드)가 사라져 공격이 더는 통하지 않음.

**음성검증 (rig-and-revert — 델타가 load-bearing 임을 증명)**
line 61 을 예전 author-통제 코드로 되돌린 rigged 사본에 **동일 공격 입력** →
```
→ threshold 101 · reasons [] · verdict pass · exit 0   ← 구멍 재개방
```
= 이 한 줄이 R-1 을 닫는 유일·load-bearing 변경. 항상-PASS 아님 실증.

**회귀 고정 · 무회귀**
`broad-intent-coverage` 픽스처에 공격 선언값 `101`(+중첩 `scope_policy`)을 심어 상설 회귀가 R-1 입력을 그대로 담음(threshold 무시·`approval_required` 기대). `tests/run-tests.sh` **77/77 PASS**(default 71·metamorphic 3·negative 3) · `py_compile` OK · `git diff --check` OK.

**보수적 개발**
보정 델타 = 게이트 1줄 + 픽스처 3줄 + 공동소유(handoff·summaries). `policies/*`·Claude 소유 무접촉·scope-creep 없음.

**비차단 관찰 (O-1, R-2 잔존) → 차기 AC 가드 G-broad-1**
회귀 픽스처가 여전히 라이브 repo 트리에 결합(name-status 파일 입력 → `diff_base_ref` HEAD 폴백 → `repo_top_level_dirs` 가 실 repo `git ls-tree -d HEAD` 를 셈). 현재 8 top-level dir, 픽스처 7개 나열=87%≥80 통과. 최상위 디렉토리 1개 추가 시 7/9=77%<80 → verdict pass 로 뒤집혀 **무관한 repo 성장에 이 회귀가 깨짐**. 프로덕션(실 diff ref 입력)은 base ref 로 결정적 → **거버넌스 구멍 아님·비차단**. 픽스처가 top-level dir 집합을 합성 base 트리 등으로 결정적 고정하도록 **차기 AC 가드**로 명시(보정 필수 아님). root-glob 케이스는 커버리지 무관해 안정적.

**판정**: R-1 해소 ✓ · 통과 · 비민감(2층 approval 격상만·1층 차단 권한 없음·정산/인증/암호화/migration/infra 무관·게이트 계열 Claude 머지 선례) → **Claude main 머지**. → `collab/decisions.md` D-042.

---

## TASK-021 (D-041) 광역 의도선언 격상 `check-change-intent` — 보정요청 (1건 · 🔴)

**대상**: `codex/2026-07-11-task021-broad-intent` · impl `616ff43` · 헤드 `1b954c3`. `check-change-intent.py` +109줄, `tests/cases.yaml` 3케이스, 러너 assert, 픽스처 3종.

**의도 대비 검수 (거수기 금지 — 능동적으로 깨보려 함)**
이 태스크의 거버넌스 목적 = "`allowed_paths:["**"]` 류로 의도 게이트를 **무력화**하는 것을 막는다". 따라서 핵심 질문은 **"작성자가 이 방어를 다시 무력화할 수 있는가"**. 코드를 읽는 데 그치지 않고 픽스처 밖 fresh 입력으로 **실제 게이트를 돌려 깨보려** 했다.

### 한 줄씩 뜯어본 로직
- `normalize_scope_glob`/`root_scope_globs`: `PurePosixPath` 정규화 + `strip("/")` 후 `{"*","**"}` 동치 검사. `**`·`*`·`./**`·`**/` 전부 동치로 잡음. `**/**`·`**/*` 는 root-glob 은 아니나 커버리지 경로가 포착(아래).
- `repo_top_level_dirs`: `git ls-tree -d --name-only <base_ref>` 로 최상위 **디렉토리**만. base_ref 는 `diff_base_ref`(ref 의 `...`/`..` 앞 토큰, 파일입력이면 HEAD). 실패 시 변경파일 디렉토리로 폴백.
- `covered_top_level_dirs`: 각 top-level dir 을 dir 자체 또는 `dir/__scope_probe__` 로 매칭 → `app/*`·`app/**` 류가 dir 을 덮는지 판정(probe 로 `app/*` 형도 커버 인정). 커버리지% = covered/total(정수 나눗셈).
- 격상: `too_broad = root_glob 존재 OR 커버리지 ≥ 임계값`. `check_files` 에서 **forbidden(blocked) 우선 → out_of_scope OR too_broad → approval_required**. too_broad 는 절대 blocked 로 안 감(AC#3).

### 적대적 검증 (fresh 입력·픽스처 밖·실제 게이트)
- **ADV2 (커버리지 검출 정상)**: 최상위 8개 전부 개별 `dir/**` 나열, 임계값 미지정(기본 80) → `coverage 100`·`top_level_coverage`·`approval_required`. 엔진 정상.
- **ADV3 (root-glob 임계값 독립)**: `["**"]` + `broad_scope_threshold_percent:101` → `root_scope_glob`·`approval_required`. AC#1(a) 는 임계값과 무관하게 발화. ✅
- **ADV1 (🔴 자기-무력화 재현)**: 최상위 8개 개별 나열(리터럴 `*`/`**` 회피) + **같은 파일에 `broad_scope_threshold_percent:101`** → `coverage 100`·`root_globs []`·**`too_broad false` → `pass`/exit 0**. 사실상 무제한 선언이 AC#1(b) 를 완전 회피. ⇒ **결함**.
- **음성검증(rig-and-revert)**: ADV1 선언에서 `broad_scope_threshold_percent` 한 줄만 제거 → `top_level_coverage`·`approval_required`/exit 2 로 뒤집힘. ⇒ 회피 스위치 = **임계값 오버라이드 그 자체**(가드가 load-bearing 함을 역으로 증명).

### 결함 R-1 (🔴) — 임계값 N 의 신뢰경계 오배치
`load_intent` 는 N 을 `intent.get("broad_scope_threshold_percent") or intent.get("scope_policy",{}).get(...) or 80` 으로 읽는데 `intent = data.get("change_intent")` — **피검자(author) 소유 선언**이다. 외부 정책파일 경로 부재·상한 클램프 부재. AC#1(b) "N 은 정책값"(= 거버넌스 소유: Claude `policies/*` 또는 고정)과 정면 충돌 + 위 실증대로 자기-무력화. **§2B 필수질문**("거버넌스 목적에 직접 구멍?") → 예 → 비차단 금지 → **보정요청**.
보정 방향: (권장) 오버라이드 제거·고정 기본 80 / 또는 Claude 소유 정책에서 읽기. **클램프 ≤100 만으론 불충분**(threshold=100+7/8 나열=87%<100 통과).

### 하류 영향
`scope_too_broad` 는 감사카드/후속 라우팅에 `reasons`·`coverage_percent`·`covered_top_level_dirs` 를 노출 → approval-routing 이 이 신호를 근거로 쓸 때, author 가 임계값을 올려 신호 자체를 지우면 하류 전 계층이 광역성을 못 본다. R-1 은 이 게이트 하나가 아니라 하류 승인체계 전체의 근거를 무력화한다.

### 비차단 관찰 R-2 (🟡 · 차기 AC / 보정 시 동봉 권장)
회귀 픽스처가 라이브 repo 트리에 결합. name-status 파일 입력 → `diff_base_ref` HEAD 폴백 → `repo_top_level_dirs` 가 실 repo 최상위 디렉토리(현재 8개)를 셈. `broad-intent-coverage`(7개 나열) 판정 = fixture 아닌 실 repo 구조 의존: 지금 7/8=87% 통과지만 최상위 디렉토리 1개 추가 시 7/9=77%<80 → `pass` 로 뒤집혀 **무관한 repo 성장에 회귀 테스트가 깨짐**(상설 회귀 픽스처 원칙 위배). 프로덕션(실 diff ref)은 base ref 로 결정적 → 거버넌스 구멍 아님 → 비차단. 픽스처가 top-level dir 집합을 결정적으로 고정하도록 권장. (`broad-intent-root` 는 root-glob 이라 커버리지 무관·안정.)

### 부차 (보정 불요)
- 비정수 임계값 → `int()` 예외 → `except`→ blocked(exit 1). 광역 판정이 차단으로 흐르는 소지지만 정상 운용 밖 입력.
- `broad_scope_threshold_percent:0` 은 falsy → `or` 사슬서 기본 80 취급(0 설정 불가). 안전 방향.

### 검증 로그
`git worktree` 상 `bash tests/run-tests.sh` → **77/77 PASS**(default 71·metamorphic 3·negative 3). ADV1/2/3 는 브랜치 게이트를 scratchpad 사본으로 직접 실행해 재현.

---

## TASK-017 (D-040) 뮤테이션(음성검증) 자동화 `tests/mutation-check.sh` — 통과

**대상**: `codex/2026-07-11-task017-mutation-check` · impl `459a519` · 핸드오프 `4bd00c0`. 신규 `tests/mutation-check.sh` + `run-tests.sh` 선택실행/그룹요약/`capability_ids`·`capability_levels` assert + cases 6종 + 픽스처 8 + README 1줄.

**의도 대비 검수 (거수기 금지 — 능동적으로 깨보려 함)**
이 태스크의 거버넌스 목적 = "40/40 PASS 가 *시험이 죽어서* 나온 게 아님을 매 CI 자동 보증". 따라서 핵심 질문은 **"이 하네스가 진짜 죽은 테스트를 잡는가, 아니면 자기 자신도 항상-green 인가"**. 코드를 읽는 걸로 끝내지 않고 하네스를 *변조해서 뒤집어* 봤다.

### 한 줄씩 뜯어본 로직
- `check_expectation_mutations`: 케이스별로 `original_cases` 를 매 반복마다 yaml 라운드트립으로 새로 떠서(변조 누적 없음·결정적) index 위치의 `verdict`/`exit_code` 를 mutator 로 바꿔 쓰고 → `TEST_CASE_NAME=case명` 으로 **그 케이스만** 선택 실행 → returncode 0 이면(=변조했는데 PASS) dead 로 수집. 끝에 원본 복원.
- `mutate_verdict`: pass→blocked, blocked→pass, approval_required→pass, 그 외→pass. `mutate_exit_code`: 0→2, 비0→0. 두 경우 다 원본과 반드시 다른 값 산출 → 변조가 실질적.
- `check_policy_mutation`: maturity fixture `app/enforcing/**` zone 을 protected→watched(+required_approval=None) 로 낮춰 `maturity-zone-enforcing-approval` 이 FAIL 하는지 → 정책이 판정을 지배함 증명. 원본 복원.
- `run-tests.sh`: `TEST_CASE_NAME`(콤마분리 다중)·`TEST_CASE_GROUP` 선택, 미선택시 `FAIL no test cases selected`, group 요약 출력, `capability_ids`/`capability_levels` 신규 assert. env 없으면 전체 스위트(하위호환).

### 적대적 검증 (직접 실행)
- **정상 실행**: `bash tests/mutation-check.sh` → `Expectation mutations checked: 121` · dead 0 · Policy mutation 감지 · Metamorphic/Negative PASS · Original files unchanged PASS · `PASS mutation-check` (exit 0). 전체 스위트 `74/74 PASS`(default 68·metamorphic 3·negative 3).
- **음성검증 ① (verdict mutator no-op rig)**: `mutate_verdict` 를 `return value` 로 변조 → verdict 보유 48케이스 전부 `dead expectation mutations` 로 열거·`FAIL mutation-check`. ⇒ 변조가 실질적으로 판정을 뒤집어야만 PASS 가 나옴을 증명(하네스 load-bearing). 원복 후 정상.
- **음성검증 ② (exit_code mutator no-op rig)**: `mutate_exit_code` 를 `return value` 로 변조 → **exit 1** · `good:exit` 등 dead 보고 · FAIL. 원복.
- ⇒ 두 필드 검출 루프 모두 진짜로 죽은 테스트를 잡는다. "돌아갈 것 같다" 아닌 "깨보려 했으나(=변조) 정상 FAIL 로 반응".
- **AC#5 정책변조 load-bearing**: 실행 로그 "maturity-zone-enforcing-approval failed after protected->watched policy mutation" = zone 하향이 실제로 판정을 approval_required→pass 로 바꿔 케이스가 깨짐. 원본 복원 확인(`Original files unchanged` — 단 O-1 참조).
- **metamorphic 실증(픽스처 밖 개념검증)**: 세 변형(별칭 `subprocess as sp`→`sp.run` / 공백·주석 / helper 선행 순서)이 전부 `subprocess_exec/protected` 동일 → 별칭해소·공백무시·정의순서독립 실제 확인. 요구 (a)(b)(c) 정확 대응.

### 하류 영향·설계 정합
- 케이스명 **74/74 유니크** 확인 → mutation-check 가 index 로 변조하고 name 으로 선택하는 정렬이 안전(중복명이면 다른 케이스 선택·오분류 위험이나 부재). 차기에 케이스 추가 시 유니크 유지가 암묵 계약 → negative(중복명) 발생 시 자동 노출됨(선택 실행이 여러 케이스 돌려 conservative FAIL).
- metamorphic 케이스의 `capability_ids`/`capability_levels` 는 mutation-check 변조 대상이 **아님**(AC#3 "최소 verdict·exit_code" 범위). 그러나 값이 비공허(`[subprocess_exec]`/`[protected]`)로 pin 되고 정상 러너 `assert_equal` 로 검증되므로 공허한 assert 아님. exit_code:0 변조는 121건에 포함되어 각 metamorphic 케이스가 "실제로 무언가 검사함"도 보장.

### 보수적 개발(§1)
순수 테스트 하네스·픽스처·README 실행예시 1줄. **정책(`policies/*`)·게이트(`.harness/gates/*`)·Claude 소유(docs·TASKS·decisions·answers·templates·CLAUDE.md) 전부 무접촉** (`git diff --name-only` 로 확인). scope-creep/over-reach 없음. blast radius = 테스트 계층에 한정.

### 비차단 관찰 (O-1 · MVP-2 / 차기 AC 가드 후보)
`main()` 의 `restore_ok = before_hashes == after_hashes` 는 `file_sha` 가 `ROOT`(실제 repo)를 읽어 계산 → 그러나 모든 변조는 `tempfile` 복사본(`repo`)에서만 일어나 ROOT 는 **구조적으로 절대 기록되지 않음**. 따라서 "Original files unchanged: PASS" 는 **항상 참(공허)** 이고 in-repo 복원 실패를 검출할 수 없다. **거버넌스 구멍 아님**: 실제 repo 안전은 copy 설계가 restore-and-verify 보다 *강하게* 보장(원본이 애초에 안 만져짐). in-repo 복원이 실패해도 후속 policy/metamorphic/negative 체크가 스퓨리어스 FAIL 로 간접 노출 → false-pass 위험도 없음. **차기 개선(강요 아님)**: 복원 검증을 원하면 temp-copy 파일 해시를 검사하거나 오해 소지 라인 제거. §2B "거버넌스 직접구멍" 아니므로 비차단 정당.

### 검증 로그
- `bash tests/run-tests.sh` → 74/74 PASS (Group default 68/68·metamorphic 3/3·negative-corpus 3/3)
- `bash tests/mutation-check.sh` → 121 변조 감지·dead 0·정책변조 감지·PASS (약 90s)
- rig ①(verdict no-op) → 48 dead·FAIL / rig ②(exit_code no-op) → exit 1·FAIL / 각 원복 후 PASS
- 케이스명 유니크 74/74 · `git diff --name-only origin/main` = 게이트/정책/Claude소유 무접촉

---

## TASK-016 동적 위험접근 감지 보강 `extract-python-capabilities.py` — **보정요청** (2026-07-11, D-038)

> 대상: `codex/2026-07-11-task016-dynamic-capabilities` (impl `6aeb513`·핸드오프 `47db5c5`). 목적: `getattr(os,name)`·`__import__(name)` 등 정적 호출명으로 해소 안 되는 **동적 민감모듈 접근**을 완전 통과시키지 않고 저확신 `watched` 로 남긴다.

**무엇을 검증했나** — ① 비리터럴 동적접근이 watched 로 잡히나, ② 리터럴/조립은 정확 매칭으로 접나(AC#6 상수접기), ③ 일반객체 동적접근은 무신호인가(AC#2 오탐억제), ④ 동적 신호가 절대 protected 로 승격 안 하나(AC#3 상한), ⑤ **그리고 이 출력을 하류 `check-new-capabilities` 가 어떻게 쓰나(하류 영향)**.

**한 줄씩 읽은 결과(핵심 로직)**
- `fold_string(node)`: `Constant(str)` 또는 `BinOp(Add)` 좌우 재귀 접기만. 값실행·변수해소 없음 → 결정적(`:206-214`). `getattr`/`__import__` 인자에 공용 적용.
- `maybe_record_dynamic_access`: `getattr`/`setattr` 대상 base 를 `resolve_dotted_name`(별칭 bindings 해소, 미바인딩은 이름 그대로) → attr 이 fold 실패(비리터럴)면 `caps_for_catalog_module(base)` 로 **watched** 신호(`level="watched"` 명시). base 가 민감모듈이 아니면 매칭 없음 = 오탐억제.
- `strongest_level`: `LEVEL_STRENGTH{watched:0, protected:1}` 로 능력별 level 을 **강한 쪽으로 병합**. 동적 watched 는 기존 정적 protected 를 강등 못하고, 자기 혼자면 watched 상한(AC#3 준수).
- `__import__` 를 generic builtin 경로(`IMPORT_BUILTINS`)에서 제외 → 비리터럴 `__import__` 가 protected(카탈로그 builtin level)로 새지 않고 dynamic 핸들러의 watched 로만 감(정합).

**적대 검증(fresh, 픽스처 밖 — 실제/테스트 정책)**
| 입력 | 결과 | 판정 |
|---|---|---|
| `getattr(os,"sy"+"stem")()` | `subprocess_exec` **protected** | AC#6 상수접기 정확 ✅ |
| `getattr(self,name)` | 무신호 | AC#2 오탐억제 ✅ |
| `getattr(os,name)` | `subprocess_exec` **watched** | AC#1 ✅ |
| `import os as _o; getattr(_o,name)` | `subprocess_exec` **watched** | 별칭 해소 ✅ |
| `getattr(osmod,name)` (미바인딩) | 무신호 | 오탐억제 ✅ |
| `__import__(name)` | `dynamic_code_exec` **watched** | AC#7 ✅ |
| `__import__("sub"+"process")` | `dynamic_code_exec`+`subprocess_exec` **protected** | 접기+import 정확 ✅ |

- **음성검증**: `cases.yaml` 의 `python-capabilities-dynamic-watched` 기대 level 을 watched→protected 변조 → 해당 케이스 **단독 FAIL(66/67)**, 원복 67/67 = 픽스처 load-bearing 실증.

**🔴 하류 영향에서 결함 발견 (R-1, 보정사유)** — CLAUDE.md §2B "이 출력을 다음 태스크가 어떻게 쓰나" 를 따진 결과:
- `check-new-capabilities` 신규탐지 = `set(head_caps) - set(base_caps)` (**id 만**, level 무시). TASK-016 전엔 능력 level 이 id 별 상수(protected)라 이 전제가 안전했으나, TASK-016 이 같은 id 를 **watched 로도** 표면화하면서 전제가 깨졌다.
- **실증(fresh, 실제 `policies/sensitive-capabilities.yaml`)**: base=`getattr(os,name)`(동적→`subprocess_exec` watched) → head 에 `os.system(cmd)`(신규 실제 RCE→protected) 추가.
  - **main(TASK-016 이전)**: `subprocess_exec` 가 base 에 없음 → 신규 → `approval_required`·**exit 2**. 포착 ✅
  - **본 브랜치**: `subprocess_exec` id 가 base 에 이미(watched) → 신규 아님 → `pass`·**exit 0**. **은닉 — 경고조차 없음** ❌
- = 개선 아닌 **순수 퇴행**. 동적 디스패처(`getattr(os,name)`)는 base 상주 현실적이고 그 뒤 실제 `os.system` 추가가 조용히 미탐. 거버넌스 직접 구멍 → **비차단 불가**.
- **보정 계약(Codex, `check-new-capabilities.py` 만)**: 공유 id 의 **level 에스컬레이션(watched→protected)** 을 신규/승격으로 잡아 `approval_required`. 상설 회귀 픽스처(위 세트, 기대 exit2) + 음성검증(가드 제거 시 pass 로 뒤집힘). 추출기·정책 무접촉.

**보수적 개발(§1)** — 추출기 델타(+143)는 무관 리팩터·scope-creep 없이 깨끗. 반려는 순전히 하류 정합 1건. AC#8 은 Claude 가 정책소유자로 `main` 반영(Q-0003 응답, A-0011).

---

## TASK-016 R-1 보정 재제출 재리뷰 — 하류 회귀 해소 · **통과·머지완료** (2026-07-11, D-039)

> 대상: `codex/2026-07-11-task016-dynamic-capabilities` (보정 fix `e839fe9`·헤드 `dec42e9`). 선행 D-038/A-0011 의 R-1(동적 watched 가 신규 protected 정적호출 은닉) 보정. **R-1 델타만** 재리뷰(멱등성: `6aeb513`·`47db5c5`·`e839fe9`·`dec42e9` 재처리 금지). 추출기 AC#1~7 은 D-038 통과 확정·재론 없음.

**무엇을 검증했나** — ① 보정이 R-1 실증(base 동적 watched + head 신규 protected 정적호출)을 실제로 막나, ② 파일 내 동일 id 집계 전제(strongest_level)가 보정을 떠받치나, ③ 완화 아닌 방향(de-escalation)을 과탐하지 않나, ④ 가드가 load-bearing 인가(음성검증), ⑤ 스코프·정합.

**한 줄씩 — 보정 로직(`check-new-capabilities.py` +22줄)**
- `LEVEL_STRENGTH = capability_gate.LEVEL_STRENGTH` — 추출기와 **동일 상수 재사용**(`{watched:0,protected:1}`)으로 순서 불일치 원천 차단. 계약 정합.
- `escalated_capability_record(...)` = `new_capability_record` 위에 `base_level`·`change:level_escalation` 부착 — 기존 record 스키마 재사용(중복 로직 없음).
- 신규 루프 `for cap_id in sorted(set(head_caps) & set(base_caps))`: `head_level` 강도 `>` `base_level` 일 때만 record 생성, 그 외 `continue`. protected → `new_capabilities`(approval), shadow maturity → `shadow_capabilities`(무영향), (도달불가) watched → warned. **결정성**: `sorted(...)` + 말미 `sort_capability_records`.

**설계 정합 — 왜 보정이 성립하나(집계가 load-bearing)**: `capability_index` 는 `{id: capability}` 단일 매핑이라 원래 "id 1개⇒level 1개" 붕괴가 R-1 사유였다. 그러나 추출기 `extract_from_source` 의 `found=defaultdict(...)` + `add_signal`→`strongest_level`(extract-python-capabilities.py:131~141)이 **파일 내 동일 id 를 최강 level·신호병합 단일 record 로 집계**한다. 따라서 head 에 watched `getattr(os,name)` + protected `os.system` 공존 시 `head_caps[subprocess_exec].level = protected` 로 확정 → 에스컬레이션 루프가 정확히 포착. (id 는 base 에 이미 있어 `head-base` 신규루프엔 안 잡히므로 이 루프가 유일 포착 지점 = 정확.)

**적대 검증 (fresh·픽스처 밖·실제 `policies/sensitive-capabilities.yaml`, 신규 git repo)**
- **R-1 핵심**: base `def f(name): getattr(os,name)`(watched) → head 에 `def g(cmd): os.system(cmd)` 추가 → 브랜치 게이트 `approval_required`/**exit 2**, `new_capabilities=[{id:subprocess_exec, level:protected, base_level:watched, change:level_escalation, signals:[dynamic_access@5, call os.system@9]}]`. R-1 실증 정확 폐쇄.
- **참고(main 대조)**: main 게이트는 추출기가 `getattr` 를 동적 감지 못 해 base 에 subprocess_exec 부재 → head `os.system` 을 **신규 id** 로 잡음(exit 2). 회귀는 **TASK-016 추출기가 base 에 watched subprocess_exec 를 넣은 뒤**에만 발생 = 순수 하류 통합 결함이었음을 재확인.
- **de-escalation 무과탐**: base protected `os.system` → head 동적 watched `getattr` 단독 → `head(0)≤base(1)` skip → **pass/exit 0**. 완화(제거)는 신규능력 아님 정합.

**음성검증 (rig-and-revert)**: 에스컬레이션 루프 블록만 제거한 게이트 사본을 동일 fresh R-1 입력에 실행 → `pass`/**exit 0**·`new:[]`·`warned:[]` 로 뒤집힘 = 가드 load-bearing 실증 + R-1 회귀 정확 재현(항상-PASS 아님). 원복 시 exit 2. 전체 `bash tests/run-tests.sh` **68/68 PASS**(신규 `new-capabilities-dynamic-level-escalation` 포함), 기존 `new-capabilities-dynamic-watched-pass`(base clean→head 동적 watched 단독=pass+warning) 유지, `git diff --check`(47db5c5..dec42e9) clean, `py_compile` OK.

**보수적 개발(§1)**: 보정 델타 `e839fe9` = `check-new-capabilities.py` +22줄(소비자 분류 1곳)·`tests/cases.yaml` 1케이스·픽스처 2파일. **추출기·`policies/*` 무접촉**(A-0011 명시요구 준수)·무관 리팩터/scope-creep 없음·Claude 소유 무접촉. `dec42e9` 는 공동소유 handoff/summaries.

**비차단 관찰 (O-1, 반려 아님)**: 에스컬레이션 record 의 `elif record["level"]=="watched"` 분기는 도달 불가(에스컬레이션 head level 은 항상 protected; watched(0)→watched(0)는 `≤` 로 skip). 방어적·무해·3단계 level 전방호환 → §2B 필수질문=아니오(구멍 아님). 비차단.

**머지(D-007)**: 신규 능력 diff 분석·판정 게이트 = **비민감**(approval 상한·1층 자동차단 불가·정산/인증·인가/암호화/migration/infra 무관·D-020~D-038 게이트 계열 선례). 테스트 머지로 코드 클린·`policies/sensitive-capabilities.yaml` AC#8 source/owner 보존 확인(브랜치 무수정). 머지가 브랜치 전체(원 추출기 `6aeb513`+보정)를 반입 — 추출기는 D-038 통과 확정분. 구현자(Codex)≠머지자(Claude) → **Claude `main` 머지·push. TASK-016 완결.**

---

## TASK-015 함수 후보 랭킹 스캐너 `bootstrap-sensitive-functions.py` — **통과·머지완료** (2026-07-11, D-037)

> 대상: `codex/2026-07-11-task015-bootstrap-functions` (impl `c174ae6`·핸드오프 `1895c1f`). 목적: `@gov` 전수 주석이 비현실적인 레거시에서 **이미 위험 능력/지정 SQL 테이블을 쓰는 함수**를 코드-밖 `sensitive-functions` 초안 후보로 뽑는다(주석 0·파일 무수정·draft_only).

**무엇을 검증했나** — "도는지"가 아니라 ① 기존 2개 추출기를 **재사용**했나(중복구현 금지), ② capability signal 을 함수 범위에 **정확히** 매핑하나(CLAUDE.md 고정 적대 세트: 데코레이터·동명 오버로드·조건부/중첩 def), ③ anchor/fingerprint 가 이동·이름변경 시 **조용한 무효화**를 막나(AC#6), ④ 신호가 **드롭 없이** 잡히나(fail-safe), ⑤ 결정적·비UTF8 내성·빈repo/무테이블 exit 0.

**한 줄씩 읽은 결과(핵심 로직)**
- AC#1 재사용 ✓: `importlib` 로 `extract-python-capabilities.py`(`extract_capabilities`)·`extract-python-inventory.py`(`extract_inventory`) 를 로드해 재사용 — 재구현 없음(`:25-26`,`:157`,`:168`,`:224`).
- 함수 매핑: `deepest_function_for_line(items, line)` = 해당 라인을 감싸는 함수 중 **가장 짧은(=가장 안쪽)** 것 선택, 없으면 `<module>` 폴백(`:77-95`). 폴백은 **드롭이 아님** — 신호는 항상 후보로 남는다(fail-safe 불변식).
- anchor = `{symbol: path::name, signature_hash: sha256(name(args))[:16]}`(`:56-74`,`:135-138`). fingerprint = `sha256({anchor, sorted(capabilities), evidence[source/capability_id/table/kind/name — line 제외]})`(`:113-129`). **line 을 지문에서 제외** → 같은 함수 내 신호 라인 이동엔 안정(D-035 계열 원칙 준수). suppression 은 accepted/rejected fingerprint 일치 시(`:304-310`).

**적대 검증(fresh, 픽스처 밖) — CLAUDE.md 고정 세트 전량 실행**
- ① **동명 오버로드**(getter/setter `Vault.secret`): start_line 이 달라 `candidate_key=(path,name,start_line)` 로 **각각 별도 후보** 유지 ✓. 시그니처(`secret(self)` vs `secret(self, value)`)가 달라 지문도 분리 ✓.
- ② **조건부/중첩 def**: `if/else` 안 def·클로저 `outer.inner` 모두 **가장 안쪽 함수로 정확 매핑**(`conditional_exec` 6-7, `outer.inner` 14-15) ✓.
- ③ **결정성**: 동일 입력 2회 stdout **바이트 동일** ✓.
- ④ **비UTF8 내성**(TASK-013 교훈): latin-1 `0xe9` 파일은 `errors` 로 격리(capability 경로=`unreadable`, table 경로=`UnicodeDecodeError` catch `:247`)되고 **형제 정상파일 후보는 보존·exit 0** — 전역 붕괴 없음 ✓.
- ⑤ **빈 repo·무 `--tables`**: exit 0, 오류 아님 ✓.
- ⑥ **음성검증**: `tests/cases.yaml` 의 `candidate_count`/`candidate_functions` 가 실제 후보에 묶여 있고, 회귀 케이스(accepted/rejected suppression)가 `suppressed_*` 단언으로 load-bearing(64/64 PASS, 케이스 기대 변조 시 해당 케이스만 FAIL 구조).

**비차단 관찰(3건 — 전부 fail-safe 또는 내재한계 → §2B 대로 차기 AC 가드로 *명시*, 반려 아님)**
- **O-1 (AC#6 rename 노트 미발화)**: `signature_hash` 가 함수명을 포함(`name(args)`)해, **이름변경(rename)** 시 `symbol` 과 `signature_hash` 가 **둘 다** 바뀐다 → `anchor_note`(`:287-293`)의 "possible move or rename" 분기는 **이동(move·경로변경, 동명)** 에만 발화하고 **rename 엔 절대 발화 못 함**(fresh 실증: `pay`→`pay2` 시 `review_note=None`; move 는 정상 발화). AC#6 "경로·**이름** 변경 시 재확인 표시" 의 이름측 미충족. **단 fail-safe**: rename 이면 지문도 바뀌어 **재제안(suppress 아님)** = 함수는 여전히 초안에 노출·보호 미해제. 손실은 "이전 결정과의 연결 힌트"뿐. AC#6 이 `signature_hash` 의 이름-독립을 명시 안 한 **명세 갭**(D-035 O-2 와 동형) → 차기 AC 가드: `signature_hash = 인자 시그니처만(이름 독립)` + 회귀 픽스처(accept→rename→재제안 **AND** move/rename 노트 발화).
- **O-2 (데코레이터 라인 능력호출 → `<module>` 귀속)**: 능력 호출이 **데코레이터 식**(`@subprocess.getoutput("id")`)에 있으면 그 라인이 `def` 라인(=`start_line`)보다 위라 `deepest_function_for_line` 이 함수 범위를 못 잡고 `<module>` 로 귀속(inventory `start_line=def줄` 한계, TASK-005/006 기존 성질). **단 fail-safe**: 신호는 **드롭 안 됨** — `<module>` 후보로 **정확한 라인 evidence** 와 함께 노출(사람이 그 라인=해당 함수 데코레이터임을 확인 가능). 함수-정밀 귀속만 상실. CLAUDE.md 고정 적대세트가 요구하는 **데코레이터 상설 회귀 픽스처가 TASK-015 에 부재** → 차기 AC 가드: 데코레이터-능력호출 픽스처 상설화 + (가능하면) 데코레이터 라인을 피감싸 함수로 귀속.
- **O-3 (동일 지문 충돌 → 양쪽 suppress)**: 한 파일 내 **이름·시그니처·능력·evidence(kind/name) 가 전부 같은** 두 함수(조건부 twin·동일시그 `@overload`)는 **같은 fingerprint** → 한쪽을 reject/accept 하면 **둘 다 suppress**(fresh 실증: twin `pay` 하나 reject 시 `suppressed_rejected=2`, 잔여 0). 유일하게 **fail-unsafe 방향**이나, 두 함수가 모든 포착 축에서 동일 = 초안 상에서 사람도 구분 불가 = 사실상 동일 함수 → 내재 한계. draft_only·verdict 미연결로 실해 미미 → 차기 AC 가드: suppression 키에 `start_line` 또는 본문 해시 disambiguator(위치 churn 재유입 주의).

**보수적 개발(§1) 평가**: 델타 = Codex 소유 `.harness/gates/bootstrap-sensitive-functions.py`(신규 408줄, 무관 리팩터/포맷/이름변경 없음)·`tests/cases.yaml`(3케이스)·`tests/run-tests.sh`·fixture 4파일·`README.md` 레지스트리 1줄·공동 `summaries`/`handoff-log`. **Claude 소유 policies/·docs/·CLAUDE.md·PROJECT.md·TASKS.md·decisions.md·templates/ 무접촉**(`--name-only` 확인)·change-intent 밖 경로 없음·scope-creep/over-reach 없음. `py_compile`·`git diff --check` OK·64/64 PASS.

**판정**: 핵심 AC(1~6 스캐폴딩)·fingerprint 안정성·재사용·결정성·fail-safe 불변식 충족, 3건 관찰은 전부 fail-safe/내재한계 → **통과**. **비민감**(draft_only 수동 씨딩 헬퍼·verdict 미연결·자동채택 없음·정산/인증·인가/암호화/DB migration/infra 무관, TASK-014·018~020 게이트 계열 Claude 머지 선례) → 구현자 Codex ≠ 머지자 Claude 로 **Claude `main` 머지**.

---

## TASK-014 fingerprint 안정성 가드 (D-035 O-2 마감) — **통과·머지완료** (2026-07-11, D-036)

> 대상: `codex/2026-07-11-task014-fingerprint-stability` (fix `4ecdc68`). 목적: D-035 에서 차기 AC 가드로 이월한 fingerprint 취약성 — accepted/rejected 된 존에 형제 파일 1개만 추가돼도 후보가 새 지문으로 재출현해 거절 원장(alert-fatigue 방지)이 무력화되는 논리결함 — 을 닫는다.

**무엇을 검증했나** — "도는지"가 아니라 ① 수정계약(지문 = 후보 정체성)을 정확히 이행했나, ② 형제 파일 추가에도 지문이 실제로 불변인가(적대 fresh), ③ 그 불변이 새 스킴 때문인가(음성검증 = 예전 스킴이면 깨지는가), ④ 회귀 픽스처가 reject·accept **양방향**을 덮나.

**한 줄씩 읽은 결과(핵심 로직)**
- `evidence_identity(e)` = `{source, rule_id}` 만 추출 → `matched`/개별 파일 `path`/`owner` 배제. 명세("경로+`level`+`{(source,rule_id)}` 집합, 개별 파일경로 지문 제외") 정확 일치.
- `candidate_fingerprint`: `evidence_rules = sorted({json.dumps(identity)…})` — **set 으로 중복 제거 후 정렬** → 같은 (source,rule_id) 가 파일 N개서 나와도 1개로 접힘 = 파일수·순서 무관. path·level 은 여전히 지문에 포함(정체성 유지·서로 다른 존 충돌 없음).
- `finalize_candidates`: 재산출 지문이 previous 의 rejected/accepted 지문과 일치하면 각각 suppress. evidence 보고(파일별 path)는 그대로 남음 = 사람 검토 정보 손실 없음.

**적대 검증(fresh 입력, 픽스처 밖·격리 worktree)**
- scratch repo(존당 파일 1개) 지문 캡처 → 형제 파일 추가 후 재산출 → **지문 전부 동일**: `services/auth/**`=`92efc7c9…`, `db/migrations/**`=`f2d0592e…`, `src/security/**`=`d69633e6…`. evidence 파일수 1→2·2→3 증가에도 불변. 픽스처의 저장 지문과도 일치(스킴 정합).
- **음성검증**: 동일 run1/run2 산출물을 **예전 evidence-전체 스킴**으로 재계산 → 형제 추가만으로 `db/migrations/**`·`services/auth/**` **CHANGED**(예: `services/auth/**` `33876acc…`→`7b264fb4…` = 예전 previous.yaml 의 원래 지문 `33876acc…` 와 정확히 일치 → 픽스처 지문이 새 스킴으로 올바로 재생성됐음도 교차확인), 단일 evidence `src/security/**` 만 SAME. → **새 스킴이 load-bearing**.

**회귀 픽스처(AC 가드 명세 이행)** — `previous.yaml` 에 `services/auth/**` rejected + `db/migrations/**` accepted 원장을 두고 repo 에 `logout.py`·`002_add_index.sql` 형제 추가 → `suppressed_rejected=1`·`suppressed_accepted=1`·잔여 후보 1(`src/security/**`). D-035 요구("존 reject→형제추가→여전히 suppressed", reject·accept 양쪽) 충족. `run-tests.sh` 에 `suppressed_accepted` 단언 추가(하네스 확장).

**보수적 개발** — Codex 소유 게이트 +11줄(무관 리팩터 0)·`cases.yaml`·`run-tests.sh`·fixture 2파일·`previous.yaml`. Claude 소유 정책/문서/TASKS 무접촉(name-only 확인). `py_compile`·`git diff --check` OK·61/61 PASS.

**비차단 관찰(O-1)** — 스킴 변경으로 예전(`ecd5d68`) 스킴 지문이 든 기존 원장은 지문 불일치로 suppression 이 조용히 깨질 수 있음. 단 draft_only·미도입(실운영 원장 부재)·D-035 가 명시 요구한 변경의 의도된 귀결 → 실해 없음, 가드 불요(관찰만).

**판정: 통과 · 비민감 → Claude main 머지(구현자≠머지자).** D-035 O-2 이월분 마감.

---

## TASK-014 정책 자동 씨딩 스캐너 `bootstrap-sensitive-zones.py` — **통과·머지완료** (2026-07-11, D-035)

> 대상: `codex/2026-07-11-task014-bootstrap-zones` (impl `ecd5d68`). 목적: 도입 시 사람이 백지에서 zones YAML 을 안 쓰도록, repo 를 스캔해 민감경로 후보를 **초안(draft)** 으로 자동 생성(사람은 승인만).

**무엇을 검증했나** — "도는지"가 아니라 ① 후보 근거가 정확한가(과대선전 없이), ② 초안일 뿐 자동채택이 없는가, ③ 거절 원장이 alert fatigue 를 실제로 막는가(AC#6 🔴), ④ 이 출력을 하류(사람이 sensitive-zones 에 붙임)가 어떻게 쓰나.

**한 줄씩 읽은 결과(핵심 로직)**
- `split_tokens` = 비알파넘 경계로 토큰화 → **부분문자열 오탐 없음**(`oauth.py`→`{oauth,py}`, `auth` 토큰 불매칭). 정합.
- `candidate_glob_for` = 매칭 토큰이 든 **첫 경로 세그먼트**까지 자르고 `/**` 부여(`services/auth/login.py`+`auth`→`services/auth/**`). 디렉토리 매칭엔 정확.
- `add_candidate` = 경로 키로 병합·evidence 누적·**LEVEL_STRENGTH 최댓값**으로 등급 승격. `merge_candidates` 로 path/codeowner 두 소스 evidence 를 한 후보로 합침 → `db/migrations/**` 가 `[codeowners, path_naming]` 두 근거. 정합.
- `finalize_candidates` = 정렬(path,level) 후 fingerprint 계산 → previous 의 rejected/accepted 지문이면 카운트만 올리고 스킵. rejected 스키마(`rejected_reason`/`rejected_by`) 항상 포함.

**적대적 검증(픽스처 밖 fresh 입력, 직접 실행)**
- **[T-A] 파일명 토큰**: `app/auth.py`(디렉토리 아닌 파일명에 토큰) → 글로브가 `app/auth.py/**` 로 생성됨. 어색 → **하류 영향 직접 확인**: 이 repo 매처 `check-sensitive-zones.match_glob("app/auth.py","app/auth.py/**")` = **True**(후행 `**` 가 0세그먼트 매칭). 즉 채택돼도 실제 파일을 보호함 → **기능상 정합·비차단**(cosmetic).
- **[T-B] no-CODEOWNERS repo**: path rule 단독으로 `services/auth/**` 후보·exit 0·`codeowners_read:false`. AC#5 ✓.
- **[T-C] 빈 규칙**: 후보 0·exit 0·오류 아님. AC#5 ✓.
- **[T-D 음성검증(rig-and-revert)]**: `cases.yaml` 의 `candidate_count: 3`→`99` 변조 → `bootstrap-sensitive-zones-candidates` **단독 FAIL(60/61)**, 원복 61/61. 테스트가 항상-PASS 아님·실가드 실증.
- **[T-E] 결정성**: 동일 입력 2회 stdout 바이트 동일. AC#4 ✓.

**🔴 발견 — fingerprint 취약성(거버넌스 영향, 차기 AC 가드로 명시 이월 O-2)**
- **재현(fresh)**: previous 에서 `services/auth/**` 를 `rejected`("too broad") 로 둔 채, repo 에 `services/auth/logout.py` **형제 파일 1개 추가** 후 재스캔 → `services/auth/**` 가 **다시 `proposed` 로 재출현**, `suppressed_rejected` **1→0**. `accepted` 로 둔 경우도 동일하게 **재제안**(`suppressed_accepted` 0). 즉 **accepted 중복제안 금지·rejected 재제안 금지 두 조항이 모두 형제파일 추가에 깨진다.**
- **원인**: `candidate_fingerprint` 가 `path+level+evidence` **전체 리스트**(매칭 파일별 `path` 포함)를 해싱 → 존 하위에 파일이 하나만 늘어도 evidence 집합이 바뀌어 지문이 변함. 살아있는 repo(특히 `auth/` 같은 활성 디렉토리)에선 사실상 매 스캔 재출현.
- **왜 🔴 인가**: AC#6 이 이 정확한 실패를 명문화("이게 없으면 스캔 재실행마다 거절된 후보가 재출현해 씨딩 자체가 alert fatigue 원인") — 기능 헤드라인 목적을 일상 성장에서 defeat.
- **그러나 보정요청(반려)이 아니라 차기 AC 가드로 처리하는 이유(공정성)**: AC#6 이 fingerprint 를 **"경로+근거(evidence) 정규화 해시"** 로 *명시*했고 Codex 는 그대로 이행. 수용기준·논리 정합·테스트 모두 충족한 구현을 명세대로 짰다는 이유로 반려하는 것은 부당(§2B "수용기준 충족+논리 정합이면 머지 유효"). 결함의 뿌리는 **명세(내가/선행 Claude 가 쓴 AC) 설계**. → §2B "거버넌스 영향 논리결함은 비차단으로 흘리지 말고 차기 AC 가드로 *명시적으로* 막는다" 에 따라 **TASKS.md AC#6 개정 + 회귀 픽스처 요구를 명시**(아래 수정계약).
- **수정계약(차기)**: fingerprint = **후보 정체성** = `path`+`level`+정렬된 `{(source, rule_id)}` 집합(개별 매칭파일 `path` 는 evidence 보고에는 남기되 지문 산출에서 제외). 회귀 픽스처: 존 reject → 형제 파일 추가 → 재스캔 시 **여전히 suppressed** (rejected·accepted 양쪽).

**보수적 개발 평가(§1)**: change-intent(TASK-014) 범위 내. Codex 소유 `.harness/gates/`·`tests/` + README 레지스트리 2줄만. **Claude 소유(policies/·docs/·CLAUDE.md·TASKS.md·templates/) 무접촉**·무관 리팩터/포맷/이름변경 없음·blast radius 정상. scope-creep/over-reach 없음.

**판정**: 통과. **비민감**(draft-only 수동 씨딩 헬퍼·verdict 파이프라인 미연결·자동채택 없음·정산/인증/암호화/migration/infra 무관) → 구현자≠머지자로 **Claude `main` 머지·push**. fingerprint 취약성은 **O-2 차기 AC 가드**로 명시(TASKS.md 반영).

---

## TASK-020 R-1 보정 재제출 재리뷰 — **통과·머지완료** (2026-07-11, D-034)

> 멱등성: 재제출 델타 `32726a6`(fix)·`d1c98e1`(docs)만 재리뷰. `5449c65`·`42062f6`(D-033 통과 정상경로) 재론 불요.

**무엇을 검증했나** — D-033/A-0010 의 수정계약 1건(R-1)이 실제로 닫혔는지, 그리고 그 수정이 새 구멍을 열지 않았는지 적대적으로.

- **정합성(런타임↔정책diff)**: 런타임 게이트(`check-sensitive-zones`·`check-new-capabilities`·`generate-change-evidence`·`extract-python-capabilities`)는 `VALID_MATURITY={"enforcing","shadow"}`·정확히 `== "shadow"` 만 완화, 무효값은 fail-closed enforcing. 보정된 `check-policy-change` 의 `maturity_weakened` 도 `after == "shadow"` 정확일치. → 대문자/오타 maturity 는 런타임서 enforcing 으로 fail-close 되므로 정책diff 가 완화로 안 잡아도 **실효 완화가 없다 = 정합**. 케이스 민감도 불일치 우회 없음(직접 확인).
- **구조 정확성**: `maturity_weakened` 는 `set(before) & set(after)` 교집합 루프 안에서만 호출 → **기존 룰**만 대상. 신규 shadow 룰(after-only)은 미발동, 삭제 룰(before-only)은 `removed_zone`/`removed_capability` 가 별도로 잡음. 무한퇴행·과탐 없음.
- **적대 재검증(격리 worktree · 픽스처 밖 fresh 입력)**:
  - T-A no-maturity frozen 정산존 +한 줄 `maturity: shadow` → `approval_required`/exit 2·`weakened_zone_maturity`. (R-1 이 지적한 바로 그 시나리오가 이제 차단됨)
  - T-B base 에 없던 신규 shadow frozen 존 추가 → pass/exit 0(과탐 아님).
  - T-C capability `protected` enforcing→shadow → `weakened_capability_maturity`/approval.
  - **음성검증(rig-and-revert)**: `maturity_weakened`→`return False` → `policy-change-maturity-shadow-loosening` **단독 FAIL(57/58)**·`-new` 는 PASS 유지(신규는 애초에 완화 아님), 원복 58/58. 감지블록이 load-bearing 이고 회귀 픽스처가 always-pass 아님을 실증.
- **회귀**: `tests/run-tests.sh` **58/58 PASS**(기존 56 + 신규 2). `git diff --check`·`py_compile` OK.

**판정: 통과.** 보수적 개발 준수(Codex 소유 게이트 +28줄·무관 리팩터/scope-creep 없음·Claude 소유 정책 무접촉). **비민감**(거버넌스 메타게이트를 fail-closed 방향으로 강화·1층 자동차단 권한 없음·기존 감지 무회귀·TASK-018/019 동일 범주 Claude 머지 선례) → 구현자(Codex)≠머지자(Claude) 로 Claude 가 `main` 머지·push. MVP-1.5 TASK-020 완결.

**비차단 이월(MVP-2, O-1)**: `maturity_weakened` 가 `before` 를 리터럴 `"enforcing"` 로만 비교 → **무효 maturity(예 `pilot`, 런타임 fail-closed enforcing) → `shadow`** 전환은 실효적 완화인데 미탐(fresh T-D: pass/exit 0). 발동 전제(base 가 이미 무효값 = 오류표시 상태)가 비정상이고 **주 경로(유효 enforcing/무기입→shadow)는 R-1 로 닫힘** → §2B 원칙대로 **차기 AC 가드로 명시**(비차단으로 흘리지 않음). 수정형: `maturity_weakened` 를 효과적 maturity 정규화(`m if m in VALID_MATURITY else "enforcing"`) 기반 `before_eff != "shadow" and after_eff == "shadow"` 로.

---

## TASK-020 규칙 성숙도(maturity/shadow) — **보정요청** (2026-07-11, D-033 · A-0010)

- 대상: 브랜치 `codex/2026-07-11-task020-maturity` (헤드 `42062f6`, 구현 `5449c65`)
- 파일: `check-sensitive-zones.py`·`generate-change-evidence.py`·`extract-python-capabilities.py`·`check-new-capabilities.py` + `tests/fixtures/maturity`·`capabilities`·`new-capabilities/{shadow-capability,invalid-maturity}` + `cases.yaml`/`run-tests.sh`
- 결정: **D-033 보정요청(R-1·🔴)** — 코드 브랜치 보류, 리뷰기록만 main.

### 심층·적대적 검증 (fresh 입력·픽스처 밖 + 음성검증)

설계 정합: 4게이트 모두 `maturity`(기본 enforcing) 를 정책 로드에 정규화, **verdict 집계 직전** shadow/non-shadow 파티션 분리 — shadow 는 `shadow_hits`/`shadow_capabilities` 로만 기록. `strongest_records` 를 두 파티션에 **각각** 적용해 shadow 가 non-shadow 판정에 개입 못 함.

- **AC #1 하위호환** ✅ — 무기입=enforcing. 기존 56/56 무회귀. enforcing 명시(T2 frozen→BLOCKED·T4 protected→APPROVAL)가 maturity 도입 전과 동일.
- **AC #2 verdict 미반영+기록** ✅ — fresh 5정책 존:
  - T1 shadow-frozen→PASS(0)+shadow_hit / T3 shadow-protected→PASS+shadow_hit.
  - **혼합존(같은 경로 2룰)**: T6 shadow-frozen + enforcing-protected → **APPROVAL(2)**(frozen 으로 에스컬레이트 안 함)·shadow_hit=frozen. T7 shadow-protected + enforcing-watched → **PASS(0)**(watched 만 집행). = 파티션 로직 정합.
  - `check-new-capabilities`: shadow cap → `shadow_capabilities`·pass. `generate-change-evidence`: shadow-frozen → 카드 `status:pass`·`frozen_touched:[]`·`shadow_hits` 기록(verdict 무오염). zone_level_by_path 는 shadow-only 경로에 원 level(protected 등) 보고하나 verdict/status 는 non-shadow touched 로만 구동 → 카드 정직·차단 무영향.
- **AC #3 fail-closed 절** ✅ — 잘못된 `maturity: pilot`→T5 검증오류+enforcing 보수(approval·exit 2). extract/capability 동일.
- **AC #4 쌍+음성** ✅ — 독립 rig-and-revert 2종: ① sensitive-zones verdict-side 필터 `!= "shadow"` → 전체수용으로 rig 시 shadow-frozen 이 **BLOCK 으로 뒤집힘**(필터 load-bearing). ② check-new-capabilities `maturity` 상수 enforcing rig → `new-capabilities-shadow-pass` **단독 FAIL(55/56)**·원복 56/56.
- **보수적 개발(§1)** ✅ — 국소·무관리팩터 없음·Claude 소유 무접촉.

### R-1 (🔴 보정사유) — AC #3 정합성 조항 미충족 (§2B 직접구멍)

AC #3: "`maturity: shadow` 로 바꾸는 diff 는 TASK-018 이 완화로 잡는다 — 두 태스크 정합 필수." **미충족.** clean fresh 저장소 실증:
- base=`app/pay/**` frozen(정산 핵심), head=같은 존에 한 줄 `maturity: shadow`. → sensitive-zones 가 `app/pay/core.py` 를 **PASS**(frozen 자동차단 무력화). → **정책 diff 를 `check-policy-change.py` 가 완화 미탐(PASS·exit 0)**. 양성대조: `frozen→protected` 하향은 정상 감지(`weakened_zone_level`·exit 2) = 게이트는 작동하나 maturity 차원 부지.
- **판정근거**: frozen 은 유일한 하드-차단(불변원칙 §4). 그 층이 어떤 게이트에도 안 걸리는 한 줄로 소리없이 꺼짐 = maturity=shadow 는 의미상 규칙삭제/등급하향과 동일한 완화. §2B 필수질문("거버넌스 목적에 직접 구멍?") = 예 → 비차단 불가.
- **수정계약**: `check-policy-change.py`(Codex 소유) 구조비교에 maturity 차원 — 기존 zone/cap enforcing→shadow 전환=`policy_loosening`(approval), 신규 shadow 룰 신설=pass(정상 롤아웃). 회귀 픽스처 1쌍 + 음성검증. 유한·구조적(무한퇴행 아님).

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

---

## TASK-011 follow-up 리뷰 — 분리대입 getattr 능력 감지 보강 (D-026, impl `b6cc23d`)

**대상**: `codex/2026-07-05-task011-getattr-assignment` (헤드 `96b8715`). D-025 에서 남긴 비차단 관찰(**제3 변형 분리대입 getattr** `fn = getattr(os,"system"); fn(c)` 미감지)을 해소하는 후속. 변경 = 추출기 `build_import_bindings` 의 `ast.Assign` 핸들러 3줄(`resolve_getattr_call_name` 우선 시도 후 `dotted_name` fallback) + 회귀 픽스처(`valid.py` +1함수·`cases.yaml` golden +1호출·하류 `new-capabilities/getattr-assignment/` + `check-new-capabilities` 케이스).

**심층 검증 방식**: 소스 한 줄씩 정독 + **픽스처 밖 fresh 입력** 4종 직접 구동 + **rig-and-revert 음성검증**. 무발견≠통과.

**실증 결과**:
- **[A] POSITIVE**: fresh `import os / fn=getattr(os,"system"); fn(cmd)` → `subprocess_exec level=protected signals=call:os.system:4` 검출 ✓ = D-025 관찰 폐쇄. 해소 경로: `resolve_getattr_call_name` 이 `getattr(os,"system")` → `os.system` 반환 → `Assign` 이 `fn→os.system` 바인딩 → 호출부 `resolve_call_name(fn)` 이 `os.system` 으로 해소 → `call_index` 적중.
- **[음성검증·rig]**: 3줄 우선분기를 되돌려 `dotted_name` 단독으로 rig → **37/39**(추출기 golden `valid.py` + 하류 `new-capabilities-getattr-assignment` **2건 FAIL**), fresh [A] MISS. 원복 39/39. → 신규 golden/케이스가 실가드(항상-PASS 아님).
- **[C] 동적 정상거부**: `fn=getattr(os,name)`(2번째 인자=변수) → 미해소(정적 판별 불가) — 수용 dynamic, 오해소 없음.
- **[D] 오탐 없음**: `getattr(os,"getcwd")`(비민감 함수) → `subprocess_exec` 무발동 = catalog 기반 정밀 매칭.
- **[B2] 대조**: `import os as o; o.system(cmd)`(직접 별칭 호출) → 정상 감지 ✓.

**하류 영향(§2B)**: 추출기 capabilities → `check-new-capabilities` 가 `head−base` 로 소비. 신규 파일에서 이 형태가 이제 신규 능력으로 잡혀 approval 승격(2층 상한·blocked 아님). 정합.

**⚠️ 비차단 관찰 1건 (거버넌스 관련·§2B 명시 → 차기 AC 가드)**:
1. **별칭 base + getattr + 분리대입 삼중난독 잔여**: fresh 실증 [B] — `import os as o; fn=getattr(o,"system"); fn(cmd)` 는 **여전히 미감지**. 원인: `Assign` 핸들러가 `resolve_getattr_call_name` 이 이미 `o→os` 해소해 반환한 `os.system` 을 **다시 `partition`** 해 root `os` 를 bindings 에서 찾는데 바인딩된 건 별칭 `o` 뿐 → `root not in bindings → continue`(이중 해소 결함). **비차단 근거**: (a) import-신호 모듈(주 실행벡터)은 backstop 이 모든 난독 포착 — 갭은 오직 call-only os 계열 삼중난독 한정, (b) 2층 approval 상한 → 최악도 승인 프롬프트 누락(오차단·자동머지 아님), (c) 명시 AC(plain 형태 + 회귀픽스처)는 충족, (d) TASKS.md line 138 이 잔여의 차기 가드 이월·catalog 문서화 수용을 이미 허용. **개선 제안(내가 짠다면)**: getattr 경로가 잡히면 값이 이미 완전 해소돼 있으므로 재-partition 없이 그대로 `target` 으로 쓰면 별칭 base 도 무료 폐쇄(3줄). §2B "대규모 리팩터 강요 금지" 하에 보정요청 아닌 **차기 AC 가드로 이월**.

**보수성(§1)**: 델타 국소, **Claude 소유(policies/docs/CLAUDE/decisions/answers/review-notes/templates) 무접촉**(diff 확인), scope-creep 없음. `git diff --check`·`py_compile`·39/39 PASS.

**머지(D-007)**: 분석 전용 추출기 강화(exit 0·판정 없음·차단 불가·2층 approval 상한) = **비민감** → 구현자(Codex)≠머지자(Claude), **Claude main 머지·push**. 멱등성: b6cc23d·96b8715 재처리 금지.

## TASK-011 follow-up (D-027) — 별칭 base + getattr 삼중난독 감지 보강 리뷰 (impl 27716df, 헤드 d5548eb)
**대상**: `codex/2026-07-05-next-task`. **D-026 비차단 관찰(삼중난독 `import os as o; fn=getattr(o,"system"); fn(c)`) 폐쇄** — 정확히 D-026 리뷰 "내가 짠다면" 제안(재-partition 없이 그대로 target) 그대로 구현.
**변경**: `Assign` 핸들러가 `resolve_getattr_call_name(..., require_bound_base=True)` 로 완전 해소된 값을 재-partition 없이 `target` 전파. `require_bound_base` 신규 파라미터: getattr base root 미바인딩 시 `None`→dotted 폴백/드롭(비-getattr Assign·미바인딩 base 무손상). +회귀 픽스처(하류 `getattr-assignment-alias/`·`valid.py`·`cases.yaml`).

**🔴 적대적 실증(fresh·워크트리 재현)**:
- [A] alias 삼중난독 검출 ✓ / [G] 형제 오염 없는 고립 alias 도 검출 ✓ / [B] 비-별칭 회귀 무손상 ✓ / [E] 연쇄 `p=o;getattr(p,...)` 도 검출 ✓ / [C] 동적 non-literal 정상 MISS / [D] `getcwd` 비민감 오탐 없음 / 결정성 md5 동일.
- **음성검증(rig-and-revert)**: `Assign` 을 D-026 이전 재-partition 로 되돌림 → 하류 `getattr-assignment-alias` **FAIL(39/40)**, 원복 40/40 = 실가드.

**⚠️ 비차단 관찰 2건(§2B)**:
1. **`valid.py` line77 = 약한/중복 가드**: rig 후에도 `valid.py` golden PASS — 같은 파일 형제함수 bare `import os` 가 **함수 스코프 없는 모듈공유 `bindings`** 에 `os→os` 를 남겨 별칭 경로가 우연 해소됨. 진짜 독립 가드는 하류 `getattr-assignment-alias`(형제 오염 없음). 오탐 아님(현행 동작 정확 기록)이나 독립 증명력 없음. flat-bindings 오염 방향은 "더 많은 해소=더 많은 탐지"=거버넌스 안전측(오탐≤approval, miss 유발 아님) → **비차단**.
2. **getattr-builtin 별칭 잔여 [F]**: `g=getattr; g(o,"system")` 미감지(`func.func.id!="getattr"` 조기반환). D-024/D-025 문서화 수용잔여("call-only 동적우회")의 더 깊은 변형(무한퇴행). import-신호 backstop·2층 상한 → **비차단·catalog 수용잔여**(TASKS.md line140 밑 명시). 지역 dataflow 도입 시 일괄 폐쇄.

**보수성(§1)**: 델타 국소(추출기 ~5줄+tests), **Claude 소유 무접촉**(diff 확인), scope-creep 없음. `git diff --check`·`py_compile`·40/40 PASS.
**머지(D-007)**: 분석 전용 추출기 강화(exit 0·차단 불가·2층 approval 상한) = **비민감** → 구현자≠머지자, **Claude main 머지·push**. 멱등성: 27716df·d5548eb 재처리 금지.

---

## TASK-018 (D-028) 정책 완화/집행-우회 게이트 `check-policy-change.py` — 보정요청

- **대상**: `codex/2026-07-09-task018-policy-change` impl `c4621fc`·헤드 `933c017`. 신규 게이트 491줄 + 픽스처 6종(loosening·strengthening·comments-only·rule-delete·runner-bypass·runner-removal) + `tests/run-tests.sh`/`cases.yaml` 확장 + README 1줄.
- **판정**: 보정요청 — 코드 머지 보류. 정책 의미-diff(AC #1~5)는 통과 수준, 결함은 집행-우회 감지(AC #7b) 협소성 + AC #7 픽스처 미완.

### 통과 실증 (재검증 불요 — 보정 재리뷰 시 델타만)
브랜치 워크트리(`933c017`) 실측: `bash tests/run-tests.sh` **46/46 PASS**·`git diff --check` clean·`py_compile` OK.
- **정책 의미-diff(AC #1·#2, fresh 픽스처 밖)**: frozen→protected 존 하향 → approval(`weakened_zone_level`) / `required_approval` 제거 → `removed_required_approval` / glob 협소화(path 편집 `**/settlement/**`→`**/settlement/core/**`) → `removed_zone`(AC#1 범위축소 포착) / `max_verdict: approval_required→watched` → `weakened_value` / `block_levels:[frozen]→[]` → `removed_list_item` / capability·signals 삭제 → `removed_list_item` / approval-routing `default_reviewer` 제거 → `removed_key` / routing **동수 스왑** → `removed_list_item`(구조 리스트 diff 가 count-only 우회 무력화). 키재정렬+주석 → pass(AC#2 구조비교).
- **AC #5**: 결정적(deterministic_stdout)·종료코드 **0/2 만**(상위 예외도 approval).
- **음성검증(rig-and-revert)**: 게이트 `verdict="pass"` 강제 시 approval-기대 4케이스(loosening-level·rule-delete·runner-bypass·runner-removal) **FAIL**, pass-기대 2케이스 유지 → 원복 46/46. 테스트 실가드 실증.
- **집행-우회 동작 경로**: 게이트 라인 제거→`removed_gate_invocation`(7a) / `|| true`·`continue-on-error: true`(정준형) 삽입→`added_gate_bypass`(7b) / `|| :`·`|| exit 0` 라인변형→`removed_gate_invocation`(안전측) / required-check 제거→`removed_required_check`(7c, 코드 동작·픽스처 없음).

### 🔴 R-1: `continue-on-error` 우회 감지가 정확문자열 `true` 만 매칭 → 등가 boolean 변형으로 집행 무력화 통과
`detect_enforcement_bypass`(line 359) `"continue-on-error: true" in line` — 소문자·단일공백·무따옴표 정확 부분문자열만. GHA/YAML 1.2 core 는 아래를 동등 boolean true 로 수용:

| head 삽입(게이트 라인 무변경) | GHA 효과 | verdict |
|---|---|---|
| `continue-on-error: true` | 무력화 | approval ✓ |
| `continue-on-error: True` / `TRUE` / `  true`(2칸) / `"true"` | 무력화 | **pass ✗ 우회** |

AC #7(b) "무력화 삽입 감지" 미충족 + TASK-018 P0 자기무력화 목적 **직접구멍**(§2B=그렇다 → 비차단 불가). truthy 정규화는 결정적 패턴매칭이라 "의미추정 금지" 위반 아님. **수정계약**: `continue-on-error` 값을 정규화(공백무시)·소문자화해 `{true,yes,on}`(따옴표무관) 매칭 + 회귀픽스처(변형→approval, 음성검증).

### 🟠 R-2: AC #7 픽스처 미완 — (b)`continue-on-error` 변형·(c)required-check 제거 부재
AC #7 은 (a)(b)(c) **픽스처 각 1건** 요구. 현재 (a)runner-removal·(b)정준형 runner-bypass 만. (c) 감지코드는 동작하나 회귀 미고정. R-1 변형 + (b)(c) 픽스처 추가.

### 비차단 관찰 (catalog)
- **O-1**: 넓은 frozen/protected 존 **유지** + 하위 약한 carve-out 존 **추가** → 유효보호 축소이나 pass. 존 precedence 해석(최장접두 등) 필요 = 의미영역. path/level 직접 편집 축소는 이미 포착 → **MVP-2**.
- required-check 감지는 워크플로 내 `required`/`branch-protection` 부분문자열 best-effort(실 branch-protection 은 repo 설정/ruleset 상주) — AC "생기면" 한정, 오탐 approval(안전측) → 현행 허용.

### AC #6 / Q-0002 — Claude 직접 반영(정책 소유)
`policies/**`·`.harness/**`·`tests/run-tests.sh`·`tests/cases.yaml`·`.github/workflows/**`·`CODEOWNERS` → `policies/sensitive-zones.yaml` **protected** 등록(이 리뷰 브랜치). **load-bearing**: 게이트 로직 자체 무력화(항상-pass 편집)는 `check-policy-change` 스스로 미포착·`check-sensitive-zones` 만 포착 — 실증: `.harness/gates/check-policy-change.py`+`tests/cases.yaml` 편집 → verdict approval_required, protected_touched 정확. level=protected(frozen 아님) = 하네스 진화 + 자기보호 양립. ⚠️ 운영부담(harness/tests 편집 매번 승인요구) 형 인지 — A-0006 §Q-0002.

### AC #8 미해결 (비차단·추적)
policy bundle digest(판정 시점 정책 파일 해시목록) 감사카드 기록 — 이 브랜치 미구현. `generate-change-evidence.py`(Codex)+`change-evidence.template.yaml`(Claude) 동시개정·TASK-019(카드 정직화·버전기록) 파일 겹침 → **TASK-019 와 함께 처리**로 이관. 게이트 자체 결함 아님.

### 머지 판정(D-007)
코드 브랜치 **보류**(R-1·R-2 보정 델타만 재리뷰, 멱등성 `c4621fc`·`933c017` 재처리 금지). 리뷰기록 + 자기보호 등록은 **main 머지**.

## TASK-018 재리뷰(2차 보정) — R-1·R-2 해소 확인 · R-3 보정요청 (2026-07-09, D-029)

- 대상: 보정 재제출 `297acac`, 헤드 `0e28580` (브랜치 `codex/2026-07-09-task018-policy-change`)
- 결정: **D-029 보정요청(2차)** — R-1·R-2 닫힘, 신규 R-3(인라인 주석 우회)로 코드 브랜치 계속 보류.
- 방법: 브랜치 헤드 워크트리 실측 + 임시 git repo 로 fresh 적대 입력 주입(픽스처 밖) + rig-and-revert 음성검증.

### R-1 해소 실증 — truthy 정규화 (`is_gate_bypass_line`)
fresh 8종(게이트 호출라인 무변경·`continue-on-error` 라인만 추가): `true`/`True`/`TRUE`/`  true`(2칸)/`"true"`/`'true'`/`yes`/`on` → **전부 approval_required(added_gate_bypass)**; 음성대조 `false` → **pass**. A-0006 지목 4우회(`True`/`TRUE`/2칸/`"true"`) 폐쇄 확인.

### R-2 해소 실증 — 픽스처 (b)·(c) + 음성검증
- (b) `runner-continue-on-error`(head `continue-on-error: True`): truthy 집합을 `set()` 으로 rig → 이 케이스 단독 FAIL(47/48), 원복 48/48 = 실가드.
- (c) `required-check-removal`(head `required` 제거): required-check 분기 `if False` rig → 이 케이스 단독 FAIL(47/48), 원복 48/48 = 실가드.
- 두 픽스처 자기 감지경로에만 반응(교차오염 없음). 전체 48/48 PASS.

### 🔴 R-3 (신규 미탐 — 적대 재검증서 발견)
`continue-on-error: true # keep going` 삽입 → 게이트 **pass**(우회). YAML ` #` 인라인 주석 → 파서가 벗겨 값 `true` → GHA 집행 무력화. 게이트는 `unquote_scalar(" true # keep going").lower()` = `"true # keep going"` ∉ `{true,yes,on}` → 미탐(`python3` 분해로 확인). AC #7(b) 계열·P0 직접구멍(§2B=그렇다) → 보정요청. 폐쇄 유한(YAML truthy 철자 확정) — 주석-strip 국소 델타면 계열 완결. 상세·수정계약: `collab/answers/A-0007.md` R-3.

### 비차단 관찰
- O-2: `continue-on-error: 1` 미탐이나 GHA 정수 truthy 수용 불확실 → R-3 범위 밖(MVP-2).
- O-1(선행): 넓은 존 유지 + 약한 carve-out 존 추가 → pass(존 precedence 의미영역, MVP-2).

## TASK-018 재리뷰(3차 보정) — R-3 해소 확인 **통과** + Claude 머지 (2026-07-09, D-030)

- 대상: R-3 보정 재제출 `ab4447a`, 헤드 `f966394` (브랜치 `codex/2026-07-09-task018-policy-change`)
- 결정: **D-030 통과** — R-3 닫힘. `check-policy-change.py`(분석·판정 게이트·비민감) → **Claude 가 main 머지**. MVP-1.5 TASK-018 완결.
- 방법: 브랜치 헤드 워크트리 실측(49/49 PASS) + 함수 직접 호출 fresh 적대 19종(픽스처 밖) + rig-and-revert 음성검증 + 단일 caller/scope 확인.

### R-3 해소 실증 — 인라인 주석 strip (`normalize_yaml_plain_scalar`)
`unquote_scalar` → `normalize_yaml_plain_scalar` 로 교체(**단일 caller** `is_gate_bypass_line` 만·grep 확인, 타 경로 무영향). 값을 순회하며 따옴표 상태 추적, **따옴표 밖·앞 공백 있는 첫 `#`** 에서 절단 후 unquote·소문자화·`{true,yes,on}` 매칭 = A-0007 수정계약 정합.
- **R-3 핵심 폐쇄**(감지=approval): `true # keep going`·`True # ops-approved`·`yes # x`·`on # x`·`'true' # c`·`"true" # c`·탭+`#`·다중 `#`(`true # a # b`) 전부 감지.
- **YAML 의미 정확**(미감지 유지=정합): `true# nospace`(공백 없는 `#`은 주석 아님·값 그대로) / `"tr#ue" # c`(따옴표 안 `#`은 값 일부, 실제 `tr#ue` 비-truthy) / 빈값 `# only comment`. → 과탐 없음.
- **R-1 무회귀**: `true`/`True`/2칸/`"true"` 감지·`false` pass. `|| true`·`|| true # note` 무영향. **19/19 기대 일치.**

### 음성검증(rig-and-revert)
주석-strip 블록(`if char == "#" …: stripped = stripped[:index].strip(); break`) 제거 → 신규 픽스처 `policy-change-runner-continue-on-error-comment` **단독 FAIL(48/49)**, 원복 **49/49** = 실가드. 전체 49/49 PASS·`git diff --check`(0e28580..head) clean·`py_compile` OK.

### 보수적 개발·scope
R-3 코드 델타(`ab4447a`) = `check-policy-change.py`(14줄)+`cases.yaml`(1케이스)+신규 픽스처 2파일. Claude 소유 무접촉·scope-creep 없음. 범위 내 answers/decisions/review-notes/sensitive-zones 는 origin/main 동기화 머지(`5691329`, 코드 무변경)로 들어온 내 기존 기록(origin/main 과 동일·변조 없음 확인).

### 공정성 메모
R-3 은 Codex 불이행 아님 — A-0006 계약 정확 이행. 인라인 주석 벡터는 내 A-0006 계약 누락이 적대 재검증서 노출. 산출물의 거버넌스-직결 결함이라 §2B 대로 머지 전 폐쇄(델타 국소·유한).

---

## TASK-019 감사카드 정직화 coverage statement — **보정요청** (2026-07-09, D-031)

- 대상: `codex/2026-07-09-task019-coverage-statement` · impl `d8ad086` · 헤드 `195a957`
- 파일: `.harness/gates/generate-change-evidence.py`(+71) · `templates/change-evidence.template.yaml` · `tests/cases.yaml` · `tests/run-tests.sh`(+28)
- 결정: **D-031 보정요청** · 반려서 `collab/answers/A-0008.md`

### 수용기준 대비 (정상 경로)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | pass 문구 통일·SAFE/안전 금지 | ✅ | `verdict pass → "no governance violation detected"`; `no_safe_text` 테스트가 `safe`/`안전` 부재 강제 |
| 2 | coverage `checked`(실행 게이트 동적)+`not_checked`(고정) | ✅(정상)/🔴(오류경로 R-1) | `checked` 는 `can_run_function_gov` 술어 기반 — baseline 2게이트 vs function 3게이트 |
| 3 | python(parser) 버전 기록 | ✅ | `python_version: sys.version.split()[0]` + `tool_version`·`policy_sha` |
| 4 | 스키마 키==템플릿+음성검증 | ✅(정상)/🟠(오류경로 R-2) | `schema_keys_match_template`(정상 4픽스처만) |

### 적대적 검증 (능동적으로 깨봄)
- **음성검증 ①(동적성 실가드)**: `executed_gate_records` 의 `if can_run_function_gov(...)` → `if True` 로 변조 → **baseline 케이스 FAIL** (`coverage.checked.gates: expected ['check-change-intent','check-sensitive-zones'], got [...,'check-function-gov-level']`). 원복 49/49. → AC #2 동적성 가드는 항상-PASS 아님(실가드).
- **음성검증 ②(정직성 실가드)**: pass 문구에 `(safe)` 주입 → `no_safe_text`("forbidden safe/안전 wording found") + `verdict_statement` 두 가드 동시 FAIL. → AC #1 정직성 가드 실가드.
- **fresh 입력 ③(픽스처 밖)**: `generate-change-evidence.py HEAD~1..HEAD --change-intent /nonexistent.yaml` → **예외 카드** 재현. `policy_sha:{}`·`reasons:['의도 선언 누락…']`·게이트 0 실행인데 `coverage_statement.checked` 는 3게이트·`verdict_statement: governance violation detected` **위조** → R-1 근거. 동일 카드 top-level 16키(template 17키에서 `changed_functions` 누락) → R-2 근거.

### 결함 (머지 전 폐쇄 요구)
- **🔴 R-1**: 오류 카드가 실행 안 한 게이트를 `checked` 로 위조 + 입력오류를 "governance violation detected"로 오표기. 카드 정직화 태스크의 정직성 회귀(신규 coverage 블록이 도입). §2B 필수질문=그렇다(산출물=거버넌스 기능). 도달성 높음(기본호출·정책파손). **수정**: 오류경로 `checked:[]`(주변 empties 와 정합), 정상경로 무변경.
- **🟠 R-2**: 오류 카드 `changed_functions` 누락 → template↔오류카드 스키마 드리프트. `schema_keys_match_template` 가 오류경로 미검사(거짓확신). **수정**: 오류카드 `changed_functions:[]` + 오류경로 픽스처로 가드 확장.

### 비차단 관찰 (MVP-2)
- **O-1**: `schema_keys_match_template` top-level 키만 비교 — 중첩 임의키 미포착(현재 coverage 단언이 사실상 커버). 차기 재귀 형상비교 옵션.
- AC #8 policy bundle digest: `policy_sha`(sensitive-zones·approval-routing sha256)로 부분충족. 전체 판정정책 번들 해시 확장은 MVP-2.

### 검증 로그
`bash tests/run-tests.sh` 49/49 PASS · `git diff --check` clean · `python3 -m py_compile generate-change-evidence.py` OK — 전부 격리 worktree 재현. 음성검증 2종·fresh 입력 1종 직접 실행.

## TASK-019 보정 재제출 재리뷰 (D-032) — 통과 · main 머지
대상 `codex/2026-07-09-task019-coverage-statement` · 보정 `c72169d` · 헤드 `29a48e9`. 범위 = R-1·R-2 델타만.

### 한 줄씩 뜯어본 것
- `coverage_statement(diff_input, verdict, checked=None)` — 기본 `None` 이라 정상 호출부 3곳 동작 **비트 단위 동일**. 예외 핸들러만 `checked=[]` 명시. 최소 침습이고, 내가 짜도 같은 형태(굳이 별도 `error_coverage_statement()` 를 파느니 선택인자가 낫다 — 호출부가 하나뿐).
- 예외 발생 지점 전수 확인: `build_evidence` 는 `load_intent`(180 `FileNotFoundError`) → `load_sensitive_policy`/`load_routing_policy`(YAML 파손) → `read_diff_lines`(86 `RuntimeError`) 순으로 **게이트 평가 이전**에만 raise 가능. 따라서 `checked:[]` 는 방어적 공백이 아니라 **사실 진술**이다. (`build_function_gov_result` 는 내부에서 errors 를 흡수해 `function_analysis_error:` reason 으로 내보내므로 통상 raise 안 함 → O-3 참고)

### 적대적 검증 — fresh 입력(픽스처 밖) 3종
| 입력 | rc | verdict | `checked` | 키수 | 템플릿 일치 |
|---|---|---|---|---|---|
| `HEAD~1..HEAD --change-intent /nonexistent-XYZ.yaml` (D-031 원 재현입력) | 1 | blocked | `[]` | 17 | ✓ |
| `--sensitive-zones /tmp/broken.yaml` (파손 YAML) | 1 | blocked | `[]` | 17 | ✓ |
| `no-such-ref-abc..HEAD` (git RuntimeError) | 1 | blocked | `[]` | 17 | ✓ |
| (대조) `tests/fixtures/good/name-status.txt` | 0 | pass | `[check-change-intent, check-sensitive-zones]` | 17 | ✓ |
→ 보정이 픽스처 1건이 아니라 **예외 핸들러 전 경로**를 덮었고, 정상경로 동적성 무회귀.

### 음성검증 (rig-and-revert)
- `checked=[]` 원복(보정 전 과잉주장) → `evidence-error-missing-intent` **단독 FAIL 49/50**
- 오류카드 `changed_functions:[]` 삭제 → **단독 FAIL 49/50**
- 원복 → **50/50 PASS**
두 변조 모두 **기존 49 케이스 전원 통과** = D-031 의 "오류 카드 미검사 → 거짓확신" 주장이 실증됨. 신규 픽스처는 그 사각지대를 정확히 메운 **실가드**(항상-PASS 아님).

### 테스트 하네스 무력화 점검 (빈 리스트 함정)
`run-tests.sh` 가 `coverage_checked_gates`/`changed_functions` 를 `if "<key>" in expect` 로 검사함을 소스에서 확인 — `expect.get(...)` truthy 였다면 **빈 리스트 기대값이 조용히 스킵**되어 R-1 가드가 무의미했을 것. 실제로는 `[]` 도 비교된다(위 음성검증이 이를 재확인).

### 하류 영향
`coverage_statement` 는 사람 리뷰어가 30초 안에 읽는 감사카드의 신뢰 근거다. 오류 카드가 `checked:[]`·`policy_sha:{}`·`changed_files:[]` 로 **일관되게 "아무것도 못 봤다"** 를 말하게 되어, 후속 approval-routing/감사 로그가 오류 카드를 "3게이트 검사 완료된 blocked" 로 오독할 여지가 사라졌다.

### 비차단 관찰 (MVP-2 · 상세 A-0009)
- **O-2 → 차기 AC 가드 명시**: 오류 카드 `verdict_statement` 가 여전히 `governance violation detected`(실제론 tool error). A-0008 이 "권장·비필수" 로 못박아 보정사유 아님. §2B 필수질문=아니오(과대 진술·fail-closed → 통과 구멍 아님). 차기 AC: 중립 문구 + 회귀 픽스처.
- **O-3**: `check_function_gov_level` raise 시 2게이트 실행됐는데 `checked:[]` = 과소보고(보수적 → 비차단). 차기: 실행 게이트 누적기록.
- **O-4**: 오류 픽스처가 **부재 경로**를 트리거로 씀(무주석). 훗날 생성되면 테스트가 시끄럽게 실패 → 비차단. 차기: 주석 1줄.
- **O-1(이월)**: `schema_keys_match_template` top-level 한정. **AC #8(이월)**: 전체 policy 번들 digest.

### 검증 로그
`bash tests/run-tests.sh` **50/50 PASS** · `git diff --check` clean · `py_compile` OK — 전부 격리 worktree 재현. fresh 오류입력 3종·정상 대조 1종·음성검증 2종 직접 실행.

---

## TASK-023 intra-repo 정적 콜그래프 빌더 — **보정요청** (2026-07-15, D-052 · A-0018)

**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` 헤드 `92b2955`(구현 `2a6cd09`). **판정**: 보정요청 1건(🟠 블로킹) + 비차단 관찰 1건. 코드 머지 보류, 리뷰기록만 main.

### 통과분 (fresh 적대입력 실증 · 격리 worktree 재현)
- `tests/run-tests.sh` **81/81** · `kit/tests/run-entrypoint-tests.sh` **9/9** · `tests/mutation-check.sh` **131 기대변조 PASS** 전부 재현.
- **AC #1 해소**: `from app.utils import check_permission as allow`→`allow(user)`=`app.utils.check_permission` 엣지 · `from app.conditional import load_value`·동일모듈 bare 호출 정상.
- **AC #2 미해소 정직 노출**: `getattr(obj,name)()`→엣지 미추정·`unresolved_calls`+`coverage.unevaluated` 에 `kind=dynamic name=getattr(...)`. 내부 `getattr` builtin 은 BUILTIN_NAMES 로 걸러 미노출.
- **AC #3 결정론**: fixture 3회 md5 **동일**(`df9433d8c45372760a6da1bdb9a67087`).
- **AC #4 조건부 def union**: `if/else` 두 `load_value` 가 동일 id 로 합쳐져 엣지 `normalize`+`fallback` 양쪽. (단 **다른-id 동명**(모듈함수 vs 클래스메서드)은 union 아님 → R-1.)
- **음성검증**: `callgraph-repo-static` 기대 엣지 `format_report`→`WRONG_TARGET` 변조 → 케이스 **단독 FAIL(80/81)** = load-bearing.
- **동반 G-sink-1**: extract-sinks 2케이스가 `--sensitive-zones tests/fixtures/sinks/sensitive-zones.yaml`(fixture-local). fixture zone `services/settlement/**` frozen 이 `frozen:services.settlement.calculate.settle_async` auto-sink 실제 구동=inert 아님. 라이브 정책 결합 절단 달성(D-046 R-2 이월분).
- **동반 A-0017**: `warn_change_intent_shape`·`warn_output_location` echo 전용·판정 무영향(배너와 게이트 조립 사이·`sys.exit(0)` 은 python 서브프로세스만). 진입점 3케이스(경고 exit2·정상 무경고 absent·출력경고 exit0) load-bearing.
- **보수적 개발**: `policies/*`·Claude 소유 무접촉·scope-creep 없음. 변경=신규 게이트+tests+동반 2건.

### 🟠 R-1 (블로킹) — bare 모듈함수 호출이 동명 클래스메서드로 오해소 → 진짜 엣지 유실
- **위치**: `extract-callgraph.py` `CallVisitor.visible_local_names()`(231–237) + `resolve_repo_function()` `sorted(set(candidates))[0]`(229).
- **기전**: `visible_local_names` 가 모듈 내 **모든 클래스**에 `{class}.{name}` 후보 무조건 추가. 후보 최소(사전순) pick → 대문자 클래스명(0x43)이 소문자 함수명(0x66)보다 먼저 → 모듈함수 `foo`+`C.foo` 공존 시 bare `foo()`→`C.foo` 오해소.
- **fresh 실증 `adv1/app/m.py`**: `def foo`+`class C: def foo`+`def bar: return foo()` → 산출 `app.m.bar -> app.m.C.foo`(틀림), 정답 `app.m.bar -> app.m.foo` **부재**(`present: False`).
- **load-bearing 검증**: 클래스 확장 루프 제거한 사본 → `adv1` 교정(`bar->app.m.foo`) **+ 공식 fixture 7엣지 원본과 바이트 동일** = 이 루프는 정답 엣지에 대해 load-bearing 0, 오염만.
- **왜 비차단 불가(§2B)**: 모듈함수 sink 시 TASK-024 역도달 상류에서 호출자 누락 = 민감 변경 미포착(하류 직접 구멍). §2B 필수 "동명 오버로드" 적대세트가 제출 픽스처에 없음(conditional.py=동일-id 조건부만). AC #1·#4 불충족.
- **보정 ①권장**: ① 클래스 확장 루프 제거 ② 스코프조건+동명 union ③ 상설 회귀 픽스처(모듈함수 vs 동명 클래스메서드→모듈함수 엣지).

### 🟡 O-1 (비차단) — 중첩 데코레이터/기본인자 호출 조용한 유실
- `visit_function` 이 `node.body` 만 방문 → 중첩 정의의 `decorator_list`·기본인자 호출(함수 caller 명확) 유실. fresh `adv4`: `outer` 안 `@make_wrapper def inner` → `outer->make_wrapper` 부재·unresolved 에도 없음.
- 모듈-스코프는 정당 out-of-scope, 중첩은 좁고 틀린 엣지는 안 만듦 → 비차단. R-1 과 함께 고치거나 **TASK-025 고정 적대세트(데코레이터/기본인자)로 이월**(본 관찰이 AC 근거).

### 검증 로그
`tests/run-tests.sh` 81/81 · `kit/tests/run-entrypoint-tests.sh` 9/9 · `tests/mutation-check.sh` 131 · fixture md5 3회 동일 · fresh 적대입력 adv1/adv2/adv3/adv4 직접 실행 · 음성검증(엣지 변조 단독 FAIL) — 전부 격리 worktree `wt023` 재현.

---

## TASK-023 R-1 보정 재제출 재리뷰 — R-1 **부분해소** · R-2 잔여 **보정요청** (2026-07-15, D-053 · A-0019)

**대상**: 브랜치 `codex/2026-07-15-task023-callgraph` 헤드 `86eef67`(보정 impl `df7e54c`, docs `86eef67`). 선행 D-052/A-0018. **재리뷰 범위 = R-1 보정 델타(`df7e54c`) + 신설 픽스처만**(멱등성: `2a6cd09`·`92b2955` 재처리 금지). **판정**: R-1 의 **모듈-caller 케이스는 정확히 해소**되었으나, **동일 결함 클래스의 method-caller 변형이 잔존**(R-2, 🟠 블로킹) → **코드 머지 보류·리뷰기록만 main.**

### 보정 델타 (정확히 A-0018 권장 ①+③ 채택)
- `df7e54c`: `visible_local_names` 의 클래스 확장 루프 **2줄 제거**(권장 ①) + 상설 회귀 픽스처 `tests/fixtures/callgraph/repo/app/overloads.py`(모듈 `foo`+`class C: def foo`+`def bar: return foo()`) 신설(권장 ③) + `cases.yaml` 에 노드 3·엣지 `bar->foo` 단언. O-1 은 A-0018 허용대로 TASK-025 이월(handoff 명시).
- **보수적 개발 OK**: 델타 = 게이트 2줄 삭제 + 신규 픽스처 1 + cases 6줄. `policies/*`·Claude 소유·엔진 다른 경로 무접촉. scope-creep 없음.

### ✅ R-1 모듈-caller 케이스 해소 확인 (fresh 적대입력 · 격리 worktree 재현)
- `tests/run-tests.sh` **81/81 PASS**. 비교 로직 `assert_equal`(actual != expected)=**정렬 리스트 완전일치** → nodes/edges 완전집합 단언(spurious 엣지 즉시 FAIL). 강함.
- **음성검증(rig-and-revert)**: 제거한 클래스 확장 루프를 재삽입 → `callgraph-repo-static` **단독 FAIL(0/1)**, 원복 81/81 = 픽스처+수정 load-bearing(항상-PASS 아님).
- **fresh 픽스처 밖 입력**: 모듈 `foo` + `class C: def foo` + **class Zebra: def foo**(사전순 뒤 클래스로 순서독립 확인) + `def bar: return foo()` → 산출 엣지 `[app.m.bar -> app.m.foo]`, spurious `bar->` 엣지 **0개**. A-0018 원 R-1(adv1) 교정 확인.

### 🟠 R-2 (블로킹·잔여) — bare 호출이 **method 스코프 안에서** 동명 클래스메서드로 오해소 (R-1 과 동일 결함 클래스)
- **위치**: `CallVisitor.visible_local_names()`(231–235). 클래스 확장 루프는 제거됐으나, `for index … self.parents[:index]` 의 **parents-prefix 확장이 여전히 클래스명을 포함**한다. `CallVisitor.visit_ClassDef`(179)가 클래스명을 `self.parents` 에 push하기 때문.
- **기전**: caller 가 **메서드**면 `parents` 에 클래스명이 있어, bare 호출이 `{Class}.{name}` 후보를 만든다. `sorted(set)[0]` 이 대문자 클래스명(0x43)을 소문자 모듈함수(0x73 등)보다 먼저 pick → **형제 메서드로 오해소**. Python 의미상 **메서드 본문의 bare 이름은 클래스 스코프를 건너뛰고**(LEGB, 클래스 스코프 제외) 모듈/전역으로 바인딩되므로 이 해소는 **항상 틀림**.
- **fresh 실증(픽스처 밖)**: `def sink()`(모듈) + `class C: def sink(self); def caller(self): return sink()` → 산출 엣지 **`app.m.C.caller -> app.m.C.sink`(틀림·silently wrong)**, 정답 `C.caller -> 모듈 sink` **부재**, `unresolved_calls` 에도 **없음**(조용한 오염 — R-1 보다 나쁨: 누락이 아니라 *틀린 엣지 주입*). `self.sink()` 는 정직히 unresolved(정합), bare 만 오염.
- **왜 R-1 과 동일한 거버넌스 하류 구멍(§2B 필수질문=예)**: 모듈함수 `sink` 가 실제 sink 면, 이를 bare 로 호출하는 **메서드 caller 가 TASK-024 역도달 상류에서 누락**되고(정답 엣지 유실) 동시에 형제 메서드로 **거짓 엣지가 주입**된다 = 민감 변경 미포착. A-0018 R-1 이 없애려던 바로 그 실패모드("진짜 caller→sink 엣지 유실")를 method-caller 경로에서 그대로 재현.
- **거짓 커버리지 함정**: 신설 `overloads.py` 픽스처는 **모듈-caller `bar` 만** 단언(caller 가 모듈함수). method-caller 변형은 **미커버**라, "동명 오버로드 상설 픽스처를 추가했다"는 표기가 §2B 가 명령하는 커버리지를 **절반만** 채우면서 전체를 채운 듯한 확신을 준다.
- **왜 비차단 불가**: §2B "비차단 판정 전 필수질문 → 거버넌스에 직접 구멍 → 비차단 금지". 동일 결함 클래스이며 *틀린 엣지를 주입*하므로 R-1 보다 오히려 강한 오염. 저비용·국소로 닫힌다(아래 실증).
- **보정(택1·①권장, 소델타)**: ① `visible_local_names` 에서 **클래스 스코프를 건너뛴 parents-prefix만** 후보화(bare 이름은 클래스 스코프 미바인딩). 예: prefix 가 `self.class_names` 에 있으면 skip. **Claude 사본 실증**: 이 3줄 변경으로 `tests/run-tests.sh` **81/81 유지** + method-caller 케이스가 `C.caller -> 모듈 sink` 로 교정. ② method-caller 케이스에서 동명 충돌 시 pick-smallest 대신 모듈/전역 우선(또는 union). ③ **상설 회귀 픽스처를 method-caller 변형으로 확장**: 같은 모듈에 모듈 `sink`+`class C{def sink; def caller: sink()}` → 엣지가 **모듈 sink 로** 가고 `C.caller->C.sink` 는 없음을 단언. (§2B "동명 오버로드" 상설화 완성.)

### 🟡 O-1 (비차단·유지) — 중첩 데코레이터/기본인자 호출 조용한 유실
- A-0018 O-1 그대로. Codex 가 A-0018 허용대로 **TASK-025 고정 적대세트로 이월** 선언(handoff `86eef67`). 재확인·수용. 틀린 엣지 없이 누락만 → 비차단 유지.

### 재제출 지침 (멱등)
- 재리뷰는 **R-2 보정 델타 + method-caller 회귀 픽스처만**. 통과분(R-1 모듈-caller 해소·엔진 본체·getattr·결정성·조건부 union·G-sink-1·A-0017)은 재검 없음. 멱등성: `df7e54c`·`86eef67` **재처리 금지**.
- ⚠️ **재제출 전 `origin/main` merge 필수**. 이번 재제출도 `origin/main`(D-052/A-0018 리뷰기록 포함) 미병합 상태로 올라와, 브랜치가 main 대비 `A-0018.md`·D-052·review-notes 를 **삭제**하는 형태였다(D-050 함정 2회째). 머지자가 3-way 로 보존 가능하나(main 단독 추가분 유지), **다음 재제출은 반드시 `origin/main` 먼저 merge**(collab-protocol §5.1).

### 검증 로그
`tests/run-tests.sh` 81/81(worktree `wt-task023`) · 음성검증(클래스 확장 루프 재삽입→callgraph 케이스 단독 FAIL 0/1) · fresh 적대입력: 모듈-caller(Zebra 순서독립·spurious 0), method-caller(`C.caller->C.sink` 오염 재현), `self.sink()`(정직 unresolved) 직접 실행 · **후보수정 실증**(class-스코프 skip 3줄 → 81/81 유지 + method-caller 교정) — 전부 격리 worktree 재현.
