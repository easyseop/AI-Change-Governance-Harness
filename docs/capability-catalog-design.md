# 능력 카탈로그 설계 계약 — TASK-010 / TASK-011 (2층: 신규 민감 능력 감지)

> 이 문서는 **Claude(정책·리스크 역할)** 가 소유한다. Codex 구현 계약이다.
> A-0003(TASK-008 `@gov` 계약)과 같은 형식 — Codex 는 이 계약대로 게이트를 구현한다.
> 작성일: 2026-07-05 · 상태: 설계 확정(선제) · 관련: TASK-010/011 / D-004 / D-017 / A-0003 / A-0005 / 설계 §1·§3

> **선제 설계 안내**: Codex 의 질문(Q) 없이 Claude 가 먼저 낸 설계다(TASK-010 은 "Claude 설계 선행" 태스크).
> 아래 정책 선택 4건은 **합리적 기본값으로 확정하되 "형 override 가능"** 으로 명시한다(비차단) — A-0003 의 층 분류 처리와 동일.

---

## 0. 무엇을 하는 층인가 (설계 §3 2층)

**1층(@gov·zone)** = 사람이 **명시 선언**한 규칙(추론 아님) → frozen 차단 가능.
**2층(능력)** = 코드가 **무엇을 할 수 있는가**를 AST 로 **추론** → 설계 §3·D-004 에 따라 **자동 차단 절대 금지, 승인요구가 상한**.

- **TASK-010 `extract-python-capabilities.py`**: 단일 `.py` → 그 파일이 가진 민감 **능력 집합**을 카탈로그 신호로 추출. **보고 전용·exit 0**(판정 없음). — TASK-008(추출) 대응.
- **TASK-011 `check-new-capabilities.py`**: `base..head` → 파일별 **head−base 신규 능력**만 골라 verdict. — TASK-009(판정) 대응.

핵심 비대칭: TASK-009 는 `base ∪ head max`(주석 제거 우회 차단). **TASK-011 은 `head − base`(신규 도입만)** — 능력 *제거*는 안전(경고 안 함), 능력 *신규 도입*만 승인요구.

---

## Q1. 카탈로그 — `policies/sensitive-capabilities.yaml` (Claude 소유 draft)

능력 = `{id, title, level, reason, reviewer, signals}`. 신호 3종:

| 신호 | 의미 | 예 |
|---|---|---|
| `imports` | **이 모듈 import 자체가 신호** (새로 들이면 능력 도입) | `subprocess`, `pickle`, `requests`, `socket` |
| `calls` | **해석된 점표기 전체 이름**(별칭·from-import 해소 후) 일치 | `os.system`, `subprocess.run`, `yaml.load` |
| `builtins` | import 없는 **내장 이름** 호출 | `eval`, `exec`, `compile`, `__import__` |

- `os`·`io` 같은 **흔한 모듈은 `imports` 에 넣지 않는다**(잡음). 그 특정 위험 호출만 `calls` 로(`os.system`).
- **왜 import-레벨 신호가 필수인가(핵심 방어)**: 호출 해석은 별칭·동적 접근으로 우회 가능하지만, **import 만큼은 정적으로 잡힌다** — `getattr(subprocess,"run")()`·`x=subprocess;x.run()` 처럼 호출 해석이 실패해도 `import subprocess` 신호가 backstop 으로 능력을 포착. (Q4 우회 세트 참조)
- 시작 카탈로그(고신호·저잡음): `subprocess_exec`·`dynamic_code_exec`·`unsafe_deserialization`·`outbound_network`·`crypto_primitive`. **자격증명·PII 취급은 명시 이연**(값·데이터흐름 분석 필요 → 별도 태스크).

## Q2. level·verdict — **2층은 승인요구가 상한 (blocked 금지)**

