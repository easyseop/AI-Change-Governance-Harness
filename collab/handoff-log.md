# handoff-log.md — 인계 기록 (시간 역순으로 위에 추가)

> 형식: `[YYYY-MM-DD] <보낸이> → <받는이> | <commit hash> | 요약`
> 멱등성: 처리한 마지막 commit hash 를 여기 남겨 같은 변경 재처리를 막는다.

---

- [2026-06-28] Claude(형 지시) → Codex | (setup) | 공통규칙 도입: `COMMON-RULES.md` 신설(은행운영 관점·보수적개발 평가축·날짜별 브랜치·상세 커밋·요약 누적·형 판단 큐·형의 요구사항). `summaries/`·`collab/needs-human/` 신설. START-HERE/CLAUDE/AGENTS/collab-protocol/README/PROJECT 동기화.
  → Codex 는 이제 `COMMON-RULES.md` 도 필독. 날짜별 브랜치 `codex/<날짜>-<주제>` 에서 작업, 푸시마다 `summaries/<날짜>.md` 누적.
- [2026-06-28] Claude → Codex | (initial scaffold) | MVP-0 스캐폴딩 완료. 정책·설계·협업골격·지시서 작성.
  Codex 는 `AGENTS.md` → `TASKS.md` 순으로 읽고 TASK-001(check-change-intent)부터 시작.
