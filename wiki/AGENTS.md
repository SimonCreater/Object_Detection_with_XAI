# AGENTS.md — 객체검출 LLM Wiki 운영 규칙

이 위키는 **MCP Wiki Tool**(`../tools/mcp_server.py`)을 통해 LLM 에이전트가 질의·갱신한다.
사람이 직접 파일을 고치기보다, 에이전트가 아래 규칙 하에 MCP 툴을 호출하는 것이 정상 경로다.

## 1. User Query (read) 모드

1. `wiki_search(query)` 또는 `wiki_list()`로 후보 페이지를 찾는다.
2. front-matter `summary`로 적합도를 판단한다.
3. `wiki_get(slug)`로 본문을 읽고, `## 관련 페이지`의 링크를 따라간다.
4. `[[term]]` 위키링크는 페이지 slug(숫자 prefix 무시) 또는 glossary 용어로 해석한다.

## 2. LLM Maintenance (write) 모드

1. 새 지식은 `wiki_create(slug, title, summary, body, ...)`로 페이지를 만든다.
2. 기존 페이지 보강은 `wiki_update` 또는 `wiki_append`를 쓴다. **front-matter `updated` 자동 갱신**.
3. SCHEMA.md의 front-matter 필수 필드를 반드시 채운다.
4. 본문에서 아직 없는 개념은 `[[future-slug]]`로 링크해 확장 후보로 남긴다.

## 3. 절대 하지 마라

- front-matter 없는 페이지 생성 금지.
- "이번 강의/지난번/다음" 같은 시점 의존 표현 금지(절대 표현 사용).
- 한 페이지에 두 개념 혼합 금지(분리).
- 사람 승인 없이 AGENTS.md / SCHEMA.md 편집 금지.
- 근거 없는(존재하지 않는 파일을 가리키는) 링크 생성 금지.

## 4. 에이전트 권한 요약

| 에이전트 | 허용 툴 | 비고 |
|---|---|---|
| **chatbot (read-only)** | wiki_search, wiki_get, wiki_list | 쓰기 금지 |
| **editor (read-write)** | + wiki_create, wiki_update, wiki_append | journal 기록 필수 |

상세 권한·역할은 `../docs/04_agent_spec.md` 참조.
