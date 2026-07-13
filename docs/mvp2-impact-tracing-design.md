# MVP-2 설계 — 영향 추적(간접 영향 / sink 역도달성)

> **소유:** Claude(판단/정책/리스크). 구현(게이트 코드) = Codex. 최종 승인 = 형.
> **상태:** **Accepted** (2026-07-13 — 형 §10 4항 전부 승인). Codex 에 TASK-022 인계.
> **관련:** `change-governance-design.md` §3(3층 구조 — 이 문서가 3층을 구체화) · `TASKS.md`(태스크 022~025) · ADR-001(판정상태·coverage 정직) · ADR-002(result 스키마).
> **확정된 방향(형 승인 2026-07-13):** ① @gov↔sink = **레벨 차등 하이브리드**(frozen 자동 sink + `@gov(sink=true)` 옵트인) · ② 시작 스코프 = **최소부터 래칫**(단일 diff·N=1~2홉·frozen 중심).

---

## 1. 문제 정의 — 무엇을 메우나 (현행 완전 무탐지 구멍)

현재 게이트가 잡는 것: 민감경로 직접변경(L1) · @gov 함수 **직접** 변경 · 새 위험능력 도입 · 의도이탈.

**메우는 구멍 = 간접 영향.** 예: `download_report()` 가 민감(sink)인데, 그것이 부르는 헬퍼 `check_permission()` 을 AI가 고치면 —
- `check_permission` 은 민감경로 아님 · @gov 아님 · 새 능력 없음 · 허용경로 안이면 의도이탈도 아님
- → **어떤 게이트도 안 울린다.** sink의 안전이 상류 수정으로 조용히 무너진다.

이게 형이 전에 물었던 *"다운로드에 @gov 달면 종단추적으로 영향 주는 건 잡히나?"* 의 **현행 답=아니오**. MVP-2가 이 답을 "예(승인요구로)"로 바꾼다.

---

## 2. 메커니즘 — sink + 역도달성(reverse reachability)

```
sink 집합 정의  →  repo 콜그래프 구성  →  diff 에서 바뀐 함수 집합
        →  "sink 이 (전이적으로 N홉 내) 호출하는 함수가 바뀌었나?"  →  예면 승인요구
```

**방향 정확히:** sink(`download_report`)이 → `check_permission` 을 호출한다. `check_permission` 이 diff에서 바뀌면 = **sink 이 의존하는 함수가 바뀜** = 간접 영향 가능. 즉 **sink 로부터 forward 도달 가능한 함수 집합** 안에 바뀐 함수가 있으면 flag.

- **N=1**: sink 이 **직접** 부르는 함수가 바뀜 (download→check_permission 직접). 가장 정밀·고가치.
- **N=2**: 한 단계 더 간접. 시작은 N=1, 과탐 실측 보며 N=2로 래칫.

---

## 3. sink 등록 모델 (형 확정: 레벨 차등 하이브리드)

sink = "간접 영향까지 지켜야 할 종착 함수". 세 출처로 등록:

| 출처 | sink 여부 | 근거 |
|---|---|---|
| **frozen 존 함수** | **자동 sink** | 왕관보석. 소수라 비싼 콜그래프 비용 감수 가치 있음 |
| `@gov(sink=true)` | **옵트인 sink** | 작성자가 "이건 상류까지 지켜라" 명시 |
| 정책 `sink-registry`(신규 YAML 또는 sensitive-zones 확장) | 명시 등록 sink | @gov 못 다는 외부/생성 코드용 |
| 일반 `@gov`(sink 미지정) · protected 존 함수 | **sink 아님** | 직접변경 게이트가 이미 커버. 콜그래프에서 제외 → 신호대잡음 보존 |

**핵심 설계 의도:** 비싸고 과탐 잦은 콜그래프 분석을 **소수 고가치 sink에만** 건다. 전체 @gov 자동 sink(①안)는 공통 유틸이 모든 sink에서 도달 가능해져 과탐 폭발 → 기각. 옵트인으로 blast radius를 작성자·정책이 통제.

`@gov(sink=true)` 문법은 기존 @gov 데코레이터 파싱(TASK-005 계열)을 확장하되 **하위호환**: `sink` 미지정 = 기존 동작(직접변경만).

### 3.1 sink-registry 스키마 (Claude 확정 — TASK-022 구현 입력)

@gov 를 못 다는 코드(외부 라이브러리 경유·코드생성·데코레이터 부착 불가)를 위한 **명시 등록 파일**. frozen 자동 sink·`@gov(sink=true)` 옵트인으로 커버 안 되는 경우만 쓴다(대부분 비어 있어도 됨).

