# 배포 킷 사용 가이드 (친절 + 정확)

> **누구를 위한 문서인가**: 이 킷(`kit/`)을 **내 저장소에 붙여서** AI/개발자의 코드 변경을 검토·게이팅하려는 사람.
> **한 줄**: AI가 만든 diff를 결정적으로(추정·LLM 없음) 검사해 **위험한 변경만 사람 승인으로** 올려주는 도구.
> **레퍼런스**: 게이트 21종의 내부 계약은 `kit/README.md`. 이 문서는 "어떻게 붙이고, 결과를 어떻게 읽고, 막히면 어떻게 하나"에 집중한다.

---

## 0. 이 킷이 안전한 이유 (먼저 안심하시라)

- **대상 코드를 실행하지 않는다.** 게이트는 소스를 **정적으로**(구문트리·경로·정책만) 읽는다. 여러분의 코드를 import 하거나 돌리지 않으므로, 검사 자체가 부작용을 내지 않는다.
- **판정에 LLM·추정 없음.** 같은 입력이면 항상 같은 결과(결정적). "AI가 애매하게 판단"하는 게 아니라 정책(YAML) + 코드 구조 대조.
- **자동 차단은 딱 하나** — 금전 직접영향(frozen)뿐. 나머지는 전부 "사람이 한 번 봐라"(승인요구)가 상한. 게이트가 마음대로 배포를 막지 않는다.

---

## 1. 30초 요약

```bash
python3 -m pip install -r kit/requirements.txt          # 1) 의존성 (최초 1회)
./kit/selftest.sh --quick                               # 2) 킷 살아있나 확인
./kit/bootstrap.sh zones <내repo> --rules rules.yaml    # 3) 민감경로 후보 자동 씨딩
#    → 사람이 검토·보강해서 policies/sensitive-zones.yaml 확정
./kit/run.sh main..feature --repo <내repo> \
     --policies <정책dir> --output card.yaml            # 4) 변경 검사
echo $?                                                 # 5) 종료코드로 판단 · card.yaml 로 근거
```

---

## 2. 결과 읽는 법 — 판정 상태와 종료코드 ★가장 중요

게이트는 **네 가지 상태**로 판정한다. 종료코드는 그 상태를 마지막에 한 번 변환한 것이다.

| 상태 | 종료코드 | 뜻 | 무엇을 해야 하나 |
|---|---:|---|---|
| **pass** | `0` | 정책 위반 **미탐지** (※"안전 인증"이 아니라 "못 찾음") | 통과. 단, 3절 coverage("못 본 것")를 감안. |
| **approval_required** | `2` | 사람이 봐야 함 (민감경로·신규능력·간접영향·의도이탈·정책완화) | 담당 리뷰어가 감사카드 보고 승인/반려. |
| **blocked** | `1` | frozen(금전 직접영향) 접촉 | 원칙적으로 막힘. 정말 필요하면 정책 소유자 예외 절차. |
| **분석 실패(fail-closed)** | `2` | 게이트 크래시·타임아웃·정책 파일 부재 등 = **검사를 못 함** | "통과"로 착각 금지. 원인(도구·환경) 고치고 재실행. 카드에 `tool_owner`로 표시됨. |

### 🔴 반드시 알아야 할 정직한 한계 — "exit 2와 1이 뭉개질 수 있다"

단순 CI는 흔히 **"0이면 성공, 0이 아니면 실패"** 로만 처리한다. 그러면 이 킷의 핵심(**승인요구(2)** 는 차단이 아니라 *사람에게 올리는 것*)이 **차단(1)과 똑같이 "실패"로 뭉개진다.**

- **대응 1**: CI에서 **종료코드만 보지 말고 감사카드(`--output`)를 읽어라.** `verdict` 필드가 정본이다.
- **대응 2**: 근본 해결은 **결과 파일 정본화**(`docs/adr/ADR-002` — 결정됨, 구현 대기). exit code는 파일을 못 읽는 환경용 fallback으로만 취급.
- **대응 3**: **분석 실패를 "승인요구"로 약화하지 마라.** 검사를 못 한 것(fail-closed)과 검사 후 승인이 필요한 것은 위험도가 다르다 — 분석 실패는 **원인을 조사**해야 하는 상태다.

> 즉: **exit code는 힌트, 감사카드의 `verdict`가 정본.** 둘이 어긋나면 "분석 실패"로 보수적으로 처리하라.

---

## 3. 이 판정이 "본 것"과 "못 본 것" (coverage)

pass가 "안전 보증"이 아닌 이유. 감사카드의 `coverage_statement`에 매번 명시된다.

