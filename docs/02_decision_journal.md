# 의사결정 저널 — Wiki Tool 구현 라운드 기록

> 제출물 ②: Wiki Tool 을 구현하며 **에이전트와 진행한 의사결정 라운드**를 기록한 문서.
> 직전 과제(Agentic Coding Wiki)의 **Journal 패턴**(Harness Engineering 의 append-only `journal.md`,
> `LLM_Wiki/pages/07-harness-and-skills.md`)을 본 프로젝트에 적용한 결과물이다.

## 저널 패턴 적용 방식 (왜 이렇게 기록하는가)

직전 과제에서 정리한 Harness 4책임 중 **Journal = "무엇을, 왜 했는지의 append-only 기록"** 을 차용한다.
- 이 문서(`02_decision_journal.md`)는 **사람-에이전트 간 설계 결정**의 저널(사람이 읽는 의사결정 근거).
- 런타임의 **기계적 변경 로그**는 별도로 `wiki/_meta/journal.md` 에 MCP 쓰기 툴이 자동 append.
- 둘을 분리해, "왜 그렇게 설계했나"(여기)와 "무엇이 실제로 바뀌었나"(런타임 저널)를 모두 추적한다.

각 라운드는 **결정 / 근거 / 대안 / 폐기 이유** 로 적는다(Planner ↔ Reviewer ping-pong, 직전 과제 `05-agent-specifications.md` 의 루프).

---

## Round 1 — 지식 도메인 선택

- **결정**: CSE-3308 대신 *Object Detection(RT-DETR·XAI·반도체 결함검출)* 을 도메인으로 채택.
- **근거**: 강의 주제 자체를 위키화하면 평가가 엄격해질 수 있다는 우려 + 연구자가 실제 다루는 살아있는 지식이라 갱신 수요가 실재.
- **대안**: (a) CSE-3308 그대로, (b) 일반 CV 전반.
- **폐기 이유**: (a) 평가 리스크, (b) 범위가 넓어 단일 출처의 응집도 저하.

## Round 2 — 콘텐츠 vs 인프라, 무엇을 먼저?

- **결정**: 위키 **콘텐츠(8 페이지)** 를 먼저 작성하고 그 위에 도구를 얹는다.
- **근거**: MCP 툴·GUI·챗봇 모두 "읽을 데이터"가 있어야 검증 가능. 빈 위키로는 검색/렌더/Q&A 시연 불가.
- **대안**: 도구 골격 먼저(목 데이터).
- **폐기 이유**: 목 데이터는 front-matter 스키마·위키링크 해석 같은 실제 난점을 못 드러냄.

## Round 3 — 전송계층과 도메인로직 분리

- **결정**: `wiki_core.py`(순수 로직) ↔ `mcp_server.py`(MCP) ↔ `app.py`(Flask GUI) 3분할.
- **근거**: 직전 과제 `08-model-context-protocol.md` 의 교훈 — Tool 로직은 전송(MCP/HTTP)과 독립이어야 재사용·테스트가 쉽다. GUI 와 에이전트가 **같은 코어**를 쓰면 데이터 정합성이 보장됨(single source of truth).
- **대안**: MCP 서버 안에 파일 I/O 직접 구현.
- **폐기 이유**: GUI 가 MCP 를 거쳐야만 데이터를 읽게 되어 결합도↑, 테스트 난이도↑.

## Round 4 — MCP 툴 표면(surface) 설계

- **결정**: 읽기 3(`wiki_search/get/list`) + 쓰기 3(`wiki_create/update/append`) = 6개.
- **근거**: 직전 과제의 AgentMEMO 툴셋(create/get/list/update/append)을 위키 도메인에 맞게 이식. CRUD 중 **삭제는 의도적으로 제외**(지식 손실·권한 위험 방지; 비활성화는 `status` 로 표현).
- **대안**: 범용 `read_file/write_file` 노출.
- **폐기 이유**: 범용 파일 툴은 스키마 검증·저널 기록을 우회 → 위키 무결성 붕괴 위험. 도메인 특화 툴이 가드레일을 강제.

## Round 5 — 에이전트 권한 분리 (read vs write)

- **결정**: **chatbot=read-only(3툴)**, **editor=read-write(6툴)** 로 권한 분리(SPEC: `04_agent_spec.md`).
- **근거**: 최소권한 원칙. 사용자 질의응답이 실수로 위키를 변형하면 안 됨. 직전 과제 `09-loop-and-hooks.md` 의 "확률적 출력에 결정론적 게이트" 원칙을 권한으로 구현.
- **대안**: 단일 만능 에이전트.
- **폐기 이유**: 쓰기 사고 위험 + 감사 추적 모호.

