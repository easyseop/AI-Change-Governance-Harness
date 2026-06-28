# .harness/gates/ — 게이트 (Codex 구현 영역)

> 이 폴더는 **Codex 가 채운다.** Claude 는 비워둔다(상호견제).
> 구현 명세·수용기준은 `../../TASKS.md`, 역할은 `../../AGENTS.md`.

MVP-0 에서 만들 게이트:

| 파일 | 태스크 | 한 줄 |
|---|---|---|
| `check-change-intent.py` | TASK-001 | diff 가 change-intent 의도 범위 밖/forbidden 을 건드렸나 |
| `check-sensitive-zones.py` | TASK-002 | diff 가 민감 경로(frozen/protected/watched)를 건드렸나 |
| `generate-change-evidence.py` | TASK-003 | 위 결과+routing 으로 변경 감사카드 생성 |

종료코드 약속: **0 통과 / 1 차단 / 2 승인필요**. 결정적(추정·LLM 금지).
