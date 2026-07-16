# 다국어 확장 설계 — 언어 어댑터 아키텍처 (Java/Spring 우선)

> **상태**: Draft — 형 방향 승인(2026-07-16): **① Java/Spring 먼저 ② tree-sitter 백본(Python `ast` 는 그대로 유지)**. 상세 논거·문답 = `collab/decisions.md` D-061.
> **왜 필요한가**: 지금 하네스의 **깊은 층**(함수레벨 `@gov`·신규능력·간접영향)은 Python `ast` 에 묶여 있다. 경로 기반 층은 이미 언어무관이라 작동하지만, Java/Spring·프론트의 **함수·능력·영향**은 못 본다. 이 설계는 **판정 엔진을 하나로 두고 언어별 "추출기"만 갈아끼워** 다국어를 지원한다.
> **한 줄**: N개 언어 × 4개 추출기 → **판정 엔진 1개**. 판정 로직(차단/승인/정직성)은 언어 수만큼 늘지 않는다.

---

## 1. 불변 원칙 (새 언어에도 그대로)

- **🔴 파이썬 동등성(parity) — 최우선 합격기준**(형 지시 2026-07-16): 새 언어는 Python 과 **동일 성능**을 내야 한다. 2등 시민 금지. 정의·강제장치 = **§1.5**.
- **판정 불변식 유지**: 1층 `frozen` 만 차단, **2·3층은 자동 차단 금지·승인요구 상한**(D-004). LLM·값추정 금지 — **결정적**.
- **보수적 개발**: **Python(`ast`) 게이트는 손대지 않는다**(91/91 + 뮤테이션 + D-005~057 검증자산 보존). 새 언어는 **기존 위에 얹기**(대규모 리팩터·통일성 목적 재작성 금지).
- **정직성(TASK-019 계보)**: 미지원 확장자·미해소 호출·프레임워크 간접(DI/AOP)은 **감사카드 coverage 에 노출**한다. **"지적 없음"을 "분석했고 안전"으로 오해하게 두지 않는다**(조용한 통과 금지).

## 1.5 파이썬 동등성(parity) — 이 설계의 최우선 요구 🔴

> 형 지시(2026-07-16): **"가장 중요한 건 파이썬과 동일한 성능을 내야 한다."** 다국어 확장의 **합격 기준**이자 최우선 제약.

**"동일 성능"의 조작적 정의 — 4개 축**:
1. **탐지 동등**: 의미상 동등한 위험 변경은 **언어가 달라도 동일 verdict**(pass/approval/blocked). → **교차언어 등가 픽스처**로 강제(아래).
2. **엄밀성 동등**: 각 언어가 **자기 고정 적대 세트**(그 언어의 우회 벡터) + 음성검증 + fail-closed 를 갖는다. Python 이 `getattr` 난독을 D-024~027 로 4단계 폐쇄했듯, Java 는 **리플렉션·문자열 SQL 난독**을 동급 깊이로 막는다.
3. **정직성 동등**: 미탐·미해소는 coverage 노출(조용한 통과 금지). 이미 전 언어 공통.
4. **🔴 안전 방향 동등(가장 중요)**: 정적분석이 불완전할 때 **과탐(approval 남발) 쪽으로 기울고, 과소탐(놓침) 쪽으론 절대 안 기운다.** 놓침 = 위험 통과 = **parity 위반**. 과탐 = 승인 프롬프트 = 허용(승인상한). **불완전성은 항상 안전한 쪽으로 반올림.**

**강제 장치 — 교차언어 등가 픽스처**: 각 위험 클래스(직접 민감함수 수정·신규 위험능력·간접영향·의도이탈)마다 **Python 판 + Java 판을 쌍**으로 만들어 **동일 verdict 를 단언**한다. 하나라도 어긋나면 **parity 회귀 = 스위트 FAIL**. 이게 "동일 성능"의 **자동 증명**(주장이 아니라 실증). 상설 회귀 `tests/parity/` 그룹 신설.

**parity 가 "공짜"인 곳과 "공짜가 아닌" 곳**:
- 🟢 **공짜(직접 달성)**: 경로층·인벤토리·주석·능력 — 구조·이름 기반이라 언어만 바뀌고 정보량 동일. tree-sitter 로 탐지 parity 직행.
- 🔴 **공짜 아님 = L3(간접영향) 하나뿐** → §5 에서 **보수적 과대근사**로 안전 parity 달성. (앞 초안의 "Java 는 더 약함"을 방치하지 않고 회복 메커니즘을 명시.)

## 2. 오늘 이미 언어무관인 것 (코드 0으로 Java/FE 작동)