- **본 것(checked)** — 실제 실행된 게이트: 경로/의도·민감경로·(파이썬)함수레벨·신규능력·간접영향·정책변경 중 돌아간 것.
- **못 본 것(not_checked)** — 런타임 실행경로·미등록 민감 비즈니스 로직·cross-commit 누적·비-파이썬 정밀분석·완전 동적 난독.

정책(민감경로·sink 등)을 **덜 채우면 "본 것"이 줄어든다.** 씨딩을 성실히 하는 만큼 커버리지가 는다.

---

## 4. 단계별 도입

```bash
# 0) 의존성 — tree-sitter 핀 버전은 Python 3.10+ 필요 (3.9면 JS/TS 스모크 1건만 실패·무해)
python3 -m pip install -r kit/requirements.txt

# 1) 킷 자체검증 (게이트 누락 시 FAIL)
./kit/selftest.sh              # 전체(러너+뮤테이션)
./kit/selftest.sh --quick      # 빠르게

# 2) 민감경로 후보 자동 씨딩 (기계) → 사람 승인
./kit/bootstrap.sh zones     <내repo> --rules rules.yaml
./kit/bootstrap.sh functions <내repo>

# 3) 대상 repo 에 change-intent.yaml 작성 (변경 의도 선언 — 5절 규칙 참고)

# 4) 검사
./kit/run.sh main..feature --repo <내repo> --policies <정책dir> --output card.yaml

# 5) CI 연동 — run.sh 를 verify 단계에 걸고, 종료코드 + card.verdict 로 게이팅
```

**`main..feature`** = 검사할 git 범위(base ≠ head). 예: `main..feature`(feature가 main 대비 바꾼 것), `HEAD~1..HEAD`(직전 커밋).

---

## 5. 규칙(정책) 설정 — 무엇을 어떻게 채우나

판정은 전부 코드 밖 YAML 정책에서 나온다. 도입 = 이 정책들을 내 조직/repo 에 맞게 채우는 일.

| 정책 파일 | 정하는 것 | 누가 채우나 |
|---|---|---|
| `sensitive-zones.yaml` | 민감 **경로**: `frozen`(차단)/`protected`(승인)/`watched`(경고) | 🟡 조직 (왕관보석 경로) |
| `sink-registry.yaml` | L3 간접영향 추적 대상(sink) · `hops`(거리) · `maturity: shadow→enforcing` | 🟡 조직 (shadow 로 관찰 후 승격) |
| `approval-routing.yaml` | 닿은 영역 → 어느 리뷰어 | 🟡 조직 (실제 담당자) |
| `sensitive-capabilities.yaml` / `java-...` | 위험 능력 카탈로그 (기본 제공) | 확장만 (protected 상한) |
| `framework-annotations.yaml` | Spring 어노테이션 → 민감도 (기본 제공) | `frozen` 금지(추론 신호) |
| `language-routing.yaml` | 확장자 → 어느 분석기 | 보통 그대로 |
| `change-intent.yaml` | **대상 repo 가 제공**: `allowed_paths`·`forbidden_paths`·`expected_paths` | 변경 주체가 선언 |

### `change-intent.yaml` — 반드시 중첩 (제일 흔한 함정)

```yaml
change_intent:                       # ✓ 반드시 이 키 아래에!
  requirement_id: REQ-2026-001
  allowed_paths:   ["src/**"]        # 여기 밖 변경 → 의도이탈(승인요구)
  forbidden_paths: ["**/auth/**"]    # 여기 안 변경 → 차단
  expected_paths:  ["src/vendor/patch.py"]   # 반드시 바뀌어야 할 파일(패치 생존성)
```
- `expected_paths`: 선언한 파일이 diff 에 **없으면** "패치 유실 의심 → 승인요구". **리터럴 경로 권장**(글롭은 하위 파일 하나만 바뀌어도 충족되는 거친 보증).
- ⚠️ `allowed_paths`를 **top-level 에 두면** 빈 선언으로 읽혀 **모든 변경이 out_of_scope(승인요구)** — fail-safe 라 위험친 않으나 "왜 다 승인요구?" 혼란.

### glob 문법 (정확히)

경로 매칭은 다음만 지원한다. 라이브러리마다 `**` 의미가 달라 판정이 흔들리지 않도록 **킷 내장 매처로 고정**돼 있다.
- `**` = 다단계 디렉터리(0단계 이상), `*` = 단일 단계, 구분자는 항상 `/`, repo-root 상대.
- 예: `**/auth.py`(어느 깊이든 auth.py), `src/**`(src 하위 전부), `backend/*/config.py`(한 단계 아래 config.py).

---

## 6. 감사카드(`change-evidence.yaml`) 읽는 법

`--output`으로 지정한 파일. 사람 리뷰어가 30초에 위험을 파악하도록 만든다.

