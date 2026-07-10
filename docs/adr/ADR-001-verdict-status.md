# ADR-001 — 하네스 판정 상태 의미론 (Canonical Verdict Status Model)

- **상태:** **Accepted** (2026-07-10 형 승인) — GPT 자문 + Claude 적대적 리뷰(v3) 반영
- **번호:** ADR-001 · 하네스 판정 상태 의미론
- **작성:** Claude(정책·설계). 구현=Codex, 최종승인=형.
- **관련:** ADR-001 v1/v2, `판정상태-GPT자문.md`(GPT 권고), CLAUDE.md §4 불변 원칙
- **v1 → v2 변경 요지:** ① **축 분리**(status / analysis_state / disposition) ② 불변식을 `max_status_by_layer`로 검증화 ③ 적용성 필터 + fail-closed ④ approval/waiver 공통 record ⑤ 영문 canonical ⑥ MVP 경계.
- **v2 → v3 보정(적대적 리뷰):** **F-1** 적용성 필터 자기무력화 차단(D4) · **F-2** status↔analysis_state 결합 불변식(D0) · **F-3** maturity(shadow) 롤업 제외(D2/D3). (관찰 F-4~F-6은 후속 스키마 ADR로 이관 — 하단 §7)

---

## 1. 배경

판정을 종료코드 0/1/2로만 표현하면 kit화·다중 어댑터에서 **차단과 승인요구가 뭉개진다.** v1은 이를 5상태로 풀었으나, **`requires_approval` 하나에 "정책상 검토 필요"와 "분석 실패로 검토 필요"가 뒤섞이는** 결함이 남았다. GPT 자문의 핵심 교정 — **상태 수를 늘리지 말고 차원을 분리하라** — 를 반영해 v2를 정한다.

---

## 2. 결정

### D0. 🔴 세 축을 분리한다 (v2 핵심)

하나의 `status`에 모든 걸 싣지 않는다. 결과는 **독립된 세 축**으로 표현한다.

| 축 | 답하는 질문 | 값(enum) |
|---|---|---|
| **`status`** | 이 변경을 **자동 진행**시켜도 되나? (행동 판정) | `passed` `warning` `requires_approval` `failed` `skipped` |
| **`analysis_state`** | 판정 **과정**이 정상이었나? (분석 품질) | `complete` `partial` `failed` `timed_out` `not_applicable` |
| **`disposition`** | 사람 결정 **후** 실제로 어떻게 됐나? (사후 집행) | `allowed` `allowed_with_warning` `not_applicable` `pending_approval` `allowed_after_approval` `rejected_after_review` `blocked` `allowed_by_waiver` |

- `error`·`timeout`·`partial`을 **status에 추가하지 않는다** → `analysis_state` + `reason_code`로 기록.
- **엔진은 `status`·`analysis_state`를 낸다. `disposition`은 사후 단계**(승인/예외 워크플로·어댑터)가 채운다. 엔진의 원판정 `status`는 **절대 덮어쓰지 않는다.**

최소 결과 형태(개념):
```json
{
  "status": "requires_approval",
  "analysis_state": "partial",
  "reason_code": "parse_error_in_applicable_file",
  "review_route": "tool_owner",
  "gates": [ ... ],
  "unevaluated_paths": ["src/payments/risk.py"]
}
```

> **🔴 결합 불변식 (F-2 보정):** 세 축은 독립이 아니다. **적용 대상 표면에서 `analysis_state ∈ {partial, failed, timed_out}`이면 `status`는 최소 `requires_approval`이어야 한다.** 엔진이 이를 강제한다 — "분석 못 한 적용대상"을 `passed`/`warning`으로 둘 수 없음(모순 조합 `passed`+분석실패 = fail-open, 문법적으로 금지). *(비적용 표면의 미분석은 `not_applicable`이라 이 규칙과 무관.)*

### D1. Canonical status 5종 (행동 판정 전용)

