# 배포 킷 도입 가이드 (다른 저장소에 반영하기)

> **목적**: 이 킷(`kit/`)을 **다른 저장소/환경에 붙여서** 변경 거버넌스를 돌리는 사람을 위한 **단계별 도입 + 규칙 설정** 가이드.
> **레퍼런스(전체 게이트·계약·알려진 갭)**: `kit/README.md`. 이 문서는 "어떻게 도입하고 무슨 규칙을 어떻게 채우나"에 집중한다.
> **핵심 성질**: 판정은 **결정적**(같은 입력=같은 출력) · **LLM·추정 없음**(정책 YAML + 코드 구조 대조만) · **차단은 1층 frozen만**, 나머지는 "사람 승인 요구"가 상한.

---

## 1. 킷이 뭐고 뭘 검사하나

**킷 = 이 하네스의 "배포 가능한 스냅샷"** — 개발 저장소를 통째로 clone 하지 않고, 게이트 21종 + 정책 + 러너만으로 대상 repo 의 변경(diff)을 판정한다. 현재 버전 `0.3.4-mvp3-java-l3`.

한 번의 `run.sh` 실행이 바뀐 파일을 **확장자별로 알맞은 분석기에 보내** 아래 5층으로 판정하고, 사람이 30초에 읽는 **감사카드**를 낸다:

| 층 | 게이트 | 무엇을 잡나 | 판정 상한 |
|---|---|---|---|
| **L1 직접** | `check-change-intent` | 선언 의도 밖 변경 · forbidden 경로 · **선언한 파일 미변경(패치 유실)** | 차단 가능 |
| | `check-sensitive-zones` | 민감 경로(frozen/protected/watched) 접촉 | **frozen=차단** |
| | `check-function-gov-level` | 민감 함수(`@gov`/`@Gov`)·Spring 어노테이션 직접 수정 | 차단 가능(@Gov frozen) |
| **L2 능력** | `check-new-capabilities` | 새로 들여온 위험 능력(exec·역직렬화·외부호출·암복호…) | **승인요구**(차단 없음) |
| **L3 간접** | `check-indirect-impact` | 바뀐 함수가 민감 함수(sink)의 상류인가 | **승인요구**(차단 없음) |
| **meta** | `check-policy-change` | 정책·집행 스위치를 몰래 완화(자기무력화)했나 | 승인요구 |
| 집계 | `generate-change-evidence` | 위 L1 3축 조립 + 감사카드 생성 | — |

> 나머지 14종(추출·언어·도구 게이트)은 위 판정 게이트가 내부에서 쓰는 부품이라 **같은 폴더에 반드시 함께** 있어야 한다(`sync-from-dev.sh` 가 누락 검증). 전체 목록은 `kit/README.md`.

**지원 언어**: Python(완전) · Java/Spring(함수·능력·간접영향 **partial**) · JS/TS(라우팅 seam만·심층층 후속) · 그 외(경로층만 + 카드에 "심층분석 미지원" 명시).

---

## 2. 규칙(정책) — 무엇을 어떻게 채우나 ★도입의 핵심

판정은 전부 **코드 밖 YAML 정책**에서 나온다(게이트 코드엔 규칙 하드코딩 없음). 도입 = **이 정책들을 대상 조직/repo 에 맞게 채우는 일**이다. 킷은 기본 초안을 동봉하고, 대상이 `--policies <dir>` 로 자기 정책을 덮어쓸 수 있다.

