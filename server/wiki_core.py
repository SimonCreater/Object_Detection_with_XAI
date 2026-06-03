"""
wiki_core.py — 전송 계층(MCP/HTTP)과 독립적인 LLM Wiki 코어 로직.

front-matter 파싱, 검색, 조회, 생성/수정/추가, 위키링크 해석, 저널 기록을
모두 담당한다. MCP 서버(mcp_server.py)와 Flask GUI(app.py)가 공통으로 import 한다.

설계 원칙
- markdown + YAML front-matter 가 단일 진실 출처(single source of truth).
- 쓰기 작업은 SCHEMA.md 의 필수 필드를 강제하고 `updated` 를 자동 갱신한다.
- 모든 쓰기는 _meta/journal.md 에 append-only 로 기록된다(감사 추적).
"""

from __future__ import annotations

import os
import re
import datetime
from pathlib import Path
from typing import Optional

import frontmatter  # python-frontmatter

# --- 경로 설정 ---------------------------------------------------------------
# 기본 WIKI_ROOT = 이 파일 기준 ../wiki. 환경변수 WIKI_ROOT 로 override 가능.
_DEFAULT_ROOT = Path(__file__).resolve().parent.parent / "wiki"
WIKI_ROOT = Path(os.environ.get("WIKI_ROOT", str(_DEFAULT_ROOT))).resolve()
PAGES_DIR = WIKI_ROOT / "pages"
GLOSSARY_DIR = WIKI_ROOT / "glossary"
JOURNAL_PATH = WIKI_ROOT / "_meta" / "journal.md"

REQUIRED_FIELDS = ["title", "slug", "summary", "category", "status"]
VALID_CATEGORIES = {"concept", "model", "method", "application"}

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")
_NUM_PREFIX_RE = re.compile(r"^\d+-")


# --- 내부 헬퍼 ---------------------------------------------------------------
def _today() -> str:
    return datetime.date.today().isoformat()


def _now_iso() -> str:
    return datetime.datetime.now().isoformat(timespec="seconds")


def _strip_prefix(slug: str) -> str:
    """'02-rt-detr' -> 'rt-detr' (위키링크 해석용)."""
    return _NUM_PREFIX_RE.sub("", slug)


def _iter_files():
    """pages/, glossary/ 의 .md 파일 경로를 순회 (README.md 제외)."""
    for d in (PAGES_DIR, GLOSSARY_DIR):
        if not d.exists():
            continue
        for p in sorted(d.glob("*.md")):
            if p.name.lower() == "readme.md":
                continue
            yield p


def _load(path: Path) -> dict:
    """한 .md 파일을 front-matter + body dict 로 로드."""
    post = frontmatter.load(path, encoding="utf-8")
    meta = dict(post.metadata)
    kind = "glossary" if path.parent.name == "glossary" else "page"
    slug = str(meta.get("slug") or path.stem)
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "summary": meta.get("summary", ""),
        "tags": meta.get("tags", []) or [],
        "category": meta.get("category", kind),
        "status": meta.get("status", ""),
        "aliases": meta.get("aliases", []) or [],
        "related": meta.get("related", []) or [],
        "kind": kind,
        "path": path,
        "meta": meta,
        "body": post.content,
    }


def _all() -> list[dict]:
    return [_load(p) for p in _iter_files()]


def _find_path(slug: str) -> Optional[Path]:
    """slug 로 파일 경로를 찾는다. 숫자 prefix / alias / glossary 까지 해석."""
    target = slug.strip().removesuffix(".md")
    items = _all()
    # 1) 정확한 slug
    for it in items:
        if it["slug"] == target:
            return it["path"]
    # 2) prefix 제거 매칭 (rt-detr -> 02-rt-detr)
    for it in items:
        if _strip_prefix(it["slug"]) == _strip_prefix(target):
            return it["path"]
    # 3) alias 매칭
    for it in items:
        if target in [str(a) for a in it["aliases"]]:
            return it["path"]
    return None


def _score(item: dict, tokens: list[str]) -> int:
    score = 0
    hay = {
        "title": item["title"].lower(),
        "slug": item["slug"].lower(),
        "summary": item["summary"].lower(),
        "tags": " ".join(str(t).lower() for t in item["tags"]),
        "body": item["body"].lower(),
    }
    weights = {"title": 5, "slug": 4, "summary": 3, "tags": 3, "body": 1}
    for tok in tokens:
        for field, text in hay.items():
            if tok in text:
                score += weights[field]
    return score


def _journal(action: str, slug: str, detail: str = "") -> None:
    """append-only 저널 기록 (감사 추적). 쓰기 작업마다 호출."""
    JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not JOURNAL_PATH.exists():
        JOURNAL_PATH.write_text(
            "# Wiki Journal — append-only 변경 기록\n\n"
            "MCP Wiki Tool 의 모든 쓰기 작업이 시간순으로 자동 기록된다.\n\n",
            encoding="utf-8",
        )
    line = f"- `{_now_iso()}` **{action}** `{slug}`"
    if detail:
        line += f" — {detail}"
    with JOURNAL_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# --- 공개 API (MCP 툴 / GUI 가 호출) ----------------------------------------
def list_pages(category: Optional[str] = None, kind: Optional[str] = None) -> list[dict]:
    """모든 페이지/용어의 요약 목록. category, kind('page'|'glossary') 필터 가능."""
    out = []
    for it in _all():
        if category and it["category"] != category:
            continue
        if kind and it["kind"] != kind:
            continue
        out.append({
            "slug": it["slug"],
            "title": it["title"],
            "summary": it["summary"],
            "category": it["category"],
            "tags": it["tags"],
            "kind": it["kind"],
        })
    return out