| status | 표시명(한글) | 의미 | 자동 진행 | exit 투영 |
|---|---|---|---|---|
| `passed` | 통과 | 문제 없음 | ✅ | 0 |
| `warning` | 경고 | 진행 가능·기록(watched·저확신) | ✅ | 0 |
| `requires_approval` | 승인요구 | **검토 전 진행 불가** | ❌ | 2 |
| `failed` | 차단 | 명백한 금지(L1) | ❌ | 1 |
| `skipped` | 미적용 | 검사 대상 아님(증명됨) | 조건부 | 0 |

> `requires_approval`은 통과도 차단도 아닌 **독립 상태**. 보존이 성공 조건.

### D2. 층→상태 매핑 + 불변식 (검증화)

엔진은 `max_status_by_layer`를 **불변식으로 강제**하고, 이를 위반하는 정책은 **로딩 시 reject**한다.
```yaml
max_status_by_layer:
  L1_frozen:     failed            # 명백한 금지
  L1_protected:  requires_approval
  L1_watched:    warning
  L2:            requires_approval  # 능력·동적접근 — 자동차단 금지
  L3:            requires_approval  # 영향추적·과잉 — 상한 내 조정
```
- **정책이 바꿀 수 있는 것:** 어느 경로/함수/능력이 어느 층·등급인지, L2/L3 finding을 `warning`↔`requires_approval` 중 무엇으로(상한 내), 승인자 라우팅·증거 요구.
- **정책이 바꿀 수 없는 것(🔴 불변식):** L2/L3를 `failed`로 승격 · `failed`를 approval로 해소 · 분석 실패를 `passed`/조용한 `skipped`로 낮춤 · exit↔status 의미 변경.
- 위험한 L2는 **차단이 아니라 승인 강도**로 대응(예: `required_approvals: 2`, `review_route: security_owner`).
- **🟡 maturity 결합 (F-3 보정 · TASK-020 정합):** `maturity: shadow` 규칙의 finding은 **status 롤업에서 제외**(판정 미반영)하고 `gates[]`에 `maturity: shadow`로 **기록만** 한다. `enforcing` 규칙만 롤업에 반영. (shadow의 의미 = "아직 판정 안 함, 관찰만" 보존. shadow→enforcing 전환은 정책 완화·강화라 TASK-018 대상.)

### D3. 롤업 (강화)

```yaml
rollup:
  if_any_failed:              failed
  elif_any_requires_approval: requires_approval
  elif_any_warning:           warning
  elif_any_passed:            passed
  elif_all_skipped:           skipped
  else:                       requires_approval   # 빈/무효 결과 = fail-closed
```
- top-level은 "가장 센 상태"지만 **`gates[]`·`findings[]`에 모든 개별 상태를 보존**한다.
- `rollup_source`(그 상태를 만든 finding)와 `summary_counts`를 함께 남긴다 — `failed` 하나에 나머지 finding이 묻히지 않게.

### D4. 적용성 필터 + fail-closed (오탐 피로 대응)

**"모르겠다 ≠ skipped. 정책상 볼 필요 없음이 규칙으로 증명됨 = skipped."**
- **결정론적 적용성 필터**로 비대상을 먼저 `skipped` 처리(오탐 피로 완화):
  ```yaml
  applicability:
    skipped_if:
      - path_glob: "**/*.png"   ; reason_code: non_code_asset
      - path_glob: "**/*.lock"  ; reason_code: lockfile_no_surface ; only_if_no_sensitive_paths_changed: true
      - path_glob: "vendor/**"  ; reason_code: vendored_excluded    ; requires_manifest_entry: true
  ```