| 층 | 원리 | 다국어 |
|---|---|---|
| 의도 이탈 (`check-change-intent`) | 파일경로 glob | 🟢 즉시 |
| `expected_paths` 부재 탐지 (TASK-027) | 경로 | 🟢 즉시 |
| 광역선언 격상 (TASK-021) | 경로 | 🟢 즉시 |
| 민감경로 (`check-sensitive-zones`) | 경로 규칙 | 🟢 즉시 (`**/*Controller.java`·`**/security/**` 등만 추가) |
| 정책 자기무력화 (`check-policy-change`) | YAML 구조 diff | 🟢 즉시 |
| maturity shadow (TASK-020) | 정책 필드 | 🟢 즉시 |

→ **Spring repo 온보딩 = 위 6층이 새 코드 없이 바로 작동.** 이 설계가 더하는 것은 **깊은 층(3·4절)** 뿐.

## 3. seam — 공통 IR + 확장자 라우터

### 3.1 공통 IR(중간표현) 4종 계약

각 언어 어댑터는 **아래 스키마로만** 산출한다. 그러면 하류 판정 게이트(`map-diff-to-functions` 교집합·classify·`check-function-gov-level`·`check-new-capabilities`·`check-indirect-impact`)는 **언어를 몰라도** 그대로 재사용된다.

1. **인벤토리**: `{path, lang, functions:[{type, name(정규화), start_line, end_line, signature_start_line(어노테이션/데코레이터 첫 줄), signature(오버로드·시그니처변경 판별), annotations:[...]}]}`
   - 현행 Python `extract-python-inventory` 출력이 이미 이 형태(`lang` 추가·`decorators`→`annotations`·`decorator_start_line`→`signature_start_line` **이름만 중립화·값 동일**). **헝크↔함수 교집합(`touched_functions`)은 순수 라인범위 계산 = 이미 언어무관.**
   - `signature` = classify(added/modified/deleted·시그니처 vs 본문 변경)용 정규화 시그니처. 각 언어 어댑터가 제공, **classify 비교 로직은 언어중립**(오버로드 매칭 = `(name, signature)` 키 — Python `order_key` 계보).
2. **능력신호**: `{path, lang, capabilities:[{id, level, signals:[{kind,name,line}]}], unresolved_dynamic, errors, parse_error, unreadable}`
3. **거버넌스 주석**: `{path, lang, annotations:[{symbol, level, reason, order_key, errors}]}`
4. **콜그래프**: `{path, lang, edges:[{caller,callee}], unresolved_calls:[...]}`  ← 간접영향(Phase X)용

**설계 요점**: IR 은 파서 차이를 흡수하는 계약이다. Python 이 `ast` 를 쓰든 Java 가 tree-sitter 를 쓰든 **판정 엔진 입장에선 동일 IR**. 새 언어 추가 = 이 4종을 채우는 추출기 작성일 뿐, 판정 엔진 무변경.

### 3.2 확장자 라우터 — 파일별 자동 분배

검사기는 "언어 모드"를 통째로 고르지 않는다. **한 PR 에 `.java`·`.py`·`.tsx` 가 섞일 수 있으므로 파일마다** 라우팅한다.

```
바뀐 파일 목록 ─┬─ *.py            → python 어댑터 (ast, 현행 유지)
               ├─ *.java          → java 어댑터   (tree-sitter)
               ├─ *.js/.jsx/.ts/.tsx → js/ts 어댑터 (tree-sitter)
               └─ 그 외(*.go, *.md …) → 심층 어댑터 없음
                                        → 경로층만 판정 + coverage 에 "심층분석 미지원: .go"
        각 어댑터가 공통 IR 산출 → 병합 → 판정 엔진(언어 무관) → 최종 판정 1회
```

- **판정 기준 = 확장자(내용 추측 아님)** — 결정적("추정 금지" 정합).
- **매핑 표는 정책 파일**(`policies/language-routing.yaml` 신설 또는 기존 확장): `.java → java-adapter` 를 YAML 로. 새 언어 = 어댑터 등록 + 확장자 한 줄, **판정 엔진 하드코딩 금지**.
- **미지원 확장자 fail-safe**: 심층 어댑터 없으면 경로층은 그대로 판정하되 **카드 coverage 에 명시**. 조용한 통과 금지(§1 정직성). ← **새 언어 도입이 사각지대가 되지 않게 하는 핵심 가드.**
- **현행 중앙화**: 지금은 각 Python 게이트가 개별로 `.py` 필터링한다. 라우터는 그 분배를 **앞단 하나로 중앙화**해 판정 게이트를 언어중립으로 만든다(작지만 실질적 구조 변화).

### 3.3 파서 배치 — 왜 Python 은 안 바꾸나

