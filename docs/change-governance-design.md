# AI Change Governance Harness — 설계 (MVP-0)

> 이 문서는 **Claude(판단/정책/리스크 역할)** 가 소유한다.
> 구현(게이트 코드)은 Codex가 소유한다. 이 문서는 "무엇을 왜 위험하다고 보는가"를 정의한다.

작성일: 2026-06-28 · 상태: MVP-0 draft

---

## 0. 한 줄 정의

> AI가 만든 코드 변경(diff)이 **선언한 의도 범위 안에 머물렀는지**, **민감 영역을 건드렸는지**
> 를 결정적으로 가려내, 사람이 **위험 변경 후보만** 보게 하는 하네스.

목표는 "모든 diff 전수검토(불가능)"가 아니라 **"사람의 주의를 좁히는 것"**.

---

## 1. 핵심 원칙 (논의에서 확정)

1. **민감함은 "어디(경로)"가 아니라 "무엇을 하느냐(능력)·무슨 데이터를 만지느냐"** 가 진짜 기준이다.
   경로는 약한 대리표지일 뿐 — MVP-0은 경로로 시작하되, 능력/데이터는 MVP-1로 확장한다.
2. **전수 분류하지 않는다.** 왕관보석(소수 치명 구역)만 울타리 친다. 99%는 자유.
3. **공유 모듈은 "민감 모듈"이 아니라 "영향범위 큰 모듈"** 로 다룬다 (분류 대신 도달범위 표시).
4. **확신도별 3층**으로 나눠 오탐/미탐을 관리한다 (아래 §3).
5. **이 하네스의 규칙을 이 협업 repo 자신에게 적용한다(dogfooding).** 자기 머지 금지 등.

---

## 2. 무엇을 묻는가 (요구 질문)

```
무엇을 바꿨는가 / 왜 / 의도 범위 안인가 /
민감 파일·기능을 건드렸는가 / 건드리면 안 되는 곳인가 /
새 민감 능력을 도입했는가 / PII·secret을 새로 다루는가 /
공유모듈 변경으로 영향범위가 커졌는가 / 승인자가 필요한가 / 증적이 남았는가
```

---

## 3. 3층 판정 구조

| 층 | 역할 | 판정 방식 | 결과 | MVP |
|---|---|---|---|---|
| **1. 결정적 변경 감시** | 민감 경로·intent 이탈 감지 | 규칙(경로 패턴) | **차단/승인요구** | **MVP-0** |
| **2. 능력/데이터 감지** | 인증·암복호·외부송신·PII 신규도입 | 규칙+catalog | 승인요구 | MVP-1 |
| **3. 의도이탈/영향범위** | scope-creep·공유모듈 blast radius | 점수/경고 | 사람 리뷰 유도 | MVP-2 |

**보정 규칙(Claude 추가):**
- **tier는 규칙마다 policy에 선언**한다. 한 규칙을 확신이 쌓이면 `advisory → blocking` 으로 승격 가능.
- **1층은 왕관보석에서 미탐률 0 지향(오탐은 감수).** 3층은 정밀도 우선(안 그러면 무시당함).
- **2·3층은 절대 자동 차단으로 시작하지 않는다.** 승인요구/참고로만.

---

## 4. MVP-0 범위 (이번에 만드는 것)

경로 + YAML 만으로, **언어 무관**하게 동작하는 부분만.

1. `change-intent.yaml` 작성 강제 (없으면 실패)
2. `git diff` ↔ `allowed_paths` / `forbidden_paths` 비교 (의도 이탈 1차)
3. `sensitive-zones.yaml` 경로 충돌 감지 → level별 차단/승인
4. **변경 감사 카드**(change-evidence) 자동 생성
5. **리뷰어 자동 추천**(approval-routing)

**MVP-0에서 일부러 빼는 것** (오탐·언어의존 큼): 의존성/config/infra/db/auth *내용* 감지,
신규 외부호출/env/secret/PII *패턴* 감지 → 전부 **MVP-1**.

---

## 5. 게이트 (Codex 구현 · Claude 수용기준 §TASKS.md)

| 게이트 | 입력 | 판정 | 층 |
|---|---|---|---|
| `check-change-intent` | diff + change-intent.yaml | allowed 밖/forbidden 안 변경 → 실패 | 1 |
| `check-sensitive-zones` | diff + sensitive-zones.yaml | frozen 닿음→차단 / protected→승인요구 | 1 |
| `generate-change-evidence` | diff + 두 게이트 결과 + routing | 감사카드 yaml 생성 + 리뷰어 추천 | — |

판정 종료코드: **통과 0 / 차단 1 / 승인필요 2**(차단은 아니지만 사람 승인 없이는 진행 불가).

---

## 6. 산출물 흐름

```
change-intent.yaml  +  git diff
        │
   ├─[check-change-intent]──▶  의도 이탈?
   ├─[check-sensitive-zones]─▶  민감 구역 충돌? (level)
        │
   [generate-change-evidence]
        │
   change-evidence.yaml  (무엇/어디/민감등급/승인필요 리뷰어)  +  통과/차단/승인필요
        ↓
   사람은 이 카드부터 보고 위험 변경만 정독
```

---

## 7. 기존 은행 하네스와의 관계

- secure-sdlc(코드 *내용* 취약점·secret) 와 import-gate(*최종* 역할분리) **사이**의 빈칸.
- 이건 **변경 *행위* 자체**를 보는 유일한 하네스. verify 단계에서 **매 변경마다** 도는 cross-cutting 게이트.
- 데이터 기반 감지(MVP-1)는 data-standard·config-secret·data-privacy 카탈로그와 연결.

---

## 8. 미해결/2차 논의 (decisions.md 로 승격 대상)

- 능력 카탈로그(`sensitive-capabilities.yaml`)를 어떤 신호로 감지할지 (import/AST/호출패턴)
- 공유모듈 blast-radius 산출의 1차 근사(import 카운트) vs 정밀(call graph)
- scope-creep 점수화 공식
