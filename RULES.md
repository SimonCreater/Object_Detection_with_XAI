# RULES.md — Agent 운영지침 (Harness)

이 저장소에서 작업하는 **모든 AI 에이전트**(Claude Code, MCP 클라이언트, 서브에이전트)가 따라야 하는 규칙.
사람 기여자에게도 동일하게 권장된다.

## 1. 위키 수정의 단일 경로

- 위키 콘텐츠(`wiki/pages/`, `wiki/glossary/`)는 **6개 도메인 툴**로만 수정한다:
  읽기 `wiki_search / wiki_get / wiki_list` · 쓰기 `wiki_create / wiki_update / wiki_append`.
- MCP 미연결 환경(예: 일반 Claude Code 세션)에서는 `wiki/SCHEMA.md` 형식을 그대로 지켜 파일을 작성하고,
  작성 직후 반드시 검증 게이트를 통과시킨다(아래 3절).
- **삭제 금지.** 페이지를 없애는 대신 front-matter `status: deprecated` 로 표시한다.

## 2. 스키마·출처 의무

- 모든 페이지는 `wiki/SCHEMA.md` 의 필수 front-matter(title/slug/summary/category/status)를 갖춘다.
- **출처 없는 수치·주장 금지.** 본문 끝 `## 참고 / 출처` 에 서지정보(arXiv/DOI/URL)를 남긴다.
  원문이 `raw/` 에 있으면 `source.ref` 로 파일명을 가리킨다.
- 기존 페이지의 사실을 정정할 때는 본문에 *정정 메모*를 남기고 출처를 함께 적는다.

## 3. 검증 게이트 (결정론적 Hook)

- 위키 파일을 쓰거나 고친 뒤에는 다음이 **exit 0** 이어야 한다:
  ```powershell
  py tools/wiki_core.py --validate
  ```
- 이 게이트는 `.claude/settings.json` 의 **PostToolUse Hook** 으로 자동 실행된다 —
  에이전트가 Write/Edit 로 위키를 건드리면 즉시 스키마 검증이 돈다(확률적 출력에 결정론적 게이트).

## 4. 저널 (append-only)

- MCP 쓰기 툴은 `wiki/_meta/journal.md` 에 자동 기록을 남긴다. **저널을 편집하거나 지우지 않는다.**
- 설계 차원의 의사결정은 `docs/02_decision_journal.md` 에 **라운드를 추가**한다(기존 라운드 수정 금지).

## 5. 자료 투입 → 통합 절차

1. 사용자가 원문(논문 PDF, 노트, URL 메모 등)을 `raw/` 에 넣는다.
2. 에이전트는 `/new-wiki-page` Skill(`.claude/skills/new-wiki-page/`) 절차를 따른다:
   원문 정독 → 기존 페이지 중복 검색 → 페이지 생성 → 검증 → 보고.
3. 큰 통합 작업은 `wiki-editor` 서브에이전트(`.claude/agents/wiki-editor.md`)에 위임할 수 있다.

## 6. 금지 사항

- 코드/문서에 **API Key·비밀값을 넣지 않는다.** LLM 연동은 subprocess/MCP 클라이언트 경유로만.
- `wiki/_meta/journal.md`, `docs/02_decision_journal.md` 의 기존 기록 수정 금지.
- `raw/` 의 원문 파일을 수정·삭제하지 않는다(읽기 전용 취급).
- 위키 본문에 시점 의존 표현("최근", "현재")을 쓰지 않는다 — 날짜나 버전으로 고정.