```yaml
change_evidence:
  requirement_id: FEAT-ADMIN         # 무슨 작업인지
  base_commit: 2526506...            # 어느 기준 대비
  verdict: approval_required          # ★정본 판정
  summary: {files_changed: 2, ...}   # 규모
  changed_files:                      # 파일별 민감도·의도내 여부
    - {path: blog.py, zone_level: protected, in_allowed_paths: true}
  reviewer_required: [security-reviewer]   # 누가 승인해야 하나
  coverage_statement: {checked: [...], not_checked: [...]}   # 본 것/못 본 것
  policy_sha: {sensitive-zones.yaml: <hash>, ...}   # 판정 당시 정책(재현성)
  python_version: "3.11.15"           # 파서 버전(재현 조건)
```

- **`policy_sha`·`python_version`** = "당시 어떤 규칙·도구로 판정했나"를 남겨 **재현성**을 보장한다. 정책이 바뀌면 이 값도 바뀐다.
- ⚠️ **카드 기본 출력이 대상 repo 안**이면 `git add -A` 로 커밋돼 **다음 diff 를 오염**시킨다 → `--output <외부경로>` 지정 또는 `.gitignore` 등록.

---

## 7. 결정성·재현성

- **결정적**: 같은 입력(같은 커밋·정책·파서) → 같은 판정. 자체 회귀 스위트가 md5 로 반복 검증.
- 재현하려면 **판정 대상이 되는 값**(verdict·gates·reasons·inputs)만 비교하고, **실행 시각·소요시간·경로 같은 관측 정보는 제외**해야 한다(그 값들은 실행마다 달라 정상).
- 카드의 `policy_sha` + `python_version` 을 함께 기록하면 "왜 이 판정이 나왔나"를 나중에 재현할 수 있다.

---

## 8. 자주 겪는 문제 (FAQ)

| 증상 | 원인 | 해결 |
|---|---|---|
| **모든 변경이 승인요구로 뜬다** | `change-intent.yaml`의 `allowed_paths`를 top-level 에 둠 | `change_intent:` 아래로 중첩 |
| **CI가 승인요구를 "실패"로 처리** | 종료코드만 보고 2와 1을 뭉갬 | 카드 `verdict` 읽기(2절) |
| **간접영향(L3)이 항상 승인요구** | sink 함수명이 콜그래프에서 안 풀림 → fail-closed | sink 함수명을 실제 정규화이름으로(모듈 함수 권장)·또는 sink 비움 |
| **tree-sitter 설치 실패** | Python 3.9 (핀 버전은 3.10+) | Python 3.10+ 사용 · 또는 Java/JS 없이 Python-only(무해) |
| **작은 변경(변수명·주석)인데 간접영향 뜸** | 라인 단위 탐지(의미 아님) — 보수적 설계 | 사람이 "리팩터" 확인 후 승인 (알려진 소음) |
| **판정에 blog.py 같은 게 안 잡힘** | 씨딩 누락(이름 신호 없는 파일) | 코드 분석으로 sensitive-zones 보강 |

---

## 9. 알려진 한계 (정직)

1. **exit code 2단계 손실** — 단순 CI가 승인요구(2)와 차단(1)을 뭉갤 수 있음. 근본 해결 = ADR-002 결과 파일 정본화(구현 대기). 그때까지 카드 `verdict`가 정본.
2. **라인 단위 변경 탐지** — 함수 안이 조금이라도(변수명·주석·공백) 바뀌면 그 함수를 "변경"으로 봄. 의미 동일성은 판단 안 함(과탐 방향·안전). 정밀화는 타입 분석 도입 시 후속.
3. **간접영향은 이름 기반** — 메서드/동적/리플렉션 호출은 완전 해소 못 함 → `coverage.unevaluated`로 정직 노출(조용히 안 넘김).
4. **언어별 깊이 차이** — Python 완전 / Java 함수·능력·간접영향(partial) / JS·TS 는 경로층만(심층 후속). 미지원 언어는 카드에 "심층분석 미지원" 명시.
5. **정적분석의 본질적 한계** — 런타임 실행경로·값 흐름은 못 봄. pass는 "안 걸림"이지 "안전 인증"이 아님(3절 coverage).

---

## 10. 킷은 생성물 — 편집 금지

`kit/gates/`·`policies/`·`templates/`·`tests/` 는 개발 저장소 스냅샷이다. **게이트 로직**을 고칠 일이 있으면 개발 저장소 원본을 고치고 `./kit/sync-from-dev.sh` 로 재생성한다. **정책(규칙)** 만 `--policies` 디렉터리에서 조직값으로 채운다.

---

**한 줄 요약**: 설치 → selftest → 씨딩(기계+사람) → `change-intent` 선언(중첩!) → `run.sh` → **종료코드는 힌트, 감사카드 `verdict`가 정본** · pass는 "미탐지"지 "안전 보증"이 아니며 coverage로 못 본 것을 확인.