| 정책 파일 | 무엇을 정하나 | 누가 채우나 |
|---|---|---|
| **`sensitive-zones.yaml`** | 민감 **경로** 지도: `frozen`(차단)/`protected`(승인)/`watched`(경고). 여기 없는 경로는 전부 자유(🟢). | 🟡 **조직이 자기 "왕관보석" 경로**로 채움(정산·이자·auth·crypto·db/migrations…). 전수 분류 금지 — 핵심만. |
| **`sink-registry.yaml`** | L3 간접영향의 **추적 대상(sink)**. frozen 자동 sink·`@gov(sink=true)` 로 못 거는 함수만 명시 등록. `hops`(추적 거리)·`maturity: shadow→enforcing`. | 🟡 조직. 신규 sink 는 **shadow(관찰만)** 로 시작 후 승격. |
| **`approval-routing.yaml`** | 닿은 영역/능력 → **어느 리뷰어**가 승인해야 하나. | 🟡 조직이 실제 담당자(그룹/이름) 기입. |
| **`sensitive-capabilities.yaml`** | Python 위험 능력 카탈로그(subprocess·pickle·eval…). `source`/`owner` 메타 포함. | 기본 제공 — 조직 확장 가능(protected/watched 상한). |
| **`java-sensitive-capabilities.yaml`** | Java 위험 능력(Runtime.exec·역직렬화·리플렉션·문자열 SQL·JNDI·외부호출…). | 기본 제공 — 조직 확장 가능. |
| **`framework-annotations.yaml`** | Spring/Jakarta 어노테이션 → 민감도(`@PreAuthorize`→protected·`@Transactional`→watched…). | 기본 제공. **불변식: `frozen` 금지**(추론 신호라 2층 상한=승인, 어기면 검증오류+protected clamp). |
| **`language-routing.yaml`** | 확장자 → 어느 심층 분석기로. 미지원 확장자는 coverage 에 노출. | 보통 그대로. 층별 `status`(supported/partial/stub) 관리. |
| **`change-intent.yaml`** | **대상 repo 가 제공**: `allowed_paths`/`forbidden_paths`/`expected_paths`(반드시 바뀌어야 할 파일). | 변경 주체(AI·개발자)가 **변경 전에 선언**. |

**도입 팁**: 처음부터 손으로 채우지 말고 **`bootstrap.sh` 로 후보를 자동 씨딩** → 사람이 승인만(아래 3단계).

---

## 3. 단계별 도입

```bash
# ── 0) 의존성 (최초 1회) — tree-sitter 파서 포함
python3 -m pip install -r kit/requirements.txt
#   ※ tree-sitter 핀 버전은 Python 3.10+ 필요. 3.9(맥 기본)면 JS/TS 스모크 1건만 실패(무해).

# ── 1) 킷이 살아있나 자체검증 (게이트 누락 시 FAIL)
./kit/selftest.sh            # 러너 스위트 + 뮤테이션
./kit/selftest.sh --quick    # 빠르게(러너만)

# ── 2) 민감경로 후보 자동 씨딩 (사람은 승인만 — 백지에서 손으로 안 씀)
./kit/bootstrap.sh zones     /path/to/target-repo --rules <rules.yaml>
./kit/bootstrap.sh functions /path/to/target-repo
#   → sensitive-zones 초안 YAML 출력. 사람이 검토·확정해 policies/ 에 반영.

# ── 3) 대상 repo 에 change-intent.yaml 작성 (변경 의도 선언)
#   반드시 change_intent: 아래 중첩! (함정 #1 — 아래 참고)

# ── 4) 변경 검사 (핵심)  base..head = git 리비전 범위
./kit/run.sh main..feature --repo /path/to/target-repo
#   대상이 자기 정책을 운영하면:
./kit/run.sh main..feature --repo /path/to/target --policies /path/to/target/policies
#   → 종료코드 0 통과 / 1 차단 / 2 승인필요  +  evidence/change-evidence.yaml

# ── 5) (CI 연동) run.sh 를 verify 단계에 걸고 종료코드로 게이팅
```

**`base..head` 란**: 검사할 git 변경 범위. `main..feature`(feature 가 main 대비 바꾼 것), `HEAD~1..HEAD`(직전 커밋). 이 범위 diff 를 판정한다.

