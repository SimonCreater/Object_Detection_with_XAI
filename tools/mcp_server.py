"""
mcp_server.py — 객체검출 LLM Wiki 를 위한 MCP(Model Context Protocol) 서버.

이 서버가 곧 "Tool 과 AI Agent 를 잇는 다리"다. LLM 에이전트(Claude/Codex/Gemini 등)는
MCP 프로토콜의 tools/list, tools/call 을 통해 아래 6개 wiki 툴을 표준 방식으로 호출한다.
실제 파일 입출력 로직은 wiki_core 에 위임한다(전송계층 ↔ 도메인로직 분리).

실행:
    py tools/mcp_server.py            # stdio 전송 (Claude Desktop / CLI 가 자식 프로세스로 구동)
    py tools/mcp_server.py --http     # streamable-http 전송 (127.0.0.1:8000/mcp)

노출 툴(읽기 3 + 쓰기 3):
    wiki_search, wiki_get, wiki_list      (read)
    wiki_create, wiki_update, wiki_append (write)

권한 모델: chatbot 에이전트는 read 3종만, editor 에이전트는 6종 전부.
(에이전트별 허용 함수는 docs/04_agent_spec.md 가 규정하며, 클라이언트 측 설정으로 강제한다.)
"""

from __future__ import annotations

import sys
from fastmcp import FastMCP

import wiki_core as core

mcp = FastMCP(
    name="objdet-wiki",
    instructions=(
        "RT-DETR · XAI(GradCAM++/AttnLRP/Visual Precision Search) · 표현 기하 해석 · 반도체 결함검출 도메인의 LLM Wiki 툴. "
        "읽기는 wiki_search→wiki_get 순으로, 쓰기는 wiki_create/update/append 를 쓴다. "
        "쓰기 작업은 자동으로 _meta/journal.md 에 기록된다."
    ),
)


# ----------------------- READ 툴 -----------------------
@mcp.tool()
def wiki_search(query: str, limit: int = 8) -> list[dict]:
    """키워드로 위키를 검색한다. 제목/슬러그/요약/태그/본문에 가중치를 둔 점수순 결과를 반환.

    Args:
        query: 검색어(공백으로 여러 토큰 가능, 예: 'rt-detr xai').
        limit: 최대 결과 수.
    Returns:
        [{slug, title, summary, category, kind, score}] 리스트.
    """
    return core.search(query, limit=limit)


@mcp.tool()
def wiki_get(slug: str) -> dict:
    """slug 로 페이지 전체(front-matter + 본문)를 가져온다. 숫자 prefix·alias·glossary 자동 해석.

    Args:
        slug: 'rt-detr' 또는 '02-rt-detr' 또는 glossary 용어('iou').
    Returns:
        {slug, title, summary, tags, category, status, related, kind, body}.
    """
    return core.get_page(slug)


@mcp.tool()
def wiki_list(category: str = "", kind: str = "") -> list[dict]:
    """모든 페이지/용어의 요약 목록을 반환한다.

    Args:
        category: 'concept'|'model'|'method'|'application' 필터(빈 값=전체).
        kind: 'page'|'glossary' 필터(빈 값=전체).
    """
    return core.list_pages(category=category or None, kind=kind or None)


# ----------------------- WRITE 툴 (editor 전용) -----------------------
@mcp.tool()
def wiki_create(slug: str, title: str, summary: str, body: str,
                category: str = "concept", tags: list[str] | None = None,
                related: list[str] | None = None) -> dict:
    """새 위키 페이지를 생성한다(SCHEMA 필수필드 검증 + created/updated 설정 + 저널 기록).

    Args:
        slug: kebab-case 소문자 슬러그(파일명이 됨).
        title, summary, body: 제목 / 한 문단 요약 / 마크다운 본문.
        category: concept|model|method|application.
        tags, related: 태그 / 관련 슬러그 리스트.
    """
    return core.create_page(slug, title, summary, body,
                            category=category, tags=tags, related=related)


@mcp.tool()
def wiki_update(slug: str, summary: str = "", body: str = "",
                tags: list[str] | None = None, status: str = "",
                related: list[str] | None = None) -> dict:
    """기존 페이지의 지정 필드만 갱신하고 updated 를 자동 갱신한다(빈 문자열/None=변경 안 함)."""
    return core.update_page(
        slug,
        summary=summary or None,
        body=body or None,
        tags=tags,
        status=status or None,
        related=related,
    )


@mcp.tool()
def wiki_append(slug: str, text: str, heading: str = "") -> dict:
    """기존 페이지 본문 끝에 텍스트를 추가한다(heading 지정 시 '## heading' 섹션으로)."""
    return core.append_page(slug, text, heading=heading or None)


# ----------------------- 리소스: 운영 메타 -----------------------
@mcp.resource("wiki://stats")
def wiki_stats() -> dict:
    """위키 전체 통계(페이지 수, 카테고리 분포, WIKI_ROOT)."""
    return core.stats()


if __name__ == "__main__":
    if "--http" in sys.argv:
        # streamable-http: 다른 프로세스(GUI/원격 클라이언트)에서 접속 가능
        mcp.run(transport="http", host="127.0.0.1", port=8000)
    else:
        # 기본 stdio: Claude Desktop / Claude Code 가 자식 프로세스로 구동
        mcp.run()
