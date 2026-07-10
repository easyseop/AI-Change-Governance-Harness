# ADR-002 — result / evidence 스키마 (MVP-minimal)

- **상태:** **Accepted, with validation split** (2026-07-10) — GPT 검토 + Claude 평가 반영
- **작성:** Claude(정책·설계). 구현=Codex, 최종승인=형.
- **관련:** ADR-001(판정 상태 의미론) · GPT ADR-002 검토(2026-07-10)
- **원칙:** ADR-001의 3축·불변식을 JSON으로 구현. **검증은 두 층으로 분리**(shape=JSON Schema / semantic=validator). MVP는 최소 필드, 상세는 스키마 버전으로 진화.
- **v1 → v2 변경:** ① 검증 분리(E8 신설) ② finding에 `analysis_state` 추가 ③ coverage를 (path,gate) 객체로 ④ decision을 원판정과 분리 ⑤ summary_counts·rollup 다원화 ⑥ enum 명시.

---

## 1. 배경

ADR-001이 "판정의 의미"를 정했다. 이 ADR은 엔진이 그 판정을 **결정론적·감사가능·어댑터 재사용 가능**하게 내보내는 **정본 결과 객체(`acgh-result`)** 와 그 **검증 방식**을 정한다.

---

## 2. 결정

### E1. 정본은 `acgh-result` JSON 하나 (원판정 immutable)

엔진 산출의 정본은 `acgh-result` JSON. 감사카드·CI annotation·spine evidence는 모두 **파생(투영)**. **원판정은 불변** — 사후 decision을 이 객체에 append하지 않는다(E5).

> **투영 우선순위:** 어댑터가 exit code/외부 status로 투영해도 충돌 시 **`acgh-result.status`가 정본**. **투영이 `requires_approval`을 `failed`와 구분해 보존 못 하면 그 투영은 명시적 lossy**이며 정본 판정으로 취급 금지.

```json
{
  "schema_version": "acgh-result/0.1",
  "engine_version": "0.x.y",
  "run": {
    "base_tree": "...", "head_tree": "...",
    "diff_digest": "sha256:...",     // 정규화 범위는 ADR-001 F-5(후속)
    "policy_digest": "sha256:...",
    "created_at": "..."              // 감사용 — 결정성엔 불참
  },
  "status": "requires_approval",     // ADR-001 D1
  "analysis_state": "complete",      // ADR-001 D0
  "rollup": { /* E2b */ },
  "summary_counts": { /* E2c */ },
  "gates": [ /* E2 */ ],
  "coverage": { /* E4 */ }
  // decisions 없음 — 별도(E5)
}
```

### E2. 게이트 · finding (finding에 `analysis_state` 포함)

```json
{
  "gate_id": "sensitive_zones",
  "status": "requires_approval",
  "analysis_state": "complete",
  "maturity": "enforcing",
  "findings": [{
    "finding_id": "f_001",
    "rule_id": "L1_PROTECTED_PATH", "rule_version": "1.0.0",
    "layer": "L1",
    "status": "requires_approval",
    "analysis_state": "complete",        // ← v2 추가(GPT Top2): 분석품질이 finding→gate→top로 전파
    "reason_code": "protected_path_touched",
    "review_route": "security_owner",
    "locus": { "path": "app/auth/login.py", "symbol": null, "capability": null },
    "message": "보호 경로 접촉 — 지정 승인자 검토 필요"
  }]
}
```

### E2b. rollup (단수 → primary + sources)

```json
"rollup": {
  "status": "requires_approval",
  "analysis_state": "complete",
  "primary_source": { "gate_id": "sensitive_zones", "finding_id": "f_001" },
  "sources": [ { "gate_id":"sensitive_zones","finding_id":"f_001" } ]   // 최상위 status 만든 enforcing finding 전부
}
```

### E2c. summary_counts (findings 기준 · enforcing만, shadow 분리)

```json
"summary_counts": { "failed":0,"requires_approval":1,"warning":2,"passed":0,"skipped":1 },  // enforcing findings only
"shadow_counts":  { "warning":1 }   // shadow는 절대 top status에 불참
```

### E3. status ↔ analysis_state 결합 (semantic validator가 강제)

