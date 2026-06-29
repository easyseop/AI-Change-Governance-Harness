# review-notes.md — Claude 리뷰 기록 (정책 의도 대비 검수)

> 게이트가 "도는지"가 아니라 "내가 의도한 위험을 잡는지"를 본다.
> 결과 승급은 `collab/decisions.md`. 여기는 근거·검증·비차단 관찰.

---

## TASK-001 `check-change-intent` — 리뷰통과 (2026-06-29)

- 대상: commit `ff75529`, 브랜치 `codex/2026-06-29-task001-change-intent`
- 파일: `.harness/gates/check-change-intent.py` (신규 192줄)
- 결정: **D-006 리뷰통과**

### 수용기준 6/6 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | intent 누락 → 실패 + "의도 선언 누락" | ✅ blocked(1), 메시지 출력 | 없는 경로 전달 → exit 1 |
| 2 | allowed 안에만 → 통과 | ✅ pass(0) | admin 2파일 → exit 0 |
| 3 | allowed 밖 → out_of_scope, 승인(2) | ✅ approval(2) | reporting 파일 → exit 2 |
| 4 | forbidden 닿음 → 차단(1) | ✅ blocked(1) | auth 파일 → exit 1 |
| 5 | glob `**`/`*`, OS 무관 | ✅ | 아래 엣지 표 |
| 6 | 변경 0건 → 통과 | ✅ pass(0) | 빈 입력 → exit 0, "changed_files: 0" |

### glob 엣지 검증 (커스텀 매처라 별도 확인)
| 케이스 | 기대 | 결과 |
|---|---|---|
| `src/*` vs `src/a/b.py` (`*`는 `/` 안 넘음) | out_of_scope | ✅ exit 2 |
| `src/*` vs `src/a.py` | pass | ✅ exit 0 |
| `**/settlement/**` vs `backend\core\settlement\calc.py` (백슬래시) | blocked | ✅ exit 1 (정규화) |
| 리네임 `R100 old → settlement/new` (목적지 경로 판정) | blocked | ✅ exit 1 |
| forbidden + out_of_scope 동시 | blocked(우선) | ✅ exit 1 |

### 판정 우선순위 (이 게이트 한정, 확정)
`forbidden(blocked,1)` > `out_of_scope(approval_required,2)` > `pass(0)`.
한 파일이 forbidden∩allowed 면 forbidden 우선(코드 `in_forbidden` 선검사). TASK-003 최종 verdict 합성과 일관.

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 게이트 1개(신규) + `handoff-log.md`(+1줄, 허용) + `summaries/2026-06-29.md`(신규, 공동출력). **Claude 소유 파일 무수정.**
- 무관 리팩터/포맷/이름변경 없음. diff 최소. **scope-creep / over-reach 없음.**
- 결정성: 출력에 시각·난수 없음, `--json`은 `sort_keys=True`. 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — 후속 태스크에서 정합만 맞추면 됨)
1. **광범위 `except Exception → blocked(1)`**: git ref 오류·YAML 파싱오류 등 *도구 오류*도 정책 *차단*과 같은 exit 1 로 수렴(fail-closed). MVP-0 종료코드 계약(0/1/2)에 별도 에러코드가 없어 안전한 선택. 단 사람이 "정책 차단"과 "실행 실패"를 출력 메시지로 구분할 수 있어야 함 — 현재 `error` 필드/`BLOCKED: <error>` 로 구분됨. 수용.
2. **intent 파일은 있으나 내용 비정상**(`change_intent` 키 없음/빈 allowed): 모든 변경이 out_of_scope → approval(2). 누락(파일없음)=blocked 와 다른 결과인데, 의도적 fail-safe 로 수용. TASK-004 에서 별도 fixture 불필요(수용기준 미요구).
3. **리네임 source 경로**: 목적지만 판정(표준). forbidden→밖으로 나가는 리네임은 안 잡지만 MVP-0 범위상 수용.

