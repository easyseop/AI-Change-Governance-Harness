# AGENTS.md — Codex 작업 대본 (AI Change Governance Harness)

> 🔴 **필독 · 새 세션이면**: 먼저 `START-HERE.md` 의 "네가 Codex 면" 절 → **`COMMON-RULES.md`(공통규칙·형의 요구사항)** 를 읽어라(읽는 순서·첫 할 일 TASK-001·구현 계약).
> 이 파일은 그 역할의 **상세 규정**이다. 맥락이 없어도 `START-HERE.md` → `COMMON-RULES.md` → 이 파일 → `TASKS.md` 순으로 읽으면 바로 구현을 시작할 수 있다.

> 이 repo에서 **Codex의 역할 = 구현/테스트/게이트.** 정책·리스크 판단은 Claude 가 한다(`CLAUDE.md`).
> Codex는 정책 *값*을 임의로 정하지 않는다 — 막히면 `collab/questions/` 로 Claude 에게 묻는다.

## 1. 먼저 읽을 것 (순서)
1. `COMMON-RULES.md` — 🔴 공통규칙(필독): 은행운영 관점·보수적개발·브랜치/커밋/요약·형의 요구사항
2. `docs/change-governance-design.md` — 무엇을 왜 만드는가 (MVP-0 범위)
3. `TASKS.md` — 네가 만들 4개 태스크 + **수용기준**
4. `docs/collab-protocol.md` — 협업·충돌방지·안전장치
5. `policies/*.yaml` — 게이트가 읽을 정책 (Claude 초안)

## 2. Codex 소유 파일 (여기만 만든다/고친다)
```
.harness/gates/check-change-intent.py
.harness/gates/check-sensitive-zones.py
.harness/gates/generate-change-evidence.py
tests/fixtures/*
tests/cases.yaml
tests/run-tests.sh
README.md (실행 방법 절)
AGENTS.md (이 파일)
collab/questions/*
```
**건드리지 말 것**: `docs/*`, `policies/*`, `CLAUDE.md`, `templates/*`, `collab/decisions.md`, `collab/answers/*`, **공통 소유 `COMMON-RULES.md`(형)**.
공동 출력(너도 추가): `summaries/<날짜>.md`(푸시마다 작업요약 누적), `collab/needs-human/H-XXXX.md`(형 판단 필요 시).
정책/스키마를 바꿔야 하면 → 직접 고치지 말고 질문.

## 3. 작업 방식
- **날짜별 브랜치** `codex/<YYYY-MM-DD>-<주제>` 에서만 작업 (단일 브랜치 금지, base=최신 main). `main` 직접 push 금지. — `COMMON-RULES.md` §2.
- **상세 커밋/푸시**(§3): 무엇을·왜·무엇을 고쳤는지 본문에 기록.
- **보수적 개발**(§1): 요청 범위(change-intent) 밖 파일·무관한 리팩터/포맷 변경 금지, 최소 diff.
- 한 TASK 끝나면 `collab/handoff-log.md` 에 `[TASK-00X done] <commit hash> — 요약` 기록 + `summaries/<날짜>.md` 에 요약 누적.
- 그 뒤 Claude 리뷰 대기 (`collab/decisions.md` 에 통과/보정 적힘).
- 정책 판단은 `collab/questions/Q-XXXX.md`(→Claude). 형 판단/승인은 `collab/needs-human/H-XXXX.md`(→형).

## 4. 구현 가이드 (MVP-0)
- Python3 + pyyaml. 기존 은행 킷(`gates/*.sh` 안의 python 인라인)과 톤 맞춤.
- diff 는 `git diff --name-status <base>..<head>` 와 `--numstat` 수준만 사용.
  **내용/AST 분석·LLM 호출 금지** (그건 MVP-1).
- 종료코드 약속: **0 통과 / 1 차단 / 2 승인필요**.
- 결정적: 같은 입력 = 같은 출력.

## 5. 🛑 안전장치 (collab-protocol §5 준수)
- repo 루트 `STOP` 파일 있으면 즉시 중단.
- 자기 머지 금지: `main` 머지는 Claude 리뷰 통과(+민감변경은 사람 승인) 후에만.
- 상대 소유/락 파일 수정 금지. 처리한 마지막 commit hash 기록(멱등성).

## 6. 완료의 정의 (MVP-0)
TASK-001~004 전부 수용기준 충족 + `tests/run-tests.sh` 6/6 PASS + Claude 리뷰통과(decisions.md).
