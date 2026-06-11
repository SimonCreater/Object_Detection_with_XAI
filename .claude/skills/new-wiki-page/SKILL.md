---
name: new-wiki-page
description: raw/ 에 넣은 원문 자료(논문 PDF·노트·메모) 1건을 읽고 스키마에 맞는 새 위키 페이지를 생성한 뒤 검증까지 마친다. 사용자가 "이 자료 위키에 통합해줘", "raw에 넣은 파일로 페이지 만들어줘"라고 할 때 사용.
---

# new-wiki-page — 원문 자료 → 위키 페이지 통합 절차

입력: `raw/` 안의 파일 1건 (사용자가 지정하지 않았으면 `raw/` 목록을 보여주고 무엇을 통합할지 확인).

## 절차 (순서 고정)

1. **원문 정독** — 지정된 파일을 읽는다(PDF면 Read 툴의 PDF 읽기 사용). 핵심 주장·수치·방법을
   출처 페이지/섹션과 함께 메모한다. **원문에 없는 내용을 지어내지 않는다.**
2. **중복 확인** — 기존 위키에서 같은 주제를 검색한다:
   ```powershell
   py -X utf8 -c "import sys; sys.path.insert(0,'tools'); import wiki_core; [print(r['slug'], r['title']) for r in wiki_core.search('<주제 키워드>')]"
   ```
   - 이미 같은 주제 페이지가 있으면 → 새로 만들지 말고 그 페이지에 보강(append/update)하고 사용자에게 알린다.
3. **페이지 작성** — `wiki/pages/NN-kebab-slug.md` 생성. `NN`은 기존 최대 번호 +1.
   front-matter 는 `wiki/SCHEMA.md` 의 필수 필드 전부(title/slug/summary/tags/category/status/created/updated/source/related).
   - `source.ref` 에 raw/ 파일명을 적는다. 본문 끝에 `## 참고 / 출처` 로 서지정보를 남긴다.
   - 본문 구조: `# 제목` → `> 요약` → `## 핵심` → `## 상세` → `## 관련 페이지` → `## 참고 / 출처`.
   - 기존 페이지와 연결: 관련 페이지를 `[[slug]]` 또는 `(slug.md)` 로 링크하고 front-matter `related` 에도 추가.
4. **검증 (필수 게이트)** —
   ```powershell
   py tools/wiki_core.py --validate
   ```
   exit 0 이 아닐 경우 에러를 고치고 재실행. (PostToolUse Hook 이 자동으로도 실행함)
5. **메타 동기화** — `wiki/llms.txt` 의 목록과 `wiki/_meta/source_index.md` 의 매핑 표에 새 페이지 1줄 추가.
6. **보고** — 생성한 slug, 한 줄 요약, 검증 결과를 사용자에게 보고하고,
   웹 뷰어(`py tools/app.py` → http://127.0.0.1:5000)에서 확인하는 방법을 안내한다.

## 금지

- 출처 없는 수치·주장 작성, 기존 페이지 삭제, `wiki/_meta/journal.md` 수정.
- `raw/` 원문 변경. (RULES.md 6절)
