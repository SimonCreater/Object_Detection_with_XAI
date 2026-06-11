"""
app.py — 객체검출 LLM Wiki 의 MVP 웹 GUI (Flask).

목적
- 위키 페이지를 사람이 보기 좋게 시각화(사이드바 + 본문 렌더 + 검색).
- 'Wiki Chatbot' 패널: 동일한 wiki_core 툴(MCP 서버가 노출하는 것과 같은 함수)을
  retrieval 방식으로 호출해 질문에 답하고 출처 페이지를 링크한다.
  (LLM API 키가 없어도 결정론적으로 동작 — README 의 'LLM 백엔드 연결' 절 참고.)

이 GUI 는 MCP 서버와 같은 wiki_core 를 공유하므로, 에이전트가 MCP 로 보는 데이터와
사람이 GUI 로 보는 데이터가 항상 일치한다(single source of truth).

실행:  py tools/app.py    →  http://127.0.0.1:5000
"""

from __future__ import annotations

import re
import markdown
from flask import Flask, request, jsonify, render_template_string, abort

import wiki_core as core

app = Flask(__name__)

CATEGORY_LABEL = {
    "concept": "개념 (Concept)",
    "model": "모델 (Model)",
    "method": "방법 (Method · XAI)",
    "application": "응용 (Application)",
}
CATEGORY_ORDER = ["concept", "model", "method", "application"]

_MD_EXT = ["tables", "fenced_code", "toc", "sane_lists"]


# --- 마크다운 → HTML (위키링크/상대링크 해석) -------------------------------
def _rewrite_links(body: str) -> str:
    # [[term]] -> 내부 링크
    def wl(m):
        term = m.group(1).strip()
        slug = core.resolve_wikilink(term)
        if slug:
            return f"[{term}](/page/{slug})"
        return f"<span class='deadlink' title='아직 없는 페이지'>{term}</span>"
    body = re.sub(r"\[\[([^\]]+)\]\]", wl, body)

    # [text](xxx.md) / [text](glossary/xxx.md) -> /page/<slug>
    def rel(m):
        text, target = m.group(1), m.group(2)
        stem = target.split("/")[-1].removesuffix(".md")
        slug = core.resolve_wikilink(stem)
        if slug:
            return f"[{text}](/page/{slug})"
        return f"{text}"  # 외부/없는 링크는 텍스트로
    body = re.sub(r"\[([^\]]+)\]\(([^)]+\.md)\)", rel, body)
    return body


def md_to_html(body: str) -> str:
    return markdown.markdown(_rewrite_links(body), extensions=_MD_EXT)


# --- 사이드바 데이터 ---------------------------------------------------------
def sidebar_groups():
    pages = core.list_pages(kind="page")
    groups = []
    for cat in CATEGORY_ORDER:
        items = sorted([p for p in pages if p["category"] == cat], key=lambda x: x["slug"])
        if items:
            groups.append((CATEGORY_LABEL.get(cat, cat), items))
    glossary = sorted(core.list_pages(kind="glossary"), key=lambda x: x["slug"])
    return groups, glossary


# --- 챗봇(retrieval) ---------------------------------------------------------
def _section(body: str, name: str) -> str:
    """본문에서 '## name' 섹션 텍스트만 추출."""
    m = re.search(rf"##\s*{re.escape(name)}\s*\n(.+?)(?=\n##\s|\Z)", body, re.S)
    return m.group(1).strip() if m else ""


def chat_answer(message: str) -> dict:
    """wiki_core.search 로 관련 페이지를 찾아 '핵심' 섹션을 모아 답을 구성한다(read-only)."""
    hits = core.search(message, limit=3)
    if not hits:
        return {"answer": "관련 위키 페이지를 찾지 못했습니다. 검색어를 바꿔보세요.", "sources": []}
    parts = []
    sources = []
    for h in hits:
        page = core.get_page(h["slug"])
        core_txt = _section(page["body"], "핵심") or page["summary"]
        # 첫 두 문장 정도로 축약
        snippet = re.sub(r"\s+", " ", core_txt).strip()
        if len(snippet) > 320:
            snippet = snippet[:320].rsplit(" ", 1)[0] + " …"
        parts.append(f"**{page['title']}** — {snippet}")
        sources.append({"slug": h["slug"], "title": page["title"]})
    answer = (
        f"질문 *“{message}”* 와 관련해 위키에서 {len(hits)}개 페이지를 찾았습니다:\n\n"
        + "\n\n".join(parts)
        + "\n\n자세한 내용은 아래 출처 페이지를 참고하세요."
    )
    return {"answer": answer, "sources": sources}


