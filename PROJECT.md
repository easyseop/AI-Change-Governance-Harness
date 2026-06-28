# PROJECT.md — AI Change Governance Harness (공동 현황판)

> Claude·Codex·사람이 함께 보는 단일 현황판. 상세 작업은 `TASKS.md`, 결정은 `collab/decisions.md`.

## 목표
AI가 만든 코드 변경이 **의도 범위 안인지 / 민감 영역을 건드렸는지** 결정적으로 가려,
사람이 **위험 변경 후보만** 보게 한다. (전수 diff 검토 불가 문제 해결)

## 현재 단계: MVP-0 (경로+YAML 기반, 언어무관)
범위: change-intent↔diff 비교 · sensitive-zones 충돌 · 감사카드 · 리뷰어 라우팅.
(능력/데이터 패턴 감지 = MVP-1, 영향범위/scope-creep = MVP-2)

## 역할
| | Claude | Codex | 사람(형) |
|---|---|---|---|
| 일 | 정책·리스크·리뷰 | 게이트 구현·테스트 | repo 생성·Codex 실행·조직 정책값 확정 |

## 진행 상태
| 영역 | 담당 | 상태 |
|---|---|---|
| 설계·리스크 기준 (`docs/`, `CLAUDE.md`) | Claude | ☑ 초안 완료 |
| 정책 초안 (`policies/*.yaml`) | Claude | ☑ 초안 완료 (조직값은 🟡 미정) |
| 감사카드 스키마 (`templates/`) | Claude | ☑ 완료 |
| 협업 골격 (`collab/`, 프로토콜) | Claude | ☑ 완료 |
| Codex 지시서 (`AGENTS.md`,`TASKS.md`) | Claude | ☑ 완료 |
| 게이트 3종 (`.harness/gates/*`) | **Codex** | ☐ 대기 (TASK-001~003) |
| 테스트 (`tests/*`) | **Codex** | ☐ 대기 (TASK-004) |

## 다음 행동 (순서)
1. (사람) 이 repo 를 GitHub 에 push.
2. (사람) Codex 를 이 repo 에 붙이고 `AGENTS.md` 읽힘 → TASK-001 시작.
3. (Codex) 게이트 구현 → `handoff-log.md` 기록.
4. (Claude) 수용기준 대비 리뷰 → `decisions.md`.
5. 반복. 완료 정의: `run-tests.sh` 6/6 + 전 TASK 리뷰통과.

## 미해결 결정 (decisions.md 로 승격 대기)
- 능력 카탈로그 감지 신호(MVP-1) · 공유모듈 blast-radius 근사식 · scope-creep 점수화.
