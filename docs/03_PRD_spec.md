# PRD / 사양서 — MCP 기반 Wiki Tool

> 제출물 ③: 프로젝트 Goal 달성을 위해 작성한 **PRD(제품 요구사항 정의서) / 사양 문서**.

## 1. 배경 & 문제 (Background)

객체검출 모델(RT-DETR 등)·XAI 해석 기법 지식은 빠르게 늘고, 모델·기법·응용이 얽혀 있다.
파편화된 메모로는 (a) 재검색, (b) 갱신, (c) LLM 에이전트의 자동 활용이 어렵다.

## 2. Goal & Non-Goal

- **Goal**: markdown 기반 LLM Wiki 를 **MCP 서버로 노출**해, AI 에이전트가 표준 프로토콜로
  질의(read)·갱신(write)하고, 사람은 GUI 로 시각화·검색·질의할 수 있게 한다.
- **Non-Goal**: 모델 학습/추론 파이프라인, 데이터셋 호스팅, 멀티 사용자 인증·동시편집 락.

## 3. 사용자 스토리 (User Stories)

- US-1: 연구자로서, 키워드로 위키를 검색해 가장 관련 있는 페이지를 즉시 찾고 싶다.
- US-2: 협업자로서, 자연어로 질문하면 위키 근거와 출처 링크가 달린 답을 받고 싶다.
- US-3: 에이전트로서, 새 결함 클래스/기법을 스키마에 맞는 페이지로 자동 추가하고 싶다.
- US-4: 관리자로서, 누가/언제/무엇을 바꿨는지 감사 추적을 보고 싶다.

## 4. 기능 요구사항 (Functional Requirements)

| ID | 요구사항 | 충족 수단 |
|---|---|---|
| FR-1 | 키워드 가중치 검색 | `wiki_search` (제목5/슬러그4/요약3/태그3/본문1) |
| FR-2 | 페이지 전체 조회(숫자prefix/alias/glossary 해석) | `wiki_get`, `resolve_wikilink` |
| FR-3 | 목록/카테고리 필터 | `wiki_list(category, kind)` |
| FR-4 | 스키마 검증 페이지 생성 | `wiki_create` (필수필드·slug 규칙·중복 검사) |
| FR-5 | 필드 부분 갱신 + updated 자동 | `wiki_update` |
| FR-6 | 본문 말미 추가 | `wiki_append` |
| FR-7 | 모든 쓰기 감사 로깅 | `_meta/journal.md` 자동 append |
| FR-8 | 웹 시각화(사이드바·렌더·위키링크) | `app.py` `/`, `/page/<slug>` |
| FR-9 | 자연어 질의(retrieval 챗봇) | `app.py` `/api/chat` → `search`+`get` |

## 5. 비기능 요구사항 (Non-Functional)

- **NFR-1 재현성**: 외부 API 키 없이 `pip install` 후 즉시 구동(로컬, 127.0.0.1).
- **NFR-2 정합성**: GUI 와 MCP 가 동일 `wiki_core` 공유 → 단일 진실 출처.
- **NFR-3 무결성**: 쓰기는 스키마 게이트를 통과해야만 파일에 반영.
- **NFR-4 최소권한**: chatbot 은 read 3툴, editor 만 write 포함 6툴.
- **NFR-5 이식성**: Windows/PowerShell 환경에서 `py` 런처로 동작 검증.

## 6. 아키텍처 (Architecture)

```
                 ┌───────────────────────────┐
 AI Agent ──MCP──▶  mcp_server.py (FastMCP)   │
 (Claude/Codex)  │   tools: wiki_search/get/  │
                 │   list/create/update/append│
                 └─────────────┬──────────────┘
 사람 ──HTTP──▶ app.py (Flask) │   (둘 다 import)
   브라우저      뷰어·검색·챗봇  ▼
                 ┌───────────────────────────┐
                 │      wiki_core.py          │  ← 전송계층 독립 도메인 로직
                 │  front-matter 파싱/검색/CRUD │
                 └─────────────┬──────────────┘
                               ▼
                 wiki/ (markdown + YAML front-matter)
                 pages/*.md · glossary/*.md · _meta/{source_index,journal}.md
```

## 7. 데이터 모델 (front-matter)

`wiki/SCHEMA.md` 규정. 필수: `title, slug, summary, category, status`(+ `created/updated/tags/related`).
`slug == 파일명`(invariant). `category ∈ {concept, model, method, application}`.

## 8. MCP 인터페이스 사양 (요약)

| 툴 | 입력 | 출력 | 권한 |
|---|---|---|---|
| `wiki_search` | query, limit | [{slug,title,summary,category,kind,score}] | read |
| `wiki_get` | slug | {…, body} | read |
| `wiki_list` | category, kind | [{slug,title,summary,…}] | read |
| `wiki_create` | slug,title,summary,body,category,tags,related | {slug,path,status} | write |
| `wiki_update` | slug,(summary/body/tags/status/related) | {slug,updated,changed} | write |
| `wiki_append` | slug,text,heading | {slug,updated} | write |

리소스: `wiki://stats` → 페이지 통계.

## 9. 수용 기준 (Acceptance Criteria)

- [x] `mcp_server.py` 가 6개 툴을 `tools/list` 에 노출(검증: in-process `list_tools` = 6).
- [x] `wiki_search('rt-detr xai')` 가 `02-rt-detr`·`04-xai-...` 를 상위로 반환.
- [x] GUI `/page/<slug>` 200 응답 + 위키링크가 내부 링크로 렌더.
- [x] `/api/chat` 가 답변 + 출처 페이지 리스트 반환.
- [x] MVP 화면 PNG/PDF 캡처 존재(`mvp/`).
- [x] 쓰기 시 `_meta/journal.md` 에 한 줄 기록(코드 경로 검증).

## 10. 마일스톤

1. 콘텐츠(8p) → 2. core → 3. MCP 서버 → 4. GUI/챗봇 → 5. 문서·SPEC → 6. MVP 캡처. (전부 완료)