**`--policies <dir>` 는 아래 7개를 모두 포함**해야 함: `sensitive-zones` · `sensitive-capabilities` · `java-sensitive-capabilities` · `approval-routing` · `sink-registry` · `language-routing` · `framework-annotations`.

---

## 4. 판정·종료코드 읽는 법

```
exit 0  = 통과      (정책 위반 미탐지 — "안전 인증"이 아니라 "미탐지")
exit 2  = 승인필요   (사람이 봐야 함 — 능력·간접영향·의도이탈·protected 등)
exit 1  = 차단      (frozen 접촉·forbidden 등 — 1층만)
```

**감사카드(`change-evidence.yaml`)** 에 담기는 것:
- 무엇이 바뀌었나(파일·함수) · 어느 층에 걸렸나 · 누가 승인해야 하나(routing)
- **coverage** = "이 판정이 **본 것 / 보지 않는 것**"(정직 고지 — PASS를 안전보증으로 오독 방지)

**분석 실패는 통과로 흡수하지 않는다**: 게이트 파일 부재·Python Traceback·타임아웃(`ACGH_GATE_TIMEOUT_SECONDS`)·계약 밖 종료코드 → **"분석 실패"로 명시 + 최소 승인요구(exit 2) + `tool_owner` 표시**(fail-closed).

---

## 5. 실사용 함정 & 한계 (정직)

**함정 2개(E2E 실측·D-051)**:
1. **`change-intent.yaml` 은 반드시 `change_intent:` 아래 중첩.** top-level 에 `allowed_paths` 두면 빈 선언으로 읽혀 **모든 변경이 승인요구**(fail-safe라 위험친 않으나 혼란).
   ```yaml
   change_intent:            # ✓ 이렇게 (중첩)
     allowed_paths: ["src/**"]
     forbidden_paths: ["**/auth/**"]
     expected_paths: ["src/vendor/patch.py"]   # 반드시 바뀌어야 할 파일(패치 생존성)
   ```
2. **감사카드 기본 출력이 대상 repo 안** → `git add -A` 로 커밋되면 다음 diff 오염. `--output <외부경로>` 지정 또는 `.gitignore` 등록.

**한계(과장 금지)**:
- **Java L3 = partial**: sink 전방폐쇄에 외부 호출이 하나라도 있으면 지연 dispatch 가 승인요구로 **승격(소음·O-14)**. 카드 `inferred: true` = 실제 호출 관측이 아니라 **보수 추정 홉 포함**. `dead_ends=` 에 무관 이름 섞일 수 있음(O-22). → **정밀 타입솔버 도입 시 개선 예정**.
- **JS/TS·그 외 언어**: 심층층 없음 — 경로층만 작동하고 카드에 "심층분석 미지원" 명시.
- **cross-commit 누적**(여러 PR 로 쪼개 우회)·spine 2단계 종료코드 손실(ADR-002 미구현)은 알려진 갭(`kit/README.md` §알려진 갭).

---

## 6. 킷은 생성물 — 직접 편집 금지

`kit/gates/`·`policies/`·`templates/`·`tests/` 는 개발 저장소 스냅샷이다. **게이트 로직**을 고칠 일이 있으면 개발 저장소 원본(`.harness/gates`)을 고치고 `./kit/sync-from-dev.sh` 로 재생성한다. **정책(규칙)** 은 대상 repo 쪽 `--policies` 디렉터리에서 조직값으로 채운다.

---

**요약**: ① `pip install -r kit/requirements.txt` → ② `selftest.sh` 로 살아있나 확인 → ③ `bootstrap.sh` 로 민감경로 씨딩·사람 승인 → ④ 대상 repo 에 `change-intent.yaml`(중첩!) → ⑤ `run.sh <base>..<head> --repo <대상> [--policies <대상정책>]` → ⑥ 종료코드·감사카드로 게이팅. 규칙은 전부 정책 YAML, 차단은 frozen만, 나머지는 사람 승인.