## Round 6 — 쓰기 작업의 무결성 가드

- **결정**: 모든 쓰기에 (a) SCHEMA 필수필드 검증, (b) `updated` 자동 갱신, (c) `_meta/journal.md` append 를 강제.
- **근거**: front-matter 누락·시점의존표현 같은 안티패턴(직전 과제 PIPELINE 9절)을 코드로 차단. 저널은 확률적 에이전트의 변경을 결정론적으로 추적.
- **대안**: 규칙을 문서로만 권고.
- **폐기 이유**: LLM 은 확률적 앵무새 — 문서 권고는 지켜지지 않을 수 있어 코드 게이트 필요.

## Round 7 — MVP 시각화/챗봇 방식

- **결정**: Flask 단일 앱(사이드바+본문 렌더+검색+retrieval 챗봇). 챗봇은 LLM 키 없이도 `wiki_core.search`→`get` 으로 결정론적 응답, 추후 LLM 백엔드 연결 가능.
- **근거**: 평가 시점에 API 키/네트워크 의존 없이 재현 가능해야 함. retrieval 만으로도 "에이전트가 MCP 툴을 써서 답한다"는 구조를 시연.
- **대안**: 외부 LLM API 직접 호출.
- **폐기 이유**: 키·비용·재현성 문제. (README 에 LLM 연결 지점 명시.)

## Round 8 — 스크린샷(MVP) 재현성

- **결정**: 챗봇 Q&A 가 채워진 상태를 서버사이드 렌더하는 `/demo/<slug>` 라우트를 추가하고, headless Chrome 으로 PNG·PDF 캡처.
- **근거**: 비동기 fetch 결과를 기다리지 않아도 정적 캡처로 완전한 화면을 얻어 재현성 확보.
- **대안**: 수동 브라우저 캡처.
- **폐기 이유**: 수동은 재현·자동화 불가.

## Round 9 — 콘텐츠를 실제 논문 기반으로 재정초(re-grounding)

- **결정**: 초기 8 페이지는 일반 지식으로 작성됐음을 확인 → `WikiTool_MCP/` 루트의 **실제 논문 7편**을 정독해 콘텐츠를 재작성·확장. 최종 **11 페이지**.
  - 정정/재작성: `02-rt-detr`(CCFM→CCFF, IoU-aware→Uncertainty-minimal Query Selection, 실제 벤치마크·하이퍼파라미터), `05-gradcam-plus-plus`(Eq.11/19·실측치), `06-lrp`(일반 LRP→**AttnLRP** 기반).
  - 신규: `09-faster-rcnn-two-stage`(Faster R-CNN), `07-visual-precision-search`(검출 블랙박스 XAI), `10-manifold-geometry-interpretability`(When Models Manipulate Manifolds), `11-pruning-robustness-geometry`(Understanding Robustness Lottery).
- **근거**: 위키의 가치는 **출처 추적 가능한 정확성**. 보유 논문 집합에 TCAV 논문이 없음을 확인 → 근거 없는 `07-tcav` 삭제, 실제 논문 기반 `07-visual-precision-search` 로 대체. 모든 정정에 "정정 메모"와 인용을 남김.
- **대안**: 일반 지식 콘텐츠 유지 + 인용만 보강.
- **폐기 이유**: 근거 없는 수치/주장(예: TCAV 페이지)은 위키 신뢰도를 훼손. append-only 저널 원칙상 본 라운드로 변경 이력을 명시.

---

## 결과 요약

| 라운드 | 산출물 |
|---|---|
| 1~2 | `wiki/` 페이지(초기 8 → R9에서 11) + 용어 3 + 메타 |
| 3~4 | `server/wiki_core.py`, `server/mcp_server.py` (6 MCP 툴) |
| 5~6 | `docs/04_agent_spec.md` 권한 모델, `_meta/journal.md` 자동 저널 |
| 7~8 | `server/app.py` GUI, `mvp/` 스크린샷·PDF |
| 9 | 실제 논문 7편 정독 → 콘텐츠 재정초(11 페이지), TCAV→VPS 대체 |

> 본 저널은 append-only 원칙에 따라, 이후 설계 변경 시 **위에 라운드를 추가**한다(기존 항목 수정 금지).
