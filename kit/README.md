# AI Change Governance Kit

> **배포 가능한 스냅샷** — 개발 저장소(`.harness/gates`·`policies`)를 통째로 clone 하지 않고,
> 게이트+정책+manifest 만으로 변경 거버넌스를 돌리는 자립형 킷.
> **상태:** Draft (MVP-0·1·1.5·2 + MVP-3 J0 language routing seam + J1 Java inventory + J2 Java `@Gov`/framework annotations 반영). **개발 작업과 분리** — 이 폴더는 `sync-from-dev.sh` 로 생성되는 스냅샷이다.

## 이게 뭐냐

AI 가 만든 코드 변경(diff)을 **결정적으로**(LLM 없음, 규칙 대조만) 걸러
**"선언 의도 밖 / 필수 변경 파일 부재 / 민감영역 접촉 / 신규 위험능력 / sink 간접영향 / 정책 자기무력화"** 만
사람 승인으로 라우팅한다. 같은 입력이면 항상 같은 판정(결정론).

```
./run.sh <base>..<head> --repo <대상repo> [--policies <대상repo-policy-dir>]
   → 감사카드(evidence/change-evidence.yaml) + 최종판정
   → 종료코드 0 통과 / 1 차단 / 2 승인필요
```

## ⚠️ 이 킷은 생성물이다 — 직접 편집 금지

`gates/`·`policies/`·`templates/`·`tests/` 는 **개발 저장소에서 복사된 스냅샷**이다.
고칠 게 있으면 **개발 저장소 원본**(`.harness/gates`·`policies`)을 고치고 재동기화:

```bash
./sync-from-dev.sh      # ★MVP 완료마다 실행 → 킷을 완료 MVP 상태로 갱신
```

동기화는 끝에서 **dev 게이트 수 == kit 게이트 수**를 검증한다(누락 방지).

## 게이트 전량 (19종 — 누락 없음)

`run.sh` 는 아래 **판정 게이트**를 빠짐없이 조립한다. (초기 스텁 `review.sh` 및
`generate-change-evidence` 단독은 **능력·간접영향·정책변경 게이트를 누락**했으나, 이 킷의
`run.sh` 는 셋을 명시적으로 추가 조립한다.)

| 게이트 | 층 | 역할 | 판정 |
|---|---|---|---|
| `check-change-intent` | L1 | 의도 이탈(allowed/forbidden)·필수 변경 파일 부재(expected_paths) | 0/1/2 |
| `check-sensitive-zones` | L1 | 민감경로(frozen/protected/watched) | 0/1/2 |
| `check-function-gov-level` | L1 | Python `@gov` 및 Java `@Gov`/Spring 어노테이션 함수 레벨 | 0/1/2 |
| `check-new-capabilities` | L2 | 신규 위험능력(외부호출·암복호·실행) | 0/2 |
| `check-indirect-impact` | L3 | 등록 sink 의 N홉 의존함수 변경 | 0/2 |
| `check-policy-change` | meta | 정책 자기무력화·집행우회 | 0/2 |
| `generate-change-evidence` | 집계 | 위 L1 3축 조립 + 감사카드 생성 | 0/1/2 |

**추출 의존 게이트**(위 판정 게이트가 내부 `Path(__file__).parent` 로 import — 직접 호출 안 하나 **co-located 필수**):
`extract-python-inventory` · `map-diff-to-functions` · `classify-python-function-changes` · `extract-gov-annotations` · `extract-python-capabilities` · `extract-sinks` · `extract-callgraph`

**오프라인 도구**(spine hook 아님 — 온보딩·CI):
`bootstrap-sensitive-zones` · `bootstrap-sensitive-functions` → `./bootstrap.sh` 로 실행.

**언어 라우팅/J0 스모크 + J1 Java 인벤토리 + J2 Java 함수레벨 민감도**(spine hook 아님 — coverage 정직성·배포환경 실증):
`language-router` · `check-tree-sitter-languages` · `extract-java-inventory`.

→ 판정 7 + 추출 7 + 도구 2 + 언어 J0 2 + 언어 J1 1 = **19종 전량**. `manifest.yaml` `gates:` 에 명시.
Tree-sitter 기반 스모크를 배포지에서 재현하려면 `python3 -m pip install -r requirements.txt` 를 먼저 실행한다.

## 사용법

```bash
# 1) per-change 거버넌스 (핵심)
./run.sh <base>..<head> --repo <대상repo>

# 대상 저장소가 자체 정책을 운영하면 킷 기본 정책 대신 명시적으로 적용
./run.sh <base>..<head> --repo <대상repo> --policies <대상repo>/policies

# 2) 온보딩 씨딩(민감경로·함수 후보 draft — 자동적용 아님, 사람 검토)
./bootstrap.sh zones     <repo> --rules <rules.yaml>
./bootstrap.sh functions <repo>

# 3) 자체검증(게이트 무결·시험 살아있음 — 배포지에서 실증)
./selftest.sh            # 러너 스위트 + 뮤테이션
./selftest.sh --quick    # 러너 스위트만

# 4) 개발본과 재동기화(MVP 완료마다)
./sync-from-dev.sh
```

`--policies` override 디렉터리는 아래 6개 파일을 모두 포함해야 한다:
`sensitive-zones.yaml`, `sensitive-capabilities.yaml`, `approval-routing.yaml`,
`sink-registry.yaml`, `language-routing.yaml`, `framework-annotations.yaml`.
기존 도입처가 킷을 업그레이드할 때는 킷 동봉 `policies/language-routing.yaml` 을
override 디렉터리에 복사한 뒤 실행한다.

**대상 repo 에 `change-intent.yaml` 이 없으면** 의도층이 fail-closed(=차단)된다 —
이는 설계상 의도(TASK-001: 의도 선언 강제). 킷은 `policies/change-intent.template.yaml`·
`change-intent.example.yaml` 을 동봉한다.