def search(query: str, limit: int = 8) -> list[dict]:
    """제목/슬러그/요약/태그/본문에 가중치를 둔 키워드 검색. 점수순 상위 limit."""
    tokens = [t for t in re.split(r"\s+", query.strip().lower()) if t]
    if not tokens:
        return []
    scored = []
    for it in _all():
        s = _score(it, tokens)
        if s > 0:
            scored.append((s, it))
    scored.sort(key=lambda x: (-x[0], x[1]["slug"]))
    return [{
        "slug": it["slug"],
        "title": it["title"],
        "summary": it["summary"],
        "category": it["category"],
        "kind": it["kind"],
        "score": s,
    } for s, it in scored[:limit]]


def get_page(slug: str) -> dict:
    """slug 로 한 페이지 전체(front-matter + 본문)를 반환. 없으면 예외."""
    path = _find_path(slug)
    if path is None:
        raise KeyError(f"page not found: {slug}")
    it = _load(path)
    return {
        "slug": it["slug"],
        "title": it["title"],
        "summary": it["summary"],
        "tags": it["tags"],
        "category": it["category"],
        "status": it["status"],
        "related": it["related"],
        "kind": it["kind"],
        "meta": it["meta"],
        "body": it["body"],
    }


def resolve_wikilink(term: str) -> Optional[str]:
    """[[term]] -> 실제 slug. 해석 실패 시 None."""
    path = _find_path(term)
    if path is None:
        return None
    return _load(path)["slug"]


def create_page(slug: str, title: str, summary: str, body: str,
                category: str = "concept", tags: Optional[list[str]] = None,
                related: Optional[list[str]] = None, status: str = "draft") -> dict:
    """새 페이지를 pages/ 에 생성. 필수 필드 검증 + created/updated 설정 + 저널 기록."""
    if not _SLUG_RE.match(slug):
        raise ValueError(f"invalid slug (kebab-case 소문자/숫자/-): {slug}")
    if category not in VALID_CATEGORIES:
        raise ValueError(f"category 는 {VALID_CATEGORIES} 중 하나여야 함: {category}")
    if _find_path(slug) is not None:
        raise FileExistsError(f"이미 존재하는 slug: {slug} (update/append 사용)")

    today = _today()
    post = frontmatter.Post(body.strip() + "\n")
    post.metadata = {
        "title": title,
        "slug": slug,
        "summary": summary,
        "tags": tags or [],
        "category": category,
        "status": status,
        "created": today,
        "updated": today,
        "related": related or [],
    }
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = PAGES_DIR / f"{slug}.md"
    path.write_bytes(frontmatter.dumps(post).encode("utf-8"))
    _journal("create", slug, f'"{title}"')
    return {"slug": slug, "path": str(path), "status": "created"}


def update_page(slug: str, summary: Optional[str] = None, body: Optional[str] = None,
                tags: Optional[list[str]] = None, status: Optional[str] = None,
                related: Optional[list[str]] = None) -> dict:
    """기존 페이지의 필드를 갱신. 지정된 필드만 덮어쓰고 updated 를 자동 갱신."""
    path = _find_path(slug)
    if path is None:
        raise KeyError(f"page not found: {slug}")
    post = frontmatter.load(path, encoding="utf-8")
    changed = []
    if summary is not None:
        post.metadata["summary"] = summary; changed.append("summary")
    if tags is not None:
        post.metadata["tags"] = tags; changed.append("tags")
    if status is not None:
        post.metadata["status"] = status; changed.append("status")
    if related is not None:
        post.metadata["related"] = related; changed.append("related")
    if body is not None:
        post.content = body.strip() + "\n"; changed.append("body")
    post.metadata["updated"] = _today()
    path.write_bytes(frontmatter.dumps(post).encode("utf-8"))
    _journal("update", slug, "fields=" + ",".join(changed) if changed else "no-op")
    return {"slug": slug, "updated": post.metadata["updated"], "changed": changed}


def append_page(slug: str, text: str, heading: Optional[str] = None) -> dict:
    """기존 페이지 본문 끝에 텍스트(선택적으로 ## heading 포함)를 추가."""
    path = _find_path(slug)
    if path is None:
        raise KeyError(f"page not found: {slug}")
    post = frontmatter.load(path, encoding="utf-8")
    block = ("\n\n## " + heading + "\n\n" + text.strip() + "\n") if heading \
        else ("\n\n" + text.strip() + "\n")
    post.content = post.content.rstrip() + block
    post.metadata["updated"] = _today()
    path.write_bytes(frontmatter.dumps(post).encode("utf-8"))
    _journal("append", slug, f'+{len(text)} chars' + (f' under "{heading}"' if heading else ""))
    return {"slug": slug, "updated": post.metadata["updated"]}


def stats() -> dict:
    """위키 전체 통계 (대시보드/검증용)."""
    items = _all()
    pages = [i for i in items if i["kind"] == "page"]
    glossary = [i for i in items if i["kind"] == "glossary"]
    by_cat: dict[str, int] = {}
    for p in pages:
        by_cat[p["category"]] = by_cat.get(p["category"], 0) + 1
    return {
        "wiki_root": str(WIKI_ROOT),
        "pages": len(pages),
        "glossary": len(glossary),
        "by_category": by_cat,
    }


if __name__ == "__main__":
    import json
    print("WIKI_ROOT =", WIKI_ROOT)
    print(json.dumps(stats(), ensure_ascii=False, indent=2))
    print("--- search('rt-detr xai') ---")
    for r in search("rt-detr xai"):
        print(f"  [{r['score']}] {r['slug']}  {r['title']}")