- catalog `level ∈ {protected, watched}`. **`frozen` 금지** — 오면 `invalid_capability_level` 기록 + **protected 로 clamp**(차단으로 승격 안 함).
- TASK-011 verdict: 신규 능력 중 `protected` 있으면 `approval_required(2)` / `watched` 만이면 `경고+pass(0)` / 없으면 `pass(0)`. **`blocked(1)` 은 이 게이트에서 절대 나오지 않는다**(불변식 — Q7 #7 음성검증으로 고정).
- 차단이 필요한 능력이면 그건 2층이 아니라 **1층 결정**(`@gov frozen` 또는 zone) 으로 사람이 선언할 일.

## Q3. 신호 해석 규칙 (결정적 — 값 추정 금지)

**import 바인딩 표를 AST 로 구축**(파일 스코프 + 함수/클래스 내 import 포함, walk 전수):

| 구문 | 바인딩 | 매칭 |
|---|---|---|
| `import subprocess` | `subprocess` → `subprocess` | `imports` 에 `subprocess` → 신호 |
| `import subprocess as sp` | `sp` → `subprocess` | 별칭 해소 → 신호 |
| `from subprocess import run` | `run` → `subprocess.run` | `calls` 에 `subprocess.run` → 신호 |
| `from subprocess import run as r` | `r` → `subprocess.run` | 별칭 해소 → 신호 |
| `from subprocess import *` | (해소 불가) | **`star_import` = 그 모듈이 카탈로그면 능력 신호** + `unresolved_dynamic` 기록 |
| `import os.path` | `os` → `os` | 점표기 root 바인딩 |

- **호출 해석**: `Call.func` 의 attribute 체인을 바인딩 표로 풀어 점표기 전체 이름 산출 → `calls` 대조. 내장 이름(`Name`)은 `builtins` 대조.
- **star import 우회 차단**: `from subprocess import *; run()` — `run` 을 못 풀지만 star_import(subprocess) 가 카탈로그 모듈이므로 `subprocess_exec` 도입으로 처리.
- **동적 우회는 backstop 으로**: `getattr(m,"run")()`·재대입 별칭은 호출 해석 실패해도 해당 **import 신호**가 잡는다. `__import__("subprocess")` 는 `__import__` 자체가 `dynamic_code_exec` 신호.
- **값 추정 금지**: `yaml.load(x, Loader=?)`·`open(p, mode)` 의 인자값으로 안전/위험 가르지 않는다 — `yaml.load` 는 보수적으로 항상 신호, `open` 쓰기모드 판별은 MVP 제외(잡음).

## Q4. 🔴 고정 적대(우회) 세트 — 상설 회귀 픽스처 필수 (§2B)

추출·매핑 게이트 공통 규정대로, 매 리뷰 재실행할 **상설 픽스처**:
1. **별칭**: `import subprocess as sp; sp.run(...)` → 감지.
2. **from-별칭**: `from subprocess import run as r; r(...)` → `subprocess.run` 해소 감지.
3. **star import**: `from subprocess import *` → `subprocess_exec`(star_import 경유) 감지.
4. **동적 접근**: `getattr(subprocess,"run")(...)` → `import subprocess` backstop 감지.
5. **동적 import**: `__import__("subprocess").run(...)` → `__import__` 가 `dynamic_code_exec` 감지.
6. **내장(무import)**: `exec(code)`·`eval(s)` → `builtins` 감지.
7. **함수 내부 import**: 톱레벨 아닌 def 안 `import pickle` → walk 전수로 감지(스코프 무관).

각 픽스처는 "신호 제거 → 미감지 = FAIL" 음성검증으로 실가드 확인.

## Q5. TASK-011 신규 판정 semantics — `head − base` (파일 단위 능력 id 집합)

- `base_caps(file)` = base 버전에서 추출한 **능력 id 집합**. `head_caps(file)` = head 버전.
- **신규 = `head_caps − base_caps`**(파일별 id 차집합). 신규 id 만 verdict 에 반영.
- **정책 선택 A(override 가능)**: 판정 단위는 **파일별 능력 id 집합**. 같은 파일이 이미 `subprocess_exec` 를 가졌다면 새 exec 호출 추가는 *신규 능력 아님*(경고 안 함) — 알람 피로 방지. 더 세밀히 원하면 조직이 catalog id 를 쪼개거나 호출부 단위로 override.
- **신규 파일**(base 부재): head 능력 **전부 신규** → 해당 능력들 approval.
- **삭제 파일**(head 부재): head 능력 없음 → **신규 없음 = 경고 안 함**(능력 제거는 안전 방향).
- **리네임**: git 이 D+A/R 무엇으로 보든 새 경로는 base 부재 = 신규 파일 취급 → 능력 전부 신규(approval). 안전 방향(과경고, 차단 아님) — 수용.

## Q6. 🔴 fail-closed — A-0005 교훈 그대로 (per-path 무조건, 전역 조건 금지)

TASK-009 D-020/A-0005 에서 "전역 `errors and not records` 로 fail-closed 걸면 동반 레코드로 꺼져 세탁" 을 겪었다. **동일 실수 반복 금지**:
- 변경 `.py` 가 **head 존재 + `parse_error`/`unreadable`** → **다른 결과 유무와 무관하게** 그 파일 per-path fail-closed `approval_required`(능력 못 읽음 = 신규 능력 은닉 가능). 신규 비-UTF8 파일에 `import subprocess` 은닉 세탁을 막는다.
- **base 존재 + 불능**(head 가독) → `base_caps` 를 **빈 집합으로 취급** → head 능력이 전부 신규로 잡혀 approval(안전 방향). 별도 차단 불필요하나 결과는 approval 로 수렴.
- 존재/부재 판별은 **`git cat-file -e <ref>:<path>` 결정적**(에러 문자열 파싱 금지 — A-0005 계약).
- **upstream error**(map/classify/inventory top-level 실패) → records 유무 무관 최소 `approval_required`.
- 회귀 픽스처: `new-cap-unreadable-head`(신규 불능 .py + 무관 변경 동반 → approval)·"fail-closed 무력화 → FAIL" 음성검증 필수.

## Q7. 출력 스키마

**TASK-010 `extract-python-capabilities.py`** — 단일 `.py`(경로 또는 stdin), `--json`, exit 0:
```json
{
  "path": "app/net.py",
  "capabilities": [
    {"id": "outbound_network", "level": "protected",
     "signals": [
       {"kind": "import", "name": "requests", "line": 2},
       {"kind": "call", "name": "requests.post", "line": 40}
     ]}
  ],
  "unresolved_dynamic": [ {"kind": "star_import", "module": "os", "line": 3} ],
  "errors": [],
  "parse_error": false, "unreadable": false
}
```
- `capabilities` 는 id 로 dedup, 각 id 아래 신호 인스턴스(감사카드용 근거·라인).
- 파일 단위 fail-safe: 문법오류→`parse_error`, 비-UTF8→`unreadable`, 형제 보존, exit 0 (TASK-013 계보).

**TASK-011 `check-new-capabilities.py`** — `base..head`, `--json`:
```json
{
  "gate": "check-new-capabilities",
  "verdict": "approval_required",
  "new_capabilities": [
    {"path": "app/net.py", "id": "outbound_network", "level": "protected",
     "reason": "신규 외부 네트워크 호출", "reviewer": "security-reviewer",
     "signals": [ /* head 측 인스턴스 */ ]}
  ],
  "warned_capabilities": [],
  "fail_closed": [ {"path": "app/x.py", "level": "protected", "reason": "head unreadable"} ],
  "errors": [],
  "exit_code": 2
}
```
- verdict: `new_capabilities`(protected) 또는 `fail_closed` 또는 upstream error 있으면 `approval_required(2)` / `warned_capabilities`(watched) 만이면 경고+`pass(0)` / 없으면 `pass(0)`. **`blocked` 없음(불변식)**.
- reviewer 는 catalog 의 `reviewer` 그대로(approval-routing 재사용 가능).

## Q8. 테스트 수용기준 (리뷰 체크리스트)

1. 각 카탈로그 능력: import-신호·call-신호 각각 1 케이스 이상 감지.
2. 🔴 **Q4 고정 적대 세트 7종** 상설 픽스처 + 각 음성검증.
3. 🔴 **신규만(Q5)**: 능력이 base·head **양쪽** → 미감지 / head 만 → 감지 / 신규 파일 → 전부 감지 / 삭제 파일 → 미감지. (base∪head 가 아니라 head−base 임을 음성검증으로 고정 — "base 무시하고 head-only 로 바꾸면 이미-있던 능력이 오검출 → FAIL")
4. 🔴 **fail-closed(Q6)**: head 불능 변경 .py → approval(동반 변경 있어도) / base 불능 → head 능력 신규화 approval. "per-path fail-closed 무력화 → FAIL" 음성검증.
5. 🔴 **never-blocked 불변식(Q2)**: catalog 에 `frozen` 을 넣어도 verdict 는 `approval_required` 상한·exit≠1. 음성검증: clamp 제거 시 blocked 나오면 FAIL 로 잡히게.
6. 카탈로그 검증오류: `invalid_capability_level`(frozen/미지)·unknown 신호종 기록+보수.
7. 결정성: 동일 입력 2회 md5 동일.
8. fail-safe: 문법오류·비-UTF8 파일 단위 격리·형제 보존·exit 0.

## 하류 계약 (TASK-012 통합)

- TASK-011 출력의 `errors`/`fail_closed` 비어있지 않으면 통합측도 최소 `approval_required`(중복 방어선 — TASK-009 D-021 와 동일 원칙).
- 능력 게이트는 `@gov`(1층)·zone(1층)과 **독립**. TASK-012 가 셋을 병합해 감사카드에 `new_capabilities[]` 를 싣는다. 능력 단독으로는 최대 approval(차단은 1층 몫).

## 정책 선택 (형 override 가능 · 비차단)

- **A. 판정 단위 = 파일별 능력 id 집합**(Q5). 기존 능력의 추가 사용은 재경고 안 함. → 호출부 단위 원하면 override.
- **B. import-of-민감모듈 = 도입으로 간주**(Q1·Q3). 호출 없어도 신호. → "실제 호출까지 있어야" 원하면 override(단 backstop 약화됨).
- **C. 시작 카탈로그 내용**(🟡) 은 조직이 채운다 — 위는 보수적 seed.
- **D. 자격증명·PII 취급 능력은 TASK-010 MVP 에서 명시 이연**(값·데이터흐름 분석 필요). → 우선순위 높이면 별도 태스크로 승격.

## 구현 경계

AST 기반 결정적 추출기, LLM·값추정 금지, 파일 단위 fail-safe. 브랜치 `codex/<날짜>-task010-capabilities`(그리고 011), 픽스처 `tests/fixtures/capabilities/`(before/after 쌍) + `tests/cases.yaml`·`run-tests.sh` 확장. TASK-005 인벤토리 스키마는 **확장 금지**(별도 게이트 — A-0003 와 동일 원칙).