선택 필드 `change_intent.expected_paths`에 반드시 diff에 나타나야 할 파일 경로를 선언할 수 있다.
각 패턴에 맞는 변경 파일이 하나도 없으면 패치 유실 가능성으로 승인요구(exit 2)하며,
감사카드 `intent_check.missing_expected`에 누락 패턴을 기록한다. 정확한 생존성 확인에는
리터럴 경로를 권장한다(글롭은 하위 파일 하나만 바뀌어도 충족되는 거친 보증).

### ⚠ 실사용 함정 2개 (외부 오픈소스 E2E 실측 발견 — D-051)

1. **`change-intent.yaml` 스키마는 반드시 `change_intent:` 아래 중첩.**
   `allowed_paths` 를 top-level 에 두면 게이트가 **빈 선언으로 읽어 모든 변경이
   out_of_scope(승인요구)** 가 된다(fail-safe 라 위험하진 않으나 "왜 다 승인요구?" 혼란).
   ```yaml
   # ✗ 틀림 (top-level)          # ✓ 맞음 (중첩 — change-intent.example.yaml)
   allowed_paths: ["src/**"]      change_intent:
                                    allowed_paths:
                                      - "src/**"
   ```
2. **감사카드 기본 출력이 대상 repo 안**(`change-evidence.yaml`) — `git add -A` 로
   커밋되면 **다음 diff 를 오염**시킨다. `--output <외부경로>` 지정 또는 대상 repo
   `.gitignore` 에 `change-evidence.yaml` 등록 권장.

   러너도 같은 상황을 감지하면 판정에는 영향을 주지 않는 `⚠` 안내를 출력한다.

### 외부 오픈소스 E2E 검증 결과 (2026-07-15 · D-051)

실제 오픈소스 4종(click·requests·flask = Python / gorilla-mux = Go)에 킷을 소급 적용:
- **Python 3종 × 4시나리오 = 12/12 기대 일치** — 무해변경 PASS · 신규능력(subprocess) 승인요구 ·
  선언범위 밖 승인요구 · frozen 접촉 차단.
- **Go(비-Python) 한계 실측**: 경로층(frozen 차단)은 언어 무관 작동 ✓, **능력층은 Go 의
  `exec.Command` 를 못 잡음**(PASS) — 능력·함수층 Python 전용이라는 알려진 갭의 실증.

게이트 파일 부재, Python Traceback, 60초 타임아웃(`ACGH_GATE_TIMEOUT_SECONDS`로 조정),
계약 밖 종료코드는 정상 판정으로 흡수하지 않는다. 러너는 이를 **분석 실패**와
`tool_owner: change-governance-kit-owner`로 표시하고 최소 승인요구(exit 2)로 닫는다.

## spine 연동 (`manifest.yaml`)

이 킷은 spine 의 **verify 단계** kit 이다. 러너 계약 = `bash · 위치인자 · cwd=kit · exit code`
— 우리 `run.sh` 와 일치해 뼈대를 그대로 쓴다.

## 🔴 알려진 갭 (Draft 인 이유)

1. **판정 3단계 → spine 2단계 손실.** spine 러너는 exit 0=pass / 비0=fail(2단계)라
   **승인요구(2)와 차단(1)이 둘 다 fail 로 뭉개질 위험**. 킷의 핵심(위험을 *차단이 아니라
   사람에게 올림*)이 훼손될 수 있음. **완전 해결 = ADR-002 `acgh-result` 정본 결과계약 구현
   (현재 미구현)**. 그때까지 `manifest.yaml verdict_mapping` 은 draft.
2. **감사카드 verdict vs 최종 verdict 불일치 가능.** `generate-change-evidence` 카드는
   L1 3축만 반영. 킷 최종판정은 능력·정책 게이트를 포함한 **전체 조립**이라, 카드가 pass 여도
   최종이 승인요구일 수 있다(능력 탐지 시). **후속: ADR-002 acgh-result 가 카드를 통합**하면 해소.
3. **spine 프로덕션 계약 미검증** — `manifest.yaml` apiVersion·필드명은 TO-BE 규격 기준 초안.
   spine 오너 확인 필요(kit-변환-검토 §7).
4. **Java 능력·콜그래프 및 JS/TS 심층 판정·cross-commit** 은 미포함. 경로층은 언어무관 동작하고,
   MVP-2 간접영향 추적은 단일 diff 내 Python 정적 호출만 분석한다.
   MVP-3 J2 는 Java `@Gov`/Spring 어노테이션 함수레벨 판정까지 포함하며, Java 능력·콜그래프는 layer coverage 로 미분석 노출한다.

## 반영된 MVP

- **MVP-0** 경로·의도(change-intent·sensitive-zones·감사카드)
- **MVP-1** 함수·능력(@gov·AST 인벤토리·능력 카탈로그)
- **MVP-1.5** 신뢰·도입 보강(정책완화 게이트·감사카드 정직화·성숙도 shadow·씨딩·뮤테이션·광역의도)
- **MVP-2** 영향추적(sink 등록·정적 콜그래프·N홉 역도달성·coverage 정직성) + 패치 생존성(`expected_paths` 부재 탐지)
- **MVP-3 J0** 언어 라우팅 seam(공통 IR 필드·확장자 라우터·tree-sitter Java/JS/TS/TSX 스모크·stub/unsupported coverage)
- **MVP-3 J1** Java 클래스/메서드/생성자 인벤토리와 diff 헝크→메서드 매핑
- **MVP-3 J2** Java `@Gov` 및 Spring/Jakarta 프레임워크 어노테이션 기반 함수레벨 민감도 판정