```yaml
# policies/sink-registry.yaml — 명시 sink 등록 (MVP-2 간접영향 추적 대상)
policy_version: "0.1-mvp2"
defaults:
  maturity: shadow          # 신규 sink 기본 = shadow (검증 후 enforcing 승격) — §6-3
  hops: 1                   # 역도달 깊이 기본 N=1 (정책값, 하드코딩 금지 — TASK-025 AC#2)
sinks:
  - id: report_download                     # 안정 불변 식별자(리네임돼도 유지)
    function: "app.reports.download_report"  # 정규화 함수명(module.path.Class.method) — 콜그래프 노드와 동일 규약
    reason: "PII 리포트 반출 경계"           # 30초 판독용
    owner: security-reviewer                 # 라우팅 대상
    maturity: shadow                         # 생략 시 defaults
    # hops: 2                                # 생략 시 defaults. 이 sink만 깊게 볼 때 개별 지정
```

**규칙(검증기 — TASK-022):**
- `id`·`function`·`reason`·`owner` 필수. `function` 이 콜그래프 노드로 **해소 안 되면** 검증오류 기록(조용한 무시 금지) + 그 항목은 fail-safe(로드 실패를 clean 으로 취급 금지).
- `maturity ∈ {enforcing, shadow}`. 무효값 → 검증오류 + **enforcing 보수 취급**(TASK-020 정합 — 완화 우회 방지).
- 빈 `sinks:`·파일 부재 = 등록 sink 없음(정상, frozen 자동+옵트인만으로 동작).
- **`function` 정규화 규약은 TASK-023 콜그래프 노드 정체성과 동일해야 한다** — 노드 식별 방식 확정 시 이 필드도 정합(구현 중 불일치 발견하면 Claude 에 Q 로 확인).

---

## 4. 콜그래프 근사 — 결정론 + 정직 (이 층의 최대 리스크)

**원리적 한계 선언:** 파이썬 콜그래프는 동적 디스패치·고차함수·getattr·덕타이핑 때문에 **정적으로 sound+precise 불가**. 근사만 가능 → 우리는 **"해석되는 정적 호출은 잡고, 못 푸는 것은 coverage 갭으로 정직하게 노출"**(ADR-001 D4·조용한 green 금지)한다.

**빌더 스펙(결정론·이름기반, Codex 구현 입력):**
- 각 `.py` 를 AST 파싱(기존 capability 추출기 인프라 재사용).
- 각 함수정의에 대해 호출 이름 수집 → 기존 import 해소(별칭·from-import) 재사용해 **repo 내 함수정의로 해소되는 호출만 엣지**(caller_fn → callee_fn).
- **해소 실패 호출**(getattr·동적·외부 라이브러리·미상 타입의 메서드)은 **버리지 않고** `unresolved_calls`(함수별)로 기록 → coverage.unevaluated 로 표출.
- 같은 파일 내 동명 오버로드·조건부 정의는 **보수적으로 병합**(strongest/합집합) — 기존 추출기 `strongest_level` 병합 방식과 정합.

**근사의 방향성(정직):**
- 정적 해석 호출에 대해선 **과대근사 아님**(실제 이름 일치만) — 과탐은 주로 "공통 유틸이 sink N홉 내" 케이스에서, N 통제로 완화.
- 동적 호출은 **과소근사**(sink이 getattr로 부르는 상류를 놓침) → **명시 한계**로 문서·coverage에 노출. 이건 MVP-2가 "완전 방어"가 아니라 "정적으로 보이는 간접경로 방어 + 못 보는 것 실토"임을 뜻한다.

---

## 5. 판정 규칙 (verdict 통합)

- 바뀐 함수(diff) ∈ (sink 로부터 forward 도달 N홉 집합) → **`indirect_impact` finding, 최소 `approval_required`**.
- **차단 절대 금지**(3층 원칙·불변원칙 §4). 간접=불확실이라 승인요구가 상한.
- 라우팅: 영향받은 **sink 의 owner/reviewer** 로(왜 걸렸나 = "이 변경이 sink X 의 상류 Y 를 수정").
- **판정 근거 명시**: finding 에 `sink_id` · `changed_function` · `path`(sink→…→changed 경로) · `hops`. 감사카드 30초 판독.
- 분석 실패(파싱오류 등) → ADR-001 F-2 결합: 해당 sink 도달분석이 partial/failed면 그 finding status 최소 approval + route=tool_owner.

---

## 6. 과탐 통제 (도입 실패 1순위 시나리오 = 과탐으로 게이트를 꺼버림)

