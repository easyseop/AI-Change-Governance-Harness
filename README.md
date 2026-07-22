# AI Change Governance Harness

> 🔴 **새 세션(Claude/Codex/사람)이면 `START-HERE.md` 부터 읽으세요.** 역할별 첫 할 일이 정리돼 있습니다.

> AI가 만든 코드 변경(diff)이 **선언한 의도 범위 안에 머물렀는지**, **민감 영역을 건드렸는지**,
> **새 위험 능력을 들여왔는지**, **민감 로직에 간접 영향을 주는지**를 **결정적으로**(LLM·추정 없이)
> 가려내, 사람이 **위험 변경 후보만** 보게 하는 하네스.
> (은행 반입 하네스군의 `06.운영관리하네스` 슬롯 — 변경 거버넌스)

## 왜

AI가 요구사항을 보고 방대한 코드를 직접 바꾸는 시대에, 무엇을·어디를·민감한 곳을 건드렸는지
사람이 모든 diff 를 전수검토하는 건 불가능하다. 이 하네스가 **위험 변경만 좁혀서** 사람 승인으로 라우팅한다.
판정은 **결정적**(같은 입력 = 같은 출력)이고 **LLM·추정을 쓰지 않는다** — 정책(YAML) + 코드 구조 분석만.

## 무엇을 잡나 — 5개 탐지 층

```
change-intent.yaml (변경 의도 선언)  +  git diff(base..head)
        │
  L1 직접 ── check-change-intent      → 의도 범위 밖 / forbidden / 선언한 파일 미변경(패치 유실)
          ├─ check-sensitive-zones    → 민감 경로(frozen/protected/watched) 충돌
          └─ @gov/어노테이션 함수레벨   → 민감 함수·Spring 어노테이션 직접 수정
  L2 능력 ── check-new-capabilities    → 새로 들여온 위험 능력(exec·역직렬화·외부호출 등)
  L3 간접 ── check-indirect-impact     → 바뀐 함수가 민감 함수(sink)의 상류인가(간접 영향)
  meta   ── check-policy-change        → 정책·집행 스위치를 몰래 완화(자기무력화)했나
        ↓
   통과(exit 0) / 승인필요(2) / 차단(1)   +  감사카드(change-evidence.yaml)
```

**판정 원칙(불변식)**: **1층 `frozen` 만 자동 차단.** 2·3층은 **자동 차단 없이 "사람 승인 요구"가 상한**
(추론 기반이라 차단은 위험). 불완전할 땐 **과탐(승인) 쪽으로 기울고 과소탐(놓침)은 금지**.

## 지원 언어

| 언어 | 경로·의도 층 | 함수/능력 층 | 간접영향(L3) |
|---|---|---|---|
| **Python** | ✅ | ✅ | ✅ |
| **Java / Spring** | ✅ | ✅ (`@Gov`·Spring 어노테이션·능력 카탈로그) | ✅ **partial**(소음·초기화 컨텍스트 일부 미커버 — 정직 고지) |
| **JS/TS** | ✅ | ⬜ (라우팅 seam만 · 후속 W1) | ⬜ |
| 그 외 | ✅ (경로층) | — | 감사카드에 "심층분석 미지원" 명시 |

- **경로 기반 층(의도·민감경로·정책)은 언어무관** — 어떤 언어든 즉시 작동.
- **깊은 층(함수·능력·간접영향)은 언어별 어댑터** — Python(`ast`)·Java/JS(tree-sitter)가 공통 IR로 판정 엔진에 물림.
  설계: `docs/multi-language-adapter-design.md`.

## 배포 키트 (`kit/`)

**키트 = 이 하네스를 다른 저장소에 바로 붙일 수 있는 "배포 가능한 스냅샷"이다.**
개발 저장소의 게이트·정책·템플릿·테스트를 한 폴더로 묶어(`sync-from-dev.sh` 로 생성),
대상 repo 의 변경을 검사하고 감사카드를 낸다. 현재 버전 **`0.3.4-mvp3-java-l3`**(게이트 21종, MVP-0~3 반영).