- **적용 대상인데 분석 못 함(파싱 실패 등) → 최소 `requires_approval` + `analysis_state=partial|failed`.** 절대 `skipped`/`passed` 아님.
- 실패는 **파일·게이트 단위로 기록**(`evaluated_paths` / `unevaluated_paths`), 전체 PR 뭉개기 금지.
- 분석 실패발 `requires_approval`은 `review_route: tool_owner`로 — **정책 검토와 구분**(승인자가 "위험 검토"인지 "도구 오류 처리"인지 알게).
- `skipped`는 `skip_reason` + `applicability_rule_id` 필수(조용한 skip 금지).
- **🔴 적용성 필터 자기무력화 차단 (F-1 보정):** 적용성 필터는 정책이라 **검사 회피 스위치가 될 수 있다**(예: `skipped_if: "**"` → 민감 변경이 "정직한 skip"으로 통과). 그래서:
  1. `skipped_if` 규칙은 **sensitive-zones(frozen/protected/watched) 경로를 skip 불가** — **경로 게이트가 적용성 필터보다 항상 우선**한다. 민감 경로는 필터 적용 전에 이미 판정된다.
  2. 적용성 규칙의 **추가·확대(범위 넓힘)는 "정책 완화"** 이므로 **TASK-018(정책 변경 게이트) 검사 대상**(축소·엄격화는 자유).
  → 이게 없으면 오탐 피로를 잡으려 만든 필터가 하네스 전체의 fail-open 해치가 된다.

### D5. JSON status 정본, 종료코드는 손실 투영 + adapter conformance

- 정본은 JSON `status`. 종료코드(0/1/2)는 손실 투영이며, **"비0=실패"로 뭉개는 소비자는 손실(lossy) 소비자**.
- **손실 소비자에게 `requires_approval`을 `warning`으로 낮추지 않는다**(안전속성 파괴) → 대신 annotation·artifact·check로 별도 노출.
- 어댑터 등급(상세는 후속): L0 exit-only(손실·프로덕션 게이트 부적합) / L1 status-json(최소) / L2 findings(권장) / L3 decision-lifecycle(완전).

### D6. approval / waiver = 공통 decision_record + `kind` (상태 아님)

`requires_approval`·`failed`는 **검토 전** 상태. 사람이 결정하면 **별도 기록**이 생기고 원판정에 *연결*(대체 아님)된다.

| | approval | waiver |
|---|---|---|
| 대상(prior_status) | `requires_approval` | `failed` |
| 의미 | 정상 검토 후 허용 | 명백한 금지의 **예외**(break-glass) |
| 만료 | 선택 | **필수** |
| 감사 질문 | "누가 검토했나" | "누가 금지를 예외처리했나" |

공통 스키마(구현 단순화), `kind`로만 분기:
```yaml
decision_record:
  kind: approval | waiver
  prior_status: requires_approval | failed
  actor · actor_role · decided_at · reason
  scope: { diff_digest, policy_digest, rule_ids, paths?, symbols?, capabilities? }
  expires_at        # waiver 필수
  evidence_links
  disposition       # allowed_after_approval | allowed_by_waiver | rejected_after_review
```
- **원판정 `status`는 덮어쓰지 않고 `disposition`으로 결과 표현.**
- **무효화:** diff_digest 바뀌면 기존 결정 무효 · policy_digest 바뀌면 재판정/재검증 · scope 밖엔 재사용 금지.

### D7. 재현·감사 메타데이터 동반

`engine_version · policy_digest · manifest_version · base_tree · head_tree · diff_digest · schema_version` + **rule 안정 식별자**(`rule_id` 불변 · `rule_name` 가변 · `rule_version` · `layer` · `max_status`). 없으면 "같은 변경=같은 판정" 증명 불가.

---

## 3. 🟢 MVP 최소 vs 후속 (구현 경계 — 과설계 방지)

GPT 권고는 성숙 시스템 기준이라 **전부 지금 만들면 과설계**다. **개념 축·불변식은 지금 확정(retrofit 비쌈), 상세는 후속**으로.