# --- 템플릿 ------------------------------------------------------------------
PAGE_HTML = """
<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Object Detection LLM Wiki</title>
<style>
  :root{--bg:#0f1116;--panel:#171a21;--panel2:#1d212b;--bd:#2a2f3a;--fg:#e6e9ef;--mut:#9aa3b2;--acc:#5b9dff;--acc2:#7ee787;}
  *{box-sizing:border-box} body{margin:0;font-family:'Segoe UI',Pretendard,system-ui,sans-serif;background:var(--bg);color:var(--fg)}
  header{display:flex;align-items:center;gap:12px;padding:12px 20px;background:var(--panel);border-bottom:1px solid var(--bd);position:sticky;top:0;z-index:10}
  header .logo{font-weight:700;font-size:16px} header .tag{color:var(--mut);font-size:12px}
  header .mcp{margin-left:auto;font-size:11px;color:var(--acc2);border:1px solid var(--bd);padding:4px 8px;border-radius:6px}
  .layout{display:grid;grid-template-columns:280px 1fr 360px;height:calc(100vh - 53px)}
  aside{background:var(--panel);border-right:1px solid var(--bd);overflow:auto;padding:14px}
  aside h3{font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--mut);margin:18px 0 6px}
  aside a{display:block;color:var(--fg);text-decoration:none;font-size:13px;padding:6px 8px;border-radius:6px;line-height:1.3}
  aside a:hover{background:var(--panel2)} aside a.active{background:#26324a;color:#fff}
  aside a small{display:block;color:var(--mut);font-size:11px;margin-top:2px}
  .search{width:100%;padding:8px 10px;background:var(--panel2);border:1px solid var(--bd);border-radius:8px;color:var(--fg);font-size:13px}
  main{overflow:auto;padding:28px 40px}
  main .crumb{color:var(--mut);font-size:12px;margin-bottom:6px}
  main .summary{background:var(--panel2);border-left:3px solid var(--acc);padding:10px 14px;border-radius:6px;color:#cdd6e4;margin:14px 0}
  .meta-chips span{display:inline-block;background:var(--panel2);border:1px solid var(--bd);border-radius:20px;padding:2px 10px;font-size:11px;color:var(--mut);margin:0 6px 6px 0}
  article{line-height:1.7;font-size:14.5px;max-width:820px}
  article h1{font-size:24px} article h2{font-size:18px;margin-top:28px;border-bottom:1px solid var(--bd);padding-bottom:6px}
  article h3{font-size:15px;color:var(--acc2)}
  article a{color:var(--acc);text-decoration:none} article a:hover{text-decoration:underline}
  article code{background:#0b0d12;border:1px solid var(--bd);padding:1px 5px;border-radius:4px;font-size:12.5px}
  article pre{background:#0b0d12;border:1px solid var(--bd);border-radius:8px;padding:14px;overflow:auto}
  article pre code{border:0;background:none}
  article table{border-collapse:collapse;margin:12px 0;width:100%} article th,article td{border:1px solid var(--bd);padding:7px 10px;font-size:13px;text-align:left}
  article th{background:var(--panel2)} .deadlink{color:#e3a008;border-bottom:1px dashed #e3a008}
  .chat{background:var(--panel);border-left:1px solid var(--bd);display:flex;flex-direction:column}
  .chat .hd{padding:12px 16px;border-bottom:1px solid var(--bd);font-weight:600;font-size:14px}
  .chat .hd small{display:block;color:var(--mut);font-weight:400;font-size:11px;margin-top:2px}
  .chat .log{flex:1;overflow:auto;padding:14px;display:flex;flex-direction:column;gap:12px}
  .msg{padding:10px 12px;border-radius:10px;font-size:13px;line-height:1.55;white-space:pre-wrap}
  .msg.u{background:#26324a;align-self:flex-end;max-width:90%} .msg.a{background:var(--panel2);border:1px solid var(--bd)}
  .msg.a .src{margin-top:8px;display:flex;flex-wrap:wrap;gap:6px}
  .msg.a .src a{font-size:11px;background:#0b0d12;border:1px solid var(--bd);color:var(--acc);padding:3px 8px;border-radius:14px;text-decoration:none}
  .chat .in{display:flex;gap:8px;padding:12px;border-top:1px solid var(--bd)}
  .chat .in input{flex:1;padding:9px 11px;background:var(--panel2);border:1px solid var(--bd);border-radius:8px;color:var(--fg)}
  .chat .in button{background:var(--acc);border:0;color:#04122e;font-weight:600;padding:0 16px;border-radius:8px;cursor:pointer}
  .tools{font-size:11px;color:var(--mut);padding:8px 14px;border-top:1px solid var(--bd)}
  .tools code{color:var(--acc2)}
</style></head><body>
<header>
  <span class="logo">🔎 Object Detection LLM Wiki</span>
  <span class="tag">RT-DETR · XAI(GradCAM++/AttnLRP/VPS) · 표현 기하 · 반도체 결함검출</span>
  <span class="mcp">● MCP tools: wiki_search · wiki_get · wiki_list · wiki_create · wiki_update · wiki_append</span>
</header>
<div class="layout">
  <aside>
    <form action="/" method="get"><input class="search" name="q" placeholder="검색… (예: nms-free, lrp)" value="{{q or ''}}"></form>
    {% if results %}
      <h3>검색 결과</h3>
      {% for r in results %}<a href="/page/{{r.slug}}">{{r.title}}<small>{{r.category}} · score {{r.score}}</small></a>{% endfor %}
    {% endif %}
    {% for label, items in groups %}
      <h3>{{label}}</h3>
      {% for it in items %}<a class="{{'active' if it.slug==current else ''}}" href="/page/{{it.slug}}">{{it.title}}<small>{{it.summary[:46]}}…</small></a>{% endfor %}
    {% endfor %}
    <h3>Glossary</h3>
    {% for it in glossary %}<a class="{{'active' if it.slug==current else ''}}" href="/page/{{it.slug}}">{{it.title}}</a>{% endfor %}
  </aside>

  <main>
    {% if page %}
      <div class="crumb">{{page.category}} / {{page.slug}}</div>
      <div class="meta-chips">
        <span>status: {{page.status}}</span>
        {% for t in page.tags %}<span>#{{t}}</span>{% endfor %}
      </div>
      <div class="summary">{{page.summary}}</div>
      <article>{{ body_html | safe }}</article>
    {% else %}
      <article>
        <h1>Object Detection LLM Wiki</h1>
        <div class="summary">RT-DETR(CNN-Transformer 하이브리드 검출기)과 XAI(GradCAM++/AttnLRP/Visual Precision Search)·표현 기하 해석을
        반도체 이미지 결함 검출에 적용하는 지식 베이스. 왼쪽에서 페이지를 고르거나, 오른쪽 챗봇에게 질문하세요.</div>
        <p>이 GUI 와 MCP 서버는 같은 <code>wiki_core</code> 를 공유합니다 —
        에이전트가 MCP 툴로 읽고 쓰는 내용이 곧 이 화면의 내용입니다.</p>
        <h2>수록 페이지 {{stats.pages}}개 · 용어 {{stats.glossary}}개</h2>
        <ul>{% for label,items in groups %}<li><b>{{label}}</b>: {{items|length}}개</li>{% endfor %}</ul>
      </article>
    {% endif %}
  </main>

  <section class="chat">
    <div class="hd">💬 Wiki Chatbot <small>read-only 에이전트 · wiki_search → wiki_get 사용</small></div>
    <div class="log" id="log">
      <div class="msg a">안녕하세요! RT-DETR·XAI·반도체 결함검출에 대해 물어보세요.
예) "RT-DETR이 왜 NMS가 필요 없어?", "반도체 결함 검출에 어떤 XAI를 써?"</div>
      {% if seed_q %}
      <div class="msg u">{{seed_q}}</div>
      <div class="msg a">{{ seed_a_html | safe }}
        <div class="src">{% for s in seed_src %}<a href="/page/{{s.slug}}">📄 {{s.title}}</a>{% endfor %}</div>
      </div>
      {% endif %}
    </div>
    <div class="in">
      <input id="q" placeholder="질문 입력…" onkeydown="if(event.key==='Enter')send()">
      <button onclick="send()">전송</button>
    </div>
    <div class="tools">호출 툴: <code>wiki_search(query)</code> → <code>wiki_get(slug)</code> (쓰기 툴은 editor 에이전트 전용)</div>
  </section>
</div>
<script>
const log=document.getElementById('log'), q=document.getElementById('q');
function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function md(s){return esc(s).replace(/\\*\\*(.+?)\\*\\*/g,'<b>$1</b>').replace(/\\*(.+?)\\*/g,'<i>$1</i>').replace(/\\n/g,'<br>')}
function add(cls,html){const d=document.createElement('div');d.className='msg '+cls;d.innerHTML=html;log.appendChild(d);log.scrollTop=log.scrollHeight;return d}
async function send(){
  const m=q.value.trim(); if(!m)return; q.value='';
  add('u',esc(m)); const t=add('a','검색 중…');
  try{
    const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});
    const j=await r.json();
    let src=''; if(j.sources&&j.sources.length){src='<div class="src">'+j.sources.map(s=>`<a href="/page/${s.slug}">📄 ${esc(s.title)}</a>`).join('')+'</div>'}
    t.innerHTML=md(j.answer)+src;
  }catch(e){t.innerHTML='오류: '+esc(String(e))}
  log.scrollTop=log.scrollHeight;
}
</script></body></html>
"""