→ 위 3건은 **차단 사유 아님**. TASK-002/003/004 진행 시 정합(특히 #1 의 verdict 합성, #2 의 fixture 기대)만 유지하면 됨.

---

## TASK-002 `check-sensitive-zones` — 리뷰통과 (2026-06-30)

- 대상: commit `704f7a0`, 브랜치 `codex/2026-06-30-task002-sensitive-zones`
- 파일: `.harness/gates/check-sensitive-zones.py` (신규 245줄)
- 결정: **D-008 리뷰통과 + Claude 머지(비민감)**

### 수용기준 6/6 (경험적 검증)
| # | 기준 | 결과 | 검증 |
|---|---|---|---|
| 1 | frozen 닿음 → 차단(1), 사유에 path+reason | ✅ blocked(1) | `src/settlement/calc.py` → exit 1, `frozen: <path> (<reason>)` |
| 2 | protected 닿음 → 승인요구(2), required_approval 포함 | ✅ approval(2) | `src/auth/login.py` → exit 2, `required_approval=security-reviewer` |
| 3 | watched 닿음 → 통과+경고(0) | ✅ pass(0) | `src/common/util.py` → exit 0, "PASS: watched ..." |
| 4 | zones 미매칭만 → 통과 | ✅ pass(0) | `src/ui/button.tsx` → exit 0, 경고 없음 |
| 5 | block/approve/warn_levels 를 policy 에서 읽음(하드코딩 금지) | ✅ | protected→block_levels 로 옮긴 policy 에서 auth 가 blocked(1) 로 변함 |
| 6 | 다중 level 매칭 → 가장 강한 것 채택 | ✅ | `src/settlement/common/x.py` (frozen∩watched) → blocked(1) |

### 엣지 검증
| 케이스 | 기대 | 결과 |
|---|---|---|
| 리네임 `R100 old → auth/new` (목적지 경로 판정) | approval | ✅ exit 2 (`parts[2]` 사용) |
| `**/*.k8s.yaml` vs `deploy/app.k8s.yaml` | approval | ✅ exit 2 |
| `db/migrations/**` vs `db/migrations/001_add.sql` | approval | ✅ exit 2 |
| mixed frozen+protected+watched 한 diff | blocked + 세 목록 전부 증거 보존 | ✅ exit 1, frozen/protected/watched_touched 각각 채워짐 |
| 빈 diff | pass | ✅ exit 0, "changed_files: 0" |
| policy 파일 없음 | blocked(fail-closed) | ✅ exit 1, `BLOCKED: <error>` |

### 보수적 개발 평가축 (COMMON-RULES §1)
- 건드린 파일: Codex 소유 게이트 1개(신규) + `handoff-log.md`(+1줄) + `summaries/2026-06-30.md`(신규). **Claude 소유 policy 무수정.**
- 무관 리팩터/포맷/이름변경 없음. TASK-001 의 glob 매처·종료코드 계약·`sort_keys=True`·fail-closed 패턴을 일관되게 재사용. **scope-creep / over-reach 없음.**
- 결정성: 출력에 시각·난수 없음, 목록 `sorted`, `--json` `sort_keys=True`. 같은 입력=같은 출력 ✅.

### 비차단 관찰사항 (보정요청 아님 — 후속 태스크에서 정합만)
1. **분류되지 않은 level 은 조용히 무시**: zone 의 `level` 이 block/approve/warn 어디에도 없으면 `level_strength=0` → 어떤 touched 목록에도 안 들어가 통과 처리됨. 현 policy 는 모든 level 이 frozen/protected/watched 라 무해. 단 정책 작성자가 오타(예: `protcted`)를 내면 *조용히 통과*될 수 있음 — MVP-1 에서 "미분류 level 경고" 고려. 수용.
2. **같은 path 가 동급 protected 여러 zone 매칭 시 중복 레코드**(예: `infra/**` ∩ `*.k8s.yaml`): 둘 다 출력됨(둘 다 platform-reviewer). 차단 판정엔 무영향, TASK-003 의 `reviewer_required` 중복제거에서 정리 예정. 수용.
3. **fail-closed 광범위 except → blocked(1)**: TASK-001 #1 과 동일 설계. 도구오류와 정책차단을 `error` 필드/`BLOCKED: <error>` 메시지로 구분. 수용.

→ 위 3건은 **차단 사유 아님**. TASK-003(`generate-change-evidence`) 에서 #2 의 reviewer 중복제거, verdict 합성(frozen/forbidden→blocked) 정합만 유지하면 됨.