> **적용 대상에서 `analysis_state ∈ {partial, failed, timed_out}`이면 그 finding·gate·top의 `status`는 최소 `requires_approval`.** (L2/L3는 상한 때문에 결과적으로 `requires_approval`.) 이건 JSON Schema가 아니라 **E8 semantic validator**가 검증하며, 위반은 invalid → fail-closed.

### E4. coverage ((path, gate) 객체 — GPT Top6)

```json
"coverage": {
  "evaluated": [
    { "path":"app/auth/login.py","gate_id":"sensitive_zones","analysis_state":"complete" },
    { "path":"app/auth/login.py","gate_id":"capability_scan","analysis_state":"complete" }
  ],
  "unevaluated": [
    { "path":"src/payments/risk.py","gate_id":"capability_scan",
      "reason_code":"python_parse_error","analysis_state":"failed","review_route":"tool_owner" }
  ],
  "skipped": [
    { "path_glob":"docs/**/*.png","applicability_rule_id":"APP_NON_CODE","skip_reason":"non_code_asset" }
  ]
}
```
- `unevaluated`의 적용대상 항목은 E3에 의해 대응 finding의 status가 이미 올라가 있어야 한다(E8 연결검증).
- `skipped`는 `applicability_rule_id`+`skip_reason` 필수. **all-skipped도 여기 근거 노출**(조용한 green 금지).

### E5. decision = 원판정과 분리 (immutable + append)

원판정 `acgh-result`는 **불변**. 승인/예외는 **별도 record**로 두고 **evidence bundle**이 묶는다(GPT Top4).
```json
// acgh-decision (append-only, 원판정과 별 파일/객체)
{
  "decision_id":"dec_...","kind":"approval",           // approval | waiver
  "prior_status":"requires_approval",                  // waiver면 failed
  "disposition":"allowed_after_approval",
  "actor":"alice@corp","actor_role":"CODEOWNER:auth","decided_at":"...","reason":"검토 완료",
  "scope":{ "result_digest":"sha256:...","diff_digest":"sha256:...","policy_digest":"sha256:...",
            "rule_ids":["L1_PROTECTED_PATH"],"finding_ids":["f_001"] },
  "expires_at": null                                    // waiver 필수, approval 선택
}
// acgh-evidence-bundle = { result(immutable) + decisions[] + bundle_digest }
```
- **무효화:** scope의 `result_digest`/`diff_digest`/`policy_digest`가 현재와 다르면 decision 재사용 금지.

### E6. 감사카드 = 렌더 (정본 아님)

`acgh-result`(+decisions)를 읽어 렌더. 30초에 보여야 할 것: **status/analysis_state · 왜(rollup.sources) · 승인 라우트 · coverage(적용/미적용/skip) · digest(diff/policy/engine/schema) · 사후 decision은 원판정과 분리 표시.** `generate-change-evidence.py`는 이 렌더러로 전환(전환기엔 `source_of_truth: acgh-result` 명시).

### E7. 스키마 버전

`acgh-result/0.1` — semver. **소비자는 schema family + major만 호환 확인**(pre-1.0이라 minor는 필드 추가 위주). 검증 실패 결과는 소비자가 invalid로 보고 최소 `requires_approval` fail-closed.

### E8. 🔴 검증은 shape + semantic 2층 (v2 핵심 — GPT Top1)

- **JSON Schema (`schemas/acgh-result.schema.json`)** — 형태만: 필수 필드·타입·enum·digest 패턴·date-time·`decision.kind==waiver → expires_at 필수`·locus/coverage 구조. **롤업 계산을 넣지 않는다.**
- **Semantic validator (`acgh validate-result`)** — 교차 불변식(아래 §3). 
- **둘 중 하나라도 실패 → invalid → 소비자 fail-closed(최소 `requires_approval`, route=tool_owner).**

---

## 3. Semantic validator 불변식 (Codex 구현 입력)