| 항목 | 지금(ADR 확정 시 방향) | 후속(스키마 ADR/나중) |
|---|---|---|
| status 3축 | **status·analysis_state 필드 존재** (disposition은 사후단계가 채움) | — |
| status enum | 5종 확정 | — |
| analysis_state | 5종 확정 | — |
| max_status_by_layer | **엔진 검증·정책 reject** | — |
| 적용성 필터 | **최소 규칙 몇 개**(docs·lock·vendor) | 전체 규칙셋 |
| fail-closed | **파일/게이트 단위 기록** | — |
| 롤업 | max + gates[] 보존 + fail-closed | rollup_source·summary_counts 정식 |
| decision_record | **최소 필드**(kind·prior_status·actor·decided_at·reason·diff/policy_digest·rule_ids·scope·expires) | tamper_evidence 서명·supersedes·revoked_at |
| reason_code | 핵심 몇 개 | 전체 enum |
| adapter conformance | 개념만(정본=status) | L0~L3 정식화 |
| warning 소비 | "기록은 남긴다"만 | 집계·정책 승격 메커니즘 |
| rule_id | **안정 식별자** | 버전 정책 |

---

## 4. 결과 · 기각한 대안

**좋아지는 것:** 승인요구가 차단/도구오류와 뒤섞이지 않음 · 우리 기존 층이 그대로 대응(frozen=failed/protected=requires_approval/watched=warning) · 감사 로그 정합 · 오탐 피로를 상태 하향이 아니라 기록 정밀도로 완화.

**기각:** ① exit-only 유지(손실) ② 승인요구→warning(자동진행) ③ 승인요구→waiver 기록(감사 역전) ④ 차단을 L2/L3 확장(불변식 위반) ⑤ error/timeout을 status로(과부하) — **전부 v2에서 배제.**

---

## 5. 열린 질문 (spine 계약 — 이 ADR을 막지 않음)

- 프로덕션 spine이 JSON `status`를 읽나, exit code만 보나? → adapter conformance·spine-kit 실효성 결정.
- `requires_approval` 제3상태 수용 가능한가, `warning`+`blocking:true`로만 표현되나?
- **엔진 canonical(이 ADR) + CI 어댑터는 이 확인을 기다리지 않고 진행 가능.** spine-kit 어댑터만 선행조건.

---

## 6. 확정 체크 (형이 OK만 주면 Accepted)

v1의 5질문은 GPT 권고로, 적대적 리뷰의 3구멍(F-1·F-2·F-3)은 v3 보정으로 **답이 정해졌다.** 남은 건 승인:

1. **D0 3축 분리** + **결합 불변식(F-2)** — 이대로?
2. **D2 불변식**(차단=L1만) + **maturity 롤업 제외(F-3)** — 이대로?
3. **D4 적용성 필터 + fail-closed** + **자기무력화 차단(F-1)** — 이대로?
4. **D6 approval≠waiver(공통 record+kind)** — 이대로?
5. **영문 canonical + 한글 표시명** — 이대로?
6. **§3 MVP 경계**(지금 축·불변식만, 상세 후속) — 이대로?

→ "이대로 확정" 주시면 ADR을 **Accepted**로 올리고 `docs/adr/ADR-001.md`로 커밋(기존 개발 영향 0), 다음은 result/evidence **스키마 ADR**로.

---

## 7. 후속 이관 (적대적 리뷰 관찰 — 비차단, 스키마 ADR에서 처리)

- **F-4** `disposition` 초기값 매핑 — 엔진이 사후 전 결과에 초기값 부여(passed→allowed · warning→allowed_with_warning · requires_approval→pending_approval · failed→blocked · skipped→not_applicable), 사후단계가 갱신.
- **F-5** `diff_digest`가 덮는 범위(raw patch vs 정규화)와 D6 결정 무효화의 결합 — 리포맷만으로 승인 무효화되면 과도. 정규화 범위 확정 필요.
- **F-6** all-skipped 롤업도 **감사카드에 명시 노출**(조용한 green 방지).
