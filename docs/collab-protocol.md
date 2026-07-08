# 협업 프로토콜 — Claude ↔ Codex (Git 비동기)

> 두 AI는 **직접 대화하지 않는다.** 같은 repo의 파일을 통해 비동기로 주고받는다.
> 이 협업 구조 자체가 변경 거버넌스의 dogfooding(자기적용)이다.

## 1. 역할·소유 파일 (충돌 방지의 1차 수단)

| | Claude | Codex |
|---|---|---|
| 역할 | 판단/정책/리스크/리뷰 | 구현/테스트/게이트 |
| 소유 | `docs/*`, `policies/*`(초안), `CLAUDE.md`, `templates/*`, `collab/decisions.md`, `collab/answers/*` | `AGENTS.md`, `.harness/gates/*`, `tests/*`, 실행 README, `collab/questions/*` |
| 공유(조심) | `PROJECT.md`, `TASKS.md`, `collab/handoff-log.md`, `collab/locks.yaml` | (좌동) |

**상대 소유 파일은 수정하지 않는다.** 바꿔야 하면 질문/handoff로 요청.
공통 소유(형): `COMMON-RULES.md`(두 AI 읽기전용). 공동 출력(둘 다 추가): `summaries/*`, `collab/needs-human/*`.

## 2. 브랜치 (충돌 방지의 2차 수단)
**단일 장수 브랜치를 쓰지 않는다. 작업 단위마다 날짜별 브랜치를 판다** (`COMMON-RULES.md` §2).
```
main                          ← 합의된 것만 (직접 push 금지, 리뷰 통과 후 머지)
codex/<YYYY-MM-DD>-<주제>      ← Codex 작업 (base=최신 main)
claude/<YYYY-MM-DD>-<주제>     ← Claude 작업/리뷰 (base=최신 main)
```
가능하면 git worktree로 작업 디렉터리 분리. 커밋/푸시는 상세히(`COMMON-RULES.md` §3).

## 3. 질문/답변 큐
- 막히는 결정은 `collab/questions/Q-XXXX.md` 에 남긴다 (`Status: open`, `Blocking: true/false`).
- 답하는 쪽은 `collab/answers/A-XXXX.md` 작성 후, 질문의 `Status: answered` 로 변경.
- **자기에게 온 `open` 질문만** 처리. 답한 질문 재처리 금지.
- 일상 인계(비-blocking)는 질문 만들지 말고 `handoff-log.md` 에 한 줄.

## 4. 결정 승격
- 대화(Q/A)에서 합의된 것은 `collab/decisions.md` 에 **결정으로 승격**한다. (대화 ≠ 결정)
- decisions.md 에 적힌 것만 "확정"이다.

## 5. 🛑 자동화(N분 watcher) 전 필수 안전장치
watcher는 **나중에.** 처음엔 명시적 handoff로 시작한다. 자동 루프 도입 전 아래가 전부 있어야 함:

| 안전장치 | 규칙 |
|---|---|
| 멱등성 | 처리한 마지막 commit hash를 `handoff-log.md`에 기록, 같은 변경 재처리 금지 |
| 종료성 | 자기에게 온 `open`만 처리, 답하면 `answered` |
| 진동 방지 | 한 질문 재오픈 ≥3회 → 사람 에스컬레이션 (ping-pong 차단) |
| 사람 차단기 | repo 루트 `STOP` 파일 존재 시 두 AI 모두 즉시 중단 |
| 예산 한도 | 세션당 최대 라운드/토큰/시간 상한 |
| **자기 머지 금지** | `main` 머지는 상대 리뷰=approved 필수. 비민감은 리뷰어(Claude)가 머지, 민감변경은 사람 승인 필요 (D-007) |
| 충돌 안전 | 상대 소유/락 파일 수정 금지, 자기 브랜치에만 commit |
| **보정 재제출 동기화** | 보정요청 시 리뷰기록은 `main` 에만 있고 코드 브랜치엔 없다 → 재제출 전 반드시 `origin/main` 동기화 (아래 §5.1) |

## 5.1 🔴 보정 재제출 동기화 (D-029 재발방지 — "예전엔 됐는데" 함정)
**증상**: Claude 가 보정요청하면 리뷰기록(`answers/A-XXXX`·`decisions`·`handoff` 최상단 보정요청 줄)을 **`main` 에 머지**한다(코드 브랜치는 보류). 그런데 Codex 는 **자기 코드 브랜치 위에서** 보정 재제출한다. 그 브랜치가 분기 후 `main` 을 한 번도 안 물었으면 **보정요청 파일이 브랜치에 아예 없어** Codex 가 못 본다(handoff 최상단이 자기 'done/재제출' 줄로 보임).
**왜 예전엔 됐나**: 리뷰통과→머지 흐름은 매 태스크 **새 브랜치를 `main` 에서 새로 따** 자동 동기화됐다. **같은 브랜치 보정 재제출**에서만 링크가 끊긴다.
**규칙**:
1. **Codex(재제출자)**: 보정 착수 전 **`git fetch origin && git merge origin/main`**(또는 rebase)로 최신 리뷰기록을 자기 브랜치에 유입한 뒤, `collab/answers/A-XXXX.md`(수정계약)·`handoff-log.md` 최상단 보정요청 줄을 읽고 **보정 델타만** 재제출(멱등성).
2. **Claude(리뷰어) 백스톱**: 보정요청을 낼 때, 코드 브랜치가 `main` 뒤처져 Codex 가 기록을 못 볼 위험이 있으면 — 형 승인 하에 **`origin/main` 을 코드 브랜치로 머지·push**(리뷰기록·정책만 유입, **코드/픽스처 0 변경** 확인 후). 충돌은 `handoff`(시간역순 합집합)·`summaries`(섹션 합집합)로 해소.
3. handoff 최상단 보정요청 줄은 **`[날짜] Claude → Codex | <commit> (**보정요청**) | …`** 형식 유지(§CLAUDE.md 2B) — Codex 가 새 태스크로 오인하지 않게 하는 감지 신호.

## 6. locks.yaml (보조 수단)
파일 편집 전 `collab/locks.yaml` 에 `path: <소유자> <시각>` 갱신. advisory라 약하므로 **브랜치 분리(§2)가 진짜 방어선**.

## 7. 한 줄
**소유 분리 → 브랜치 분리 → 질문/답변 → 결정 승격. 자동화는 안전장치 다 깔린 뒤에.**