```text
severity: failed=4 > requires_approval=3 > warning=2 > passed=1 ; skipped=중립
analysis_state: complete | partial | failed | timed_out | not_applicable
maturity: enforcing | shadow            # MVP는 2종 (disabled 제외 — 규칙 끄기는 정책완화=TASK-018)

[layer 상한]  every finding: severity(status) ≤ severity(max_status_by_layer[layer])
              L1=failed · L2=requires_approval · L3=requires_approval  (정책 로딩도 동일 검사, 위반 reject)
[결합]        applicable finding: analysis_state∈{partial,failed,timed_out} → status∈{requires_approval,failed}
              gate·top 에도 동일 적용
[gate rollup] gate.status = max_status(적용 findings); 적용 finding 없고 완주면 passed / 명시 미적용이면 skipped
              gate.analysis_state = worst(findings): failed>timed_out>partial>complete>not_applicable
[top rollup]  result.status = max_status(enforcing gates); 모두 skipped/not_applicable이면 skipped
              shadow gate/finding은 top에 불참
[maturity]    shadow finding/gate는 보고만, rollup 제외
[coverage]    unevaluated(적용대상) → 대응 finding(status≥requires_approval, analysis_state∈실패군, route=tool_owner) 존재
              skipped → applicability_rule_id + skip_reason 필수
[summary]     summary_counts = enforcing findings 카운트와 일치 ; shadow는 shadow_counts
[rollup src]  rollup.sources = 실제 top status 만든 enforcing finding들
[decision]    scope.result_digest/diff_digest/policy_digest == 현재 result ; kind=waiver→expires_at 필수·prior=failed ;
              kind=approval→prior=requires_approval
[invalid 처리] schema/semantic/policy-load/engine-error → status=requires_approval, route=tool_owner
              (failed 로 올리지 않음 — failed는 L1 명백금지 전용, ADR-001 정합)
```

---

## 4. MVP-minimal vs 후속

| 항목 | MVP(지금) | 후속 |
|---|---|---|
| 검증 | JSON Schema + semantic validator(위 §3 전부) | 성능·에러코드 표준화 |
| finding | id·rule_id·layer·status·**analysis_state**·reason_code·locus·review_route | dedup·rule_version 정책 |
| coverage | (path,gate) 객체 · evaluated/unevaluated/skipped | 대량 요약·문장화 |
| summary | enforcing findings + shadow_counts | gate 이중 카운트 |
| rollup | primary + sources[] | 시각화 |
| decision | 별도 record + bundle | tamper 서명·supersedes·revoked |
| reason_code | 핵심 몇 개 | 전체 enum |

---

## 5. 구현 순서 (Codex)

1. enum·모델 고정(Status/AnalysisState/Layer/Maturity/DecisionKind/Disposition) — `dataclasses`+`jsonschema` 최소 의존.
2. `acgh-result.schema.json`(shape만).
3. `validate_result.py`(`validate_shape`·`validate_semantics`·`compute_rollup`·`compute_summary_counts`), 실패도 JSON으로.
4. 기존 게이트 `--json` → normalized finding[] → gate → envelope → 검증(adapter layer만 신규, 게이트 로직 무변경).
5. 렌더러는 **검증된** result만 입력.

---

## 6. spine/kit 어댑터

투영은 정본 `acgh-result` 링크를 보존. `requires_approval`을 구분 못 하는 어댑터는 **lossy로 표시 + 원본 result를 evidence로 포함**. `requires_approval`을 `warning`/`waiver`로 낮추지 않는다(ADR-001 정합).

---

## 7. 확정 체크 (형)

GPT 체크리스트 12항은 v2에 **전부 반영**(finding.analysis_state·enum·검증분리·summary 기준·shadow 제외·all-skipped·coverage gate_id·rollup 다원화·decision 분리·waiver 만료·invalid 처리·lossy 우선). 남은 형 결정:

1. **decision 분리**(원판정 immutable + 별도 record + bundle) — 이 방향? *(추천)*
2. **maturity MVP = `enforcing|shadow`만**(`disabled` 제외 = 규칙 안 싣기, TASK-018) — 동의?
3. **summary_counts = enforcing findings 기준** — 동의?

→ OK 주시면 **Accepted로 커밋**(`docs/adr/ADR-002.md`), 다음은 **JSON Schema + semantic validator 불변식(§3)을 Codex 구현 입력으로** 인계.
