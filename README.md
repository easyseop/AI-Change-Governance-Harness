# AI Change Governance Harness

> 🔴 **새 세션(Claude/Codex/사람)이면 `START-HERE.md` 부터 읽으세요.** 역할별 첫 할 일이 정리돼 있습니다.

> AI가 만든 코드 변경(diff)이 **선언한 의도 범위 안에 머물렀는지**, **민감 영역을 건드렸는지**
> 결정적으로 가려내, 사람이 **위험 변경 후보만** 보게 하는 하네스.
> (은행 반입 하네스군의 `06.운영관리하네스` 슬롯 — 변경 거버넌스)

## 왜
AI가 요구사항을 보고 방대한 코드를 직접 바꾸는 시대에, 무엇을·어디를·민감한 곳을 건드렸는지
사람이 모든 diff 를 전수검토하는 건 불가능하다. 이 하네스가 위험 변경만 좁혀서 보여준다.

## 어떻게 (한 장)
```
change-intent.yaml (변경 의도 선언)  +  git diff
        │
   ├─ check-change-intent      → 의도 범위 밖/forbidden 건드렸나
   ├─ check-sensitive-zones    → 민감 경로(frozen/protected/watched) 충돌
   └─ generate-change-evidence → 변경 감사카드 + 리뷰어 추천
        ↓
   통과 / 차단 / 승인필요   (+ change-evidence.yaml)
```

## 구조
```
docs/        설계·협업 프로토콜 (Claude)
policies/    sensitive-zones · change-intent · approval-routing (Claude 초안, 🟡 조직값)
templates/   change-evidence 감사카드 스키마 (Claude)
.harness/gates/  게이트 3종 (Codex 구현)
tests/       fixtures + 러너 (Codex)
collab/      questions·answers·decisions·handoff-log·locks·needs-human (협업)
summaries/   날짜별 작업 요약 (푸시마다 누적)
COMMON-RULES.md  공통규칙(은행운영 관점·보수적개발·브랜치/커밋/요약·형의 요구사항) — 둘 다 필독, 형 소유
PROJECT.md · TASKS.md · CLAUDE.md · AGENTS.md
```

## 협업 모델
- **Claude** = 판단/정책/리스크/리뷰 · **Codex** = 구현/테스트/게이트.
- 직접 대화 없이 Git 파일(`PROJECT.md`·`collab/`)로 비동기 협업. 상세 `docs/collab-protocol.md`.

## 실행 방법 (MVP-0)
```bash
python3 .harness/gates/check-change-intent.py <base>..<head> change-intent.yaml
python3 .harness/gates/check-sensitive-zones.py <base>..<head> policies/sensitive-zones.yaml
python3 .harness/gates/generate-change-evidence.py <base>..<head> --change-intent change-intent.yaml
python3 .harness/gates/extract-python-inventory.py path/to/file.py --json
python3 .harness/gates/map-diff-to-functions.py <base>..<head> --json
python3 .harness/gates/classify-python-function-changes.py <base>..<head> --json
python3 .harness/gates/extract-gov-annotations.py path/to/file.py --json
python3 .harness/gates/check-function-gov-level.py <base>..<head> policies/sensitive-zones.yaml --json
python3 .harness/gates/extract-python-capabilities.py path/to/file.py policies/sensitive-capabilities.yaml --json
python3 .harness/gates/check-new-capabilities.py <base>..<head> policies/sensitive-capabilities.yaml --json
python3 .harness/gates/check-policy-change.py <base>..<head> --json
bash tests/run-tests.sh
```

## 현재 상태
**MVP-0 스캐폴딩 완료** (Claude 측). 게이트 구현은 Codex 대기 — `PROJECT.md` 참고.
