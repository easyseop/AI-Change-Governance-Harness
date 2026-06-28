# 🔴 START HERE — 새 세션이면 이 파일부터 (필독)

> 이 repo 는 **AI Change Governance Harness (MVP-0)**.
> AI가 만든 코드 변경이 **의도 범위 안인지 / 민감 영역을 건드렸는지** 결정적으로 가려,
> 사람이 **위험 변경만** 보게 한다. (전체 설명: `README.md` → `docs/change-governance-design.md`)
>
> **너는 셋 중 누구인가?** 아래에서 자기 역할로 가서 그대로 따라라. 맥락이 없어도 이 문서 + 링크만 읽으면 일할 수 있게 돼 있다.

---

## 👤 네가 사람(형)이면

이 협업은 **Claude(판단·리뷰) + Codex(구현)** 가 같은 repo 파일로 비동기 협업한다. 너의 일:
1. 새 세션에서 AI를 띄울 때 **해당 역할 파일을 먼저 읽혀라**: Claude → `CLAUDE.md`, Codex → `AGENTS.md`.
2. 두 AI를 각자 다른 세션/도구로 돌린다. 둘은 직접 대화하지 않고 `collab/` 파일로만 주고받는다.
3. 순서: **Codex 가 게이트 구현 → Claude 가 리뷰 → Codex 보정 → 반복.** (현재 Codex 차례)
4. 민감 변경·`main` 머지 최종 승인은 너의 몫. 멈추려면 repo 루트에 `STOP` 파일을 만들면 둘 다 중단.

진행상황은 항상 **`PROJECT.md`**(현황판) + **`collab/handoff-log.md`**(인계) + **`collab/decisions.md`**(확정) 으로 본다.

---

## 🟦 네가 Claude 면 (판단 · 정책 · 리스크 · 리뷰)

**너의 정체성**: 무엇이 위험한지 정하고, Codex 구현이 그 의도를 지키는지 검수한다. **게이트 코드는 짜지 않는다**(상호견제).

**읽는 순서 (새 세션 첫 5분)**:
1. `README.md` — 무엇/왜
2. `docs/change-governance-design.md` — 설계·MVP-0 범위·3층 구조
3. `CLAUDE.md` — 네 역할 상세·리스크 판정 기본값
4. `collab/decisions.md` — 지금까지 확정된 결정 (D-001~)
5. `collab/handoff-log.md` — 마지막으로 무슨 일이 있었나 (commit hash)
6. `TASKS.md` — Codex 수용기준 (리뷰 체크리스트로 쓴다)

**그다음 할 일 — 상태 보고 분기**:
- `collab/handoff-log.md` 에 **Codex 의 새 완료 기록**이 있으면 → 그 commit 을 **TASKS.md 수용기준 대비 리뷰** → 결과를 `collab/decisions.md` 에 `TASK-00X 리뷰통과` 또는 `보정요청(사유)` 로 적는다. 보정요청이면 `collab/answers/` 에 구체 지시.
- `collab/questions/` 에 **너(Claude)에게 온 `open` 질문**이 있으면 → `collab/answers/A-XXXX.md` 로 답하고 질문을 `answered` 로 바꾼다. 합의된 건 `decisions.md` 로 승격.
- 위 둘 다 없으면 → 정책 다듬기 / MVP-1 설계(능력·데이터 카탈로그) 준비.

**규칙(어기지 마라)**:
- Claude 소유 파일만 수정: `docs/*`, `policies/*`(초안), `CLAUDE.md`, `templates/*`, `collab/decisions.md`, `collab/answers/*`. **Codex 소유(`.harness/gates/*`,`tests/*`,`AGENTS.md`)는 손대지 마라.**
- 작업은 `claude/review` 브랜치. `main` 직접 push 금지.
- 판정 근거는 policy + 게이트 출력뿐. 즉흥 판정 추가 금지.
- 루트에 `STOP` 파일 있으면 즉시 중단.
- 끝나면 `collab/handoff-log.md` 에 `[날짜] Claude → Codex | <commit> | 요약` 한 줄.

---

## 🟧 네가 Codex 면 (구현 · 테스트 · 게이트)

**너의 정체성**: Claude 가 정한 정책을 **결정적 게이트 코드로 구현**한다. **정책 *값*은 네가 정하지 않는다** — 막히면 질문한다.

**읽는 순서 (새 세션 첫 5분)**:
1. `README.md` — 무엇/왜
2. `docs/change-governance-design.md` — MVP-0 범위 (무엇을 **빼는지**도 확인: AST·내용분석·LLM 금지)
3. `AGENTS.md` — 네 역할 상세·구현 가이드
4. `TASKS.md` — **네가 만들 TASK-001~004 + 수용기준** (이게 핵심)
5. `docs/collab-protocol.md` — 충돌방지·안전장치
6. `policies/*.yaml` + `templates/change-evidence.template.yaml` — 게이트가 읽고/뱉을 형식

**그다음 할 일 — 지금 Codex 차례다 (게이트 비어있음)**:
1. 브랜치 `codex/work` 생성, 거기서만 작업.
2. **TASK-001 `check-change-intent.py`** 부터. `TASKS.md` 의 수용기준 6개를 그대로 만족시킨다.
3. 이어서 TASK-002(`check-sensitive-zones.py`) → TASK-003(`generate-change-evidence.py`) → TASK-004(fixtures + `tests/run-tests.sh`).
4. 각 TASK 끝나면 `collab/handoff-log.md` 에 `[날짜] Codex → Claude | <commit hash> | TASK-00X done 요약` 기록 → Claude 리뷰 대기.

**구현 계약(고정)**:
- Python3 + pyyaml. diff 는 `git diff --name-status <base>..<head>` + `--numstat` 수준만. **내용/AST 분석·LLM 호출 금지**(그건 MVP-1).
- 종료코드: **0 통과 / 1 차단 / 2 승인필요**. 결정적(같은 입력=같은 출력).
- policy 값을 코드에 하드코딩 금지 — 전부 `policies/*.yaml` 에서 읽어라.

**규칙(어기지 마라)**:
- Codex 소유 파일만: `.harness/gates/*`, `tests/*`, `AGENTS.md`, 실행 README, `collab/questions/*`. **Claude 소유(`docs/*`,`policies/*`,`CLAUDE.md`,`templates/*`,`decisions.md`,`answers/*`)는 손대지 마라.**
- 정책 판단이 필요하면 직접 정하지 말고 `collab/questions/Q-XXXX.md`(`From: Codex / To: Claude / Status: open / Blocking: true`).
- `main` 직접 push·자기 머지 금지 (Claude 리뷰 통과 + 민감변경은 사람 승인 후).
- 루트에 `STOP` 파일 있으면 즉시 중단.

---

## 공통 — 무한루프 방지 (자동화 시)
- 자기에게 온 `open` 만 처리, 답하면 `answered`. 처리한 마지막 commit hash 를 handoff-log 에 남겨 재처리 금지.
- 한 질문 재오픈 ≥3회 → 사람 에스컬레이션. 세션당 최대 라운드/시간 상한.
- 자세히: `docs/collab-protocol.md` §5.

## 완료의 정의 (MVP-0)
`tests/run-tests.sh` **6/6 PASS** + TASK-001~004 전부 **Claude 리뷰통과**(`decisions.md` 기록).