1. **옵트인 sink 밀도** — 전체가 아니라 frozen+명시만 sink. 공통 유틸은 *등록된* sink의 N홉 내일 때만 걸림.
2. **거리 한계 N=1 시작** — 직접 호출만. 가장 정밀. 래칫으로 N=2.
3. **shadow 성숙도 재사용**(TASK-020) — 신규 sink는 `maturity: shadow` 로 먼저 관찰(verdict 미반영, `shadow_hits` 기록) → 과탐 실측 후 enforcing 승격. **간접영향 층은 shadow로 시작 강력 권장.**
4. **고팬인 함수 dampening은 하지 않음(초기)** — "너무 흔한 함수는 제외"는 진짜 경로를 숨길 위험 → 대신 N 통제로. (후속 검토 항목으로만.)

---

## 7. 명시적 비범위 (MVP-2에서 **안** 하는 것 — 정직)

| 항목 | 왜 미룸 | 어디로 |
|---|---|---|
| **cross-commit 누적**(여러 PR로 쪼개 넣기) | 단일 diff 무상태 모델을 깸 — baseline sink-graph 저장소 필요 = 다른 아키텍처 | MVP-2 Phase B 또는 MVP-3 |
| **비-Python artifact**(SQL·YAML·notebook·IaC) 함수수준 | 경로층이 파일단위 이미 커버. 언어별 콜그래프는 별개 로드맵 | 언어별 후속 |
| **동적 호출 완전 복원** | 원리적 불가(§4) | 영구 한계 — coverage로 노출 |
| 고팬인 dampening·시각화·경로 랭킹 | 초기 과탐 데이터 없이 튜닝 불가 | 래칫 후속 |

---

## 8. 태스크 분해 (Codex 구현 · AC 는 TASKS.md 에 확정)

- **TASK-022** sink 등록 스키마 — `@gov(sink=true)` 파싱 확장(하위호환) + frozen 자동 sink + 정책 `sink-registry`. Claude 스키마 설계 / Codex 구현. **판정 무변경**(등록만).
- **TASK-023** intra-repo 정적 콜그래프 빌더 — 결정론·이름기반 엣지 + `unresolved_calls` coverage 노출. 판정 미연결(그래프 산출만).
- **TASK-024** 역도달성 게이트 — 바뀐 함수 ∈ sink N홉 forward → `indirect_impact`/approval. verdict·감사카드 통합. N=1 시작. shadow 성숙도 지원.
- **TASK-025** 과탐 통제 + 고정 적대 입력 세트 — 회귀 픽스처(§9)·거리 튜닝·음성검증.

의존: 022 → 023 → 024 → 025. 각 태스크는 이전 통과·머지 후 착수(기존 배치 규율).

---

## 9. 고정 적대 입력 세트 (상설 회귀 — CLAUDE.md §2B 세트의 MVP-2 확장)

콜그래프/역도달성은 **매 리뷰마다 이 세트를 돌린다**(픽스처로 상설화, 통과 못하면 결함):

1. **직접 간접경로**: sink→helper 직접호출, helper 수정 → **approval**(핵심 참).
2. **N홉 경계**: N=1 설정에서 2홉 상류 수정 → **미발화**(경계 정확), N=2 승격 시 발화.
3. **동적 디스패치 미탐(정직성 테스트)**: sink이 `getattr(obj,name)()` 로 helper 호출 → helper 수정이 **coverage.unevaluated 에 노출되는지**(조용히 통과 아님 검증).
4. **옵트인 경계**: sink 미등록(일반 @gov) 상류 수정 → **미발화**(밀도 통제 정확).
5. **과탐 경계**: sink과 무관한 함수 수정 → **미발화**.
6. **음성검증(rig-and-revert)**: 역도달성 필터 무력화 → 참 케이스(#1) BLOCK→PASS 뒤집힘 실증.
7. **동명/조건부 정의**: sink이 조건부 def 된 helper 호출 → 보수적 병합으로 발화.

---

## 10. 확정 체크 (형) — **전부 승인됨 (2026-07-13)**

1. **@gov↔sink = 레벨 차등**(frozen 자동 + `@gov(sink=true)` 옵트인) — ✅ 승인.
2. **최소 스코프**(단일 diff·N=1·frozen 중심·shadow 시작) — ✅ 승인.
3. **cross-commit·비-Python 명시 비범위**(§7) — ✅ 승인.
4. **간접영향 층은 shadow 성숙도로 시작**(§6-3) — ✅ 승인.

→ **Accepted.** TASK-022 부터 Codex 착수. sink 등록 스키마(§3.1)는 Claude 확정분 — Codex 는 이 스키마로 구현.
