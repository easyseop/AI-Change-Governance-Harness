# handoff-log.md — 인계 기록 (시간 역순으로 위에 추가)

> 형식: `[YYYY-MM-DD] <보낸이> → <받는이> | <commit hash> | 요약`
> 멱등성: 처리한 마지막 commit hash 를 여기 남겨 같은 변경 재처리를 막는다.

---

- [2026-06-28] Claude → Codex | (initial scaffold) | MVP-0 스캐폴딩 완료. 정책·설계·협업골격·지시서 작성.
  Codex 는 `AGENTS.md` → `TASKS.md` 순으로 읽고 TASK-001(check-change-intent)부터 시작.
