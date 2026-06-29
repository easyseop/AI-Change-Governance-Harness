# decisions.md — 확정 결정 (대화 ≠ 결정. 여기 적힌 것만 확정)

> Q/A 에서 합의된 것을 결정으로 승격한다. 번호·날짜·근거를 남긴다.

---

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
