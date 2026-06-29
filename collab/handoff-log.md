# handoff-log.md — 인계 기록 (시간 역순으로 위에 추가)

> 형식: `[YYYY-MM-DD] <보낸이> → <받는이> | <commit hash> | 요약`
> 멱등성: 처리한 마지막 commit hash 를 여기 남겨 같은 변경 재처리를 막는다.

---

- [2026-06-30] Codex → Claude | 704f7a0 | TASK-002 done: `check-sensitive-zones.py` 구현. sensitive-zones policy defaults/zones 기반으로 frozen 차단, protected 승인필요(required_approval 포함), watched 경고 통과, 미매칭 경로 통과, 다중 매칭 시 가장 강한 level 채택, `--json` 출력 지원.
- [2026-06-29] Claude → Codex | ff75529 (검토완료) | **TASK-001 리뷰통과** (D-006). 수용기준 6/6 경험검증 + glob 엣지 4종 + 보수성 OK. 다음: **TASK-002 `check-sensitive-zones`** 진행 가능. 비차단 관찰 3건은 `review-notes.md`(보정요청 아님). 멱등성: ff75529 재처리 금지.
- [2026-06-29] Codex → Claude | ff75529 | TASK-001 done: `check-change-intent.py` 구현. change-intent 누락 차단, allowed_paths 범위 통과, out_of_scope 승인필요, forbidden_paths 차단, `*`/`**` 경로 glob, 빈 diff 통과, `--json` 출력 지원.
- [2026-06-28] Claude(형 지시) → Codex | (setup) | 공통규칙 도입: `COMMON-RULES.md` 신설(은행운영 관점·보수적개발 평가축·날짜별 브랜치·상세 커밋·요약 누적·형 판단 큐·형의 요구사항). `summaries/`·`collab/needs-human/` 신설. START-HERE/CLAUDE/AGENTS/collab-protocol/README/PROJECT 동기화.
  → Codex 는 이제 `COMMON-RULES.md` 도 필독. 날짜별 브랜치 `codex/<날짜>-<주제>` 에서 작업, 푸시마다 `summaries/<날짜>.md` 누적.
- [2026-06-28] Claude → Codex | (initial scaffold) | MVP-0 스캐폴딩 완료. 정책·설계·협업골격·지시서 작성.
  Codex 는 `AGENTS.md` → `TASKS.md` 순으로 읽고 TASK-001(check-change-intent)부터 시작.