| 언어 | 파서 | 근거 |
|---|---|---|
| **Python** | `ast` (**현행 유지**) | 내장·공짜·검증완료. `ast` 는 정규화 이름·`end_lineno`·데코레이터·strongest-wins 승계가 이미 얹혀 있어 tree-sitter(구문트리만)보다 **우리 용도엔 우월**. 바꾸면 다운그레이드 + 회귀 위험. |
| Java | tree-sitter | 파이썬에 자바 파서 없음. tree-sitter-java 문법 로드. |
| JS/TS | tree-sitter | 동일. tree-sitter-javascript/typescript. |

- **의존성 등급 정직**: `ast`/`fnmatch` = 표준 라이브러리(설치 0). `pyyaml` = 유일한 순수-파이썬 외부 의존. tree-sitter = 외부 + 네이티브(C) 한 겹 위 — 다만 prebuilt wheel 로 `pip install` 한 줄, 실부담은 "pyyaml 하나 더" 수준. 다중 런타임(JVM/Node) 네이티브 툴과는 급이 다르다.
- **tree-sitter 한계 = 타입 미해소**. 호출이 정확히 어느 정의로 가는지(타입 추론)는 안 됨 → **이름기반 거친 해소**. 이는 **현행 Python 콜그래프도 동일**하므로 새 손해가 아니다. 정말 필요한 고가치 지점(Java 타입기반 콜그래프)만 후속 네이티브 보강 여지(§7).
- **🔴 결정성·재현성 parity**: tree-sitter 문법 **버전 고정(pin)** + 감사카드에 **언어별 파서/문법 버전 기록**(Python parser 버전 기록 = TASK-019 AC#3 계보). 같은 소스 + 같은 문법버전 → 같은 파스트리(플랫폼 무관 확인). 문법 업그레이드는 정책 변경으로 취급(재현성 계약).

## 4. 언어별 어댑터가 채울 것

### 4.1 Java / Spring — 어노테이션이 우리 개념과 거의 1:1 (금광)

**(a) 인벤토리(J1)**: class/method/constructor 정규화 이름(`Class.method`)·라인범위·어노테이션 목록. → 공통 IR #1. 헝크 매핑·classify 재사용.

**(b) 거버넌스 주석 + Spring 카탈로그(J2)** — `@Gov(level="frozen", reason=...)` 는 **진짜 자바 어노테이션**(컴파일 불필요, 구문만 파싱 — Python `@gov` 보다 자연스러움). 여기에 **Spring 프레임워크 어노테이션 카탈로그**(신규 정책 아티팩트)를 더한다:

| Spring/JDK 어노테이션·API | 판정 | 근거 |
|---|---|---|
| `@PreAuthorize` `@PostAuthorize` `@Secured` `@RolesAllowed` | protected | 인가 경계가 코드에 선언 |
| `@Transactional` | watched (정산 서비스 위면 zone 이 frozen 로 승격) | 자금/DB 트랜잭션 |
| `@GetMapping` `@PostMapping` `@RequestMapping` | watched + 진입점 표시 | 외부 공격면 |
| `@Query(nativeQuery=true)` `@Modifying` | protected (+ sink 후보) | SQL 직접 |
| `@Scheduled` `@EventListener` `@KafkaListener` | watched | 비동기·간접 진입점 |

**(c) 능력 카탈로그(J3)** — 위험 프리미티브:

| Java 능력 | id/판정 | 근거 |
|---|---|---|
| `Runtime.exec` `ProcessBuilder` | command_exec / protected | RCE |
| `ObjectInputStream.readObject` | unsafe_deserialization / protected | 역직렬화 취약 |
| `Class.forName` `Method.invoke` | reflection / watched | 동적 디스패치 |
| `Statement.execute*` (문자열 SQL) | sql_injection_surface / protected | SQLi |
| `Cipher` `MessageDigest` `KeyGenerator` | crypto / protected | 암호 경계 |
| `InitialContext.lookup` (JNDI) | jndi_lookup / protected | log4shell 계열 |
| `RestTemplate` `WebClient` `HttpClient` | outbound_http / watched | 신규 외부호출 |

→ (b)(c) 모두 **기존 판정 게이트 재사용**: (b)→`check-function-gov-level`(effective level → frozen=block/protected=approval/watched=warn), (c)→`check-new-capabilities`(base..head 신규 도입만 approval). **Java 대응 우회 벡터**(리플렉션·문자열 SQL 조립 등)를 고정 적대 세트로(각 태스크 AC).

### 4.2 Frontend (JS/TS) — 후속(W1)

인벤토리(함수선언·화살표함수·클래스메서드·React 컴포넌트) + **XSS/능력 카탈로그**: `dangerouslySetInnerHTML`·`innerHTML=`·`document.write`(XSS sink→protected)·`eval`·`new Function`(동적실행→protected)·`fetch`/`axios`(외부호출→watched)·`localStorage`/`document.cookie`(민감저장→watched)·`process.env`/`child_process`(node→protected). 주석 규약 = JSDoc `/** @gov {level:"frozen"} */` 또는 `// @gov(level=frozen)`.

## 5. parity 가 공짜가 아닌 지점 — L3(간접영향)과 그 회복

앞 절들(경로·인벤토리·주석·능력)은 tree-sitter 로 **탐지 parity 가 직접 달성**된다(구조·이름 기반이라 언어만 바뀔 뿐 정보량 동일). **유일하게 parity 가 공짜가 아닌 곳은 L3 콜그래프**다.

**문제**: Java 관용구(인터페이스 + DI + AOP)는 호출부와 구현을 **의도적으로 분리**한다. 이름기반 정적 콜그래프는 `service.transfer()` 가 어느 구현으로 가는지 모른다(런타임 주입). Python(대부분 직접 호출)보다 **정적으로 놓치는 실제 엣지가 많다** → 그냥 두면 L3 는 Java 에서 **과소탐(놓침) = §1.5 parity 위반.**

**해법 = 보수적 과대근사(안전 parity 달성)**:
- 인터페이스 메서드 호출 → repo 내 **그 인터페이스의 모든 구현체로 엣지**(어느 게 주입될지 모르니 전부 연결·tree-sitter 로 `implements`/`extends` 열거 가능).
- `@Autowired`/생성자 주입 필드 → 그 타입의 **모든 구현**으로 해소.
- `@Transactional`·AOP 프록시 경유 → **직접 엣지로 취급**(프록시 무시).
- 결과: 산출 콜그래프 = 실제 런타임 엣지의 **상위집합(superset)** → **진짜 엣지를 안 놓침 = 안전 방향 parity 달성**(§1.5 축4). 비용 = 승인 프롬프트 증가(과탐) — 2·3층 승인상한이라 감내.

**정밀 parity(옵션·후속)**: 과탐이 실사용에서 과하면, 후속 **네이티브 심볼솔버**(JavaParser/Spoon)로 인터페이스→실제 구현을 타입으로 좁힌다. tree-sitter 만으로 **안전 parity**, 네이티브는 **정밀 parity**. Java 는 정적타입이라 심볼솔버 도입 시 오히려 **Python L3 를 능가**할 수 있음(Python 동적타입은 이 해소가 근본적으로 더 어려움).

**여전한 정직 노출(coverage — 과대근사로도 못 잡는 것)**:
- **완전 동적**: 리플렉션 디스패치(Java)·`eval`/`window[...]`(JS)·`getattr`(Python) — 존재는 watched 로 잡되 대상 값 추정 안 함(전 언어 동일 원칙). → `coverage.unevaluated`.
- **컨테이너 밖 배선**: 설정파일 기반 빈·외부 주입 → 코드에 안 보임. → coverage 노출.
- **TS 타입 미해소**: tree-sitter CST 는 타입 없음 → 타입기반 호출 해소는 네이티브 보강 전까지 불가(프론트 W1 의 정밀 parity 는 후속).

## 6. 단계 로드맵 + 태스크 맵

| 단계 | 내용 | 태스크 |
|---|---|---|
| **J0** | 어댑터 seam: 공통 IR 계약 + 확장자 라우터 + 미지원 coverage + tree-sitter 도입(Java 파싱 전 배관) | **TASK-029** |
| **J1** | Java 함수/메서드 인벤토리 추출기 (tree-sitter → IR) | **TASK-030** |
| **J2** | Java `@Gov` + Spring 어노테이션 카탈로그 → 함수레벨 민감도 | **TASK-031** |
| **J3** | Java 능력 카탈로그 + 신규능력 감지 | **TASK-032** |
| J-bootstrap | bootstrap 스캐너에 Java/Spring 경로·함수 씨딩 확장 | (J0 에 포함 / 후속) |
| **W1** | Frontend 인벤토리 + XSS/능력 카탈로그 | 후속(J 완결 후 AC 정밀화) |
| **X** | 언어별 콜그래프 → 간접영향(Java 우선) | 후속(가장 어려움·마지막) |

**권고 순서**: J0 → J1 → J2 → J3 (각 통과·머지 후 다음 — 기존 배치 규율). 은행 핵심(정산·인증) 로직이 Spring 백엔드라 J 우선이 ROI 최고.

## 7. 명시 비범위 (이번에 안 함)

- **cross-commit 누적**(여러 PR 로 쪼개 우회) — 무상태 단일-diff 모델을 깸(baseline 저장 필요). *구 "MVP-3 후보"였으나 다국어를 MVP-3 로 확정하며 후속 마일스톤으로 재이월.*
- **타입기반 정밀 콜그래프**(Spoon/JavaParser symbol solver·TS 컴파일러) — 네이티브 툴 보강. tree-sitter 백본 위 고가치 지점만 선택 도입.
- **전 언어 동시** — Java 검증 후 프론트, 그다음 콜그래프. 한 번에 안 함.
