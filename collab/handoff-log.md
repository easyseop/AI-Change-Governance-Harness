# handoff-log.md — 인계 기록 (시간 역순으로 위에 추가)

> 형식: `[YYYY-MM-DD] <보낸이> → <받는이> | <commit hash> | 요약`
> 멱등성: 처리한 마지막 commit hash 를 여기 남겨 같은 변경 재처리를 막는다.

---

- [2026-07-01] Codex → Claude | 86c9a75 | TASK-005 done: `extract-python-inventory.py` 구현. Python AST 기반으로 함수/클래스 정규화 이름(`Class.method`, `outer.inner`), 시작/끝 라인, 데코레이터 목록을 결정적으로 출력하고, 문법 오류는 예외 없이 빈 인벤토리+`parse_error`로 반환한다. `tests/run-tests.sh`에 TASK-005 fixture 2개를 추가해 기존 MVP-0 6개 포함 `8/8 PASS` 확인.
- [2026-07-01] Claude → Codex | 93e2c40 (검토완료·머지) | **TASK-004 리뷰통과** (D-010). 수용기준 4/4 경험검증(`run-tests.sh` 6/6 PASS, exit 0) + fixture↔policy 정합(rigged 아님) + 음성검증(기대 변조→FAIL/exit1) + 보수성 OK. **비민감(테스트 하네스·문서) → Claude 가 main 머지·push** (구현자≠머지자). **MVP-0 게이트 4종 완료.** 다음: 형 지시/MVP-1 대기 — review-notes(TASK-004) 비차단 관찰 #1(evidence blocked/approval 케이스 추가) 참고. 멱등성: 93e2c40 재처리 금지.
- [2026-06-30] Codex → Claude | abc47ef | TASK-004 done: `tests/fixtures/*`, `tests/cases.yaml`, `tests/run-tests.sh` 구현. good/out-of-scope/forbidden/frozen/protected/watched 6개 fixtures를 추가하고, 세 게이트를 실제 실행해 기대 verdict/exit_code/핵심 출력 필드를 검증한다. `bash tests/run-tests.sh` 결과 6/6 PASS.
- [2026-06-30] Claude → Codex | f2ecb50 (검토완료·머지) | **TASK-003 리뷰통과** (D-009). 수용기준 5/5 경험검증(시나리오 8종+실제 git ref) + 엣지/결정성/fail-closed + 보수성 OK. **비민감(하네스 게이트 코드) → Claude 가 main 머지·push** (구현자≠머지자). 다음: **TASK-004 테스트 fixtures + 러너** 진행 가능 — review-notes(TASK-003) #2(numstat 동반)·verdict 기대(pass/blocked/approval_required) 정합 유지. 멱등성: f2ecb50 재처리 금지.
- [2026-06-30] Codex → Claude | f2ecb50 | TASK-003 done: `generate-change-evidence.py` 구현. name-status/numstat 기반으로 change-evidence YAML 생성, change-intent/sensitive-zones/approval-routing policy 로딩, zone_level/in_allowed_paths/summary/base_commit 기록, blocked/approval_required/pass verdict 합성, reviewer_required 중복 제거를 지원.
- [2026-06-30] Claude → Codex | 704f7a0 (검토완료·머지) | **TASK-002 리뷰통과** (D-008). 수용기준 6/6 경험검증 + 엣지 6종 + 보수성 OK. **비민감(하네스 게이트 코드) → Claude 가 main 머지·push** (구현자≠머지자). 다음: **TASK-003 `generate-change-evidence`** 진행 가능 — review-notes #2(reviewer 중복제거)·verdict 합성 정합 유지. 멱등성: 704f7a0 재처리 금지.
- [2026-06-30] Codex → Claude | 704f7a0 | TASK-002 done: `check-sensitive-zones.py` 구현. sensitive-zones policy defaults/zones 기반으로 frozen 차단, protected 승인필요(required_approval 포함), watched 경고 통과, 미매칭 경로 통과, 다중 매칭 시 가장 강한 level 채택, `--json` 출력 지원.
- [2026-06-29] Claude → Codex | ff75529 (검토완료) | **TASK-001 리뷰통과** (D-006). 수용기준 6/6 경험검증 + glob 엣지 4종 + 보수성 OK. 다음: **TASK-002 `check-sensitive-zones`** 진행 가능. 비차단 관찰 3건은 `review-notes.md`(보정요청 아님). 멱등성: ff75529 재처리 금지.
- [2026-06-29] Codex → Claude | ff75529 | TASK-001 done: `check-change-intent.py` 구현. change-intent 누락 차단, allowed_paths 범위 통과, out_of_scope 승인필요, forbidden_paths 차단, `*`/`**` 경로 glob, 빈 diff 통과, `--json` 출력 지원.
- [2026-06-28] Claude(형 지시) → Codex | (setup) | 공통규칙 도입: `COMMON-RULES.md` 신설(은행운영 관점·보수적개발 평가축·날짜별 브랜치·상세 커밋·요약 누적·형 판단 큐·형의 요구사항). `summaries/`·`collab/needs-human/` 신설. START-HERE/CLAUDE/AGENTS/collab-protocol/README/PROJECT 동기화.
  → Codex 는 이제 `COMMON-RULES.md` 도 필독. 날짜별 브랜치 `codex/<날짜>-<주제>` 에서 작업, 푸시마다 `summaries/<날짜>.md` 누적.
- [2026-06-28] Claude → Codex | (initial scaffold) | MVP-0 스캐폴딩 완료. 정책·설계·협업골격·지시서 작성.
  Codex 는 `AGENTS.md` → `TASKS.md` 순으로 읽고 TASK-001(check-change-intent)부터 시작.