# --- 라우트 ------------------------------------------------------------------
@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    groups, glossary = sidebar_groups()
    results = core.search(q) if q else None
    return render_template_string(PAGE_HTML, page=None, body_html="", q=q,
                                  results=results, groups=groups, glossary=glossary,
                                  current=None, stats=core.stats())


@app.route("/page/<slug>")
def page(slug):
    try:
        p = core.get_page(slug)
    except KeyError:
        abort(404)
    groups, glossary = sidebar_groups()
    return render_template_string(PAGE_HTML, page=p, body_html=md_to_html(p["body"]),
                                  q="", results=None, groups=groups, glossary=glossary,
                                  current=p["slug"], stats=core.stats())


@app.route("/demo/<slug>")
def demo(slug):
    """스크린샷용: 페이지를 열고 챗봇 Q&A 가 이미 채워진 상태로 서버사이드 렌더."""
    try:
        p = core.get_page(slug)
    except KeyError:
        abort(404)
    groups, glossary = sidebar_groups()
    q = request.args.get("q", "반도체 결함 검출에 어떤 XAI를 써?")
    ans = chat_answer(q)
    seed_a_html = markdown.markdown(ans["answer"], extensions=_MD_EXT)
    return render_template_string(PAGE_HTML, page=p, body_html=md_to_html(p["body"]),
                                  q="", results=None, groups=groups, glossary=glossary,
                                  current=p["slug"], stats=core.stats(),
                                  seed_q=q, seed_a_html=seed_a_html, seed_src=ans["sources"])


@app.route("/api/search")
def api_search():
    return jsonify(core.search(request.args.get("q", ""), limit=int(request.args.get("limit", 8))))


@app.route("/api/chat", methods=["POST"])
def api_chat():
    msg = (request.get_json(force=True) or {}).get("message", "")
    return jsonify(chat_answer(msg))


@app.route("/api/stats")
def api_stats():
    return jsonify(core.stats())


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
