# docs/adr/ — 아키텍처 결정 기록 (ADR)

하네스의 배포·계약 관련 굵직한 설계 결정을 기록한다. 코드 게이트 태스크(TASKS.md)와 별개로,
"판정을 어떤 형태로 내보내나", "kit/어댑터 계약은 무엇인가" 같은 **구조 결정**을 남긴다.

| # | 제목 | 상태 |
|---|---|---|
| [ADR-001](ADR-001-verdict-status.md) | 판정 상태 의미론 (status/analysis_state/disposition 3축) | Accepted |
| [ADR-002](ADR-002-result-evidence-schema.md) | result/evidence 스키마 (검증 2층 분리) | Accepted |

> 작성 규약: Claude 가 정책·설계 판단으로 초안 → 형 승인 시 Accepted.
> 불변 원칙(CLAUDE.md §4: 결정론·2·3층 자동차단 금지·fail-closed)을 어기는 결정은 둘 수 없다.
