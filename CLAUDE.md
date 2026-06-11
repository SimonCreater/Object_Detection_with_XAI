# CLAUDE.md — 프로젝트 컨텍스트 (Claude Code 자동 로드)

markdown LLM Wiki + MCP 서버 + 웹 뷰어가 통합된 Wiki Tool. **운영 규칙은 [RULES.md](RULES.md) 를 따른다.**

## 구조 한눈에

| 경로 | 역할 |
|---|---|
| `wiki/` | 위키 본체 (pages/ glossary/ _meta/ + SCHEMA.md, AGENTS.md, llms.txt) |
| `raw/` | 사용자가 넣는 원문 자료(논문/노트) — 위키 페이지의 소스 |
| `tools/` | `wiki_core.py`(로직) · `mcp_server.py`(MCP 6툴) · `app.py`(Flask 뷰어) |
| `.claude/` | Hook(`settings.json`) · Skill(`skills/new-wiki-page/`) · Subagent(`agents/wiki-editor.md`) |
| `docs/` | 도메인 정의 · 의사결정 저널 · PRD · 에이전트 SPEC |

## 자주 쓰는 명령 (Windows, `py` 런처)

```powershell
py -m pip install -r requirements.txt   # 의존성
py tools/app.py                         # 웹 뷰어 → http://127.0.0.1:5000
py tools/mcp_server.py                  # MCP 서버 (stdio)
py tools/wiki_core.py --validate        # 위키 스키마 검증 (Hook이 자동 실행)
py tools/wiki_core.py                   # 통계 + 샘플 검색 (스모크 테스트)
```

## 작업 시 주의

- 위키 페이지를 만들 땐 `/new-wiki-page` Skill 절차를 따른다 (`raw/` 원문 → 페이지 → 검증).
- 페이지 삭제 금지(`status: deprecated`), 저널은 append-only — 자세한 것은 RULES.md.
- 새 페이지의 front-matter 는 `wiki/SCHEMA.md` 가 단일 기준이다.