### 사용법

```bash
# 0) 의존성 (최초 1회) — tree-sitter 파서 포함
python3 -m pip install -r kit/requirements.txt

# 1) 대상 저장소의 변경을 검사  (base..head = git 리비전 범위)
./kit/run.sh main..feature --repo /path/to/target-repo
#   → 통과(exit 0) / 승인필요(2) / 차단(1)  +  evidence/change-evidence.yaml(감사카드)
#   ※ 대상 repo 는 change-intent.yaml(변경 의도 선언)을 제공한다(없으면 의도층 fail-closed).

# 2) 대상 저장소 "자기 정책"으로 집행  (온보딩 — 대상이 선언한 frozen/sink 를 존중)
./kit/run.sh main..feature --repo /path/to/target --policies /path/to/target/policies

# 3) 킷 자체검증 (배포지에서 "게이트가 살아있나" 실증 — 게이트 누락 시 FAIL)
./kit/selftest.sh

# 4) 온보딩 — 대상 repo 스캔해 민감경로 후보 자동 씨딩(사람은 승인만)
./kit/bootstrap.sh /path/to/target-repo

# 5) (개발자 전용) dev 저장소에서 킷 재생성 — MVP 완료마다
./kit/sync-from-dev.sh
```

- **`base..head`** = 검사할 git 변경 범위. 예: `main..feature`(feature 브랜치가 main 대비 바꾼 것),
  `HEAD~1..HEAD`(직전 커밋). 이 범위의 diff 를 게이트가 판정한다.
- **감사카드(`change-evidence.yaml`)** = 사람 리뷰어가 30초 안에 위험을 파악하도록,
  무엇이 바뀌었고 어느 층에 걸렸고 누가 승인해야 하는지 + **"이 판정이 본 것 / 보지 않는 것"**(coverage)을 담는다.
- **다른 저장소에 도입/반영하려면 → `docs/kit-onboarding.md`** (단계별 도입 + 규칙 설정법).
- 상세 운영·게이트 레퍼런스: `kit/README.md`.

## 저장소 구조

```
docs/        설계·협업 프로토콜 (Claude)
policies/    sensitive-zones · sensitive-capabilities · change-intent · sink-registry ... (Claude 초안, 🟡 조직값)
templates/   change-evidence 감사카드 스키마 (Claude)
.harness/gates/  게이트 21종 (Codex 구현)
tests/       fixtures + 러너 + 뮤테이션 + parity (Codex)
kit/         배포 킷 — dev 스냅샷 (run.sh·sync·selftest·bootstrap)
collab/      questions·answers·decisions·handoff-log·needs-human (비동기 협업)
summaries/   날짜별 작업 요약 (푸시마다 누적)
COMMON-RULES.md  공통규칙(은행운영·보수적개발·브랜치/커밋/요약) — 둘 다 필독, 형 소유
PROJECT.md · TASKS.md · CLAUDE.md · AGENTS.md
```

## 협업 모델 (상호견제)

- **Claude** = 판단/정책/리스크/리뷰 · **Codex** = 구현/테스트/게이트 · **형(사람)** = 최종 승인.
- Claude 는 **게이트 코드를 직접 작성하지 않는다**(자기가 짠 걸 자기가 검수하면 무의미).
- 직접 대화 없이 Git 파일(`TASKS.md`·`collab/`)로 비동기 협업. 상세 `docs/collab-protocol.md`.

## 현재 상태

- **MVP-0**(경로·의도) · **MVP-1**(Python 함수/능력) · **MVP-1.5**(신뢰·운영성) · **MVP-2**(간접영향) · **MVP-3**(다국어·Java) — **완료·킷 반영**.
- 킷 `0.3.4-mvp3-java-l3` (Java 직접탐지 + 간접영향 partial).
- **후속**: Java L3 소음 정밀화(TASK-041, 정밀 타입솔버 도입 시 · 현재 이월) · Frontend(JS/TS) 심층층(W1).
- 진행 상세: `TASKS.md` · `collab/decisions.md`.
