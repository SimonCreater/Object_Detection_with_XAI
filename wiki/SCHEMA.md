# SCHEMA.md — 페이지 형식 정의

## front-matter (필수)

```yaml
---
title: "사람이 읽는 제목"
slug: NN-kebab-case-slug      # 파일명과 동일(.md 제외)
summary: "한 문단 요약 — 검색·RAG의 핵심 키"
tags: [tag1, tag2]
category: concept|model|method|application
status: draft|stable
created: YYYY-MM-DD
updated: YYYY-MM-DD
source:
  - type: pdf|url|domain-note
    ref: "출처 경로 또는 설명"
related: [other-slug, ...]
---
```

| 필드 | 규칙 |
|---|---|
| `slug` | 파일명과 일치(invariant). 페이지는 `NN-` 숫자 prefix 사용 |
| `summary` | 1문단. 검색 인덱스의 1차 매칭 대상 |
| `category` | concept/model/method/application 중 하나 |
| `updated` | 편집 시 MCP 툴이 자동 갱신 |

## 본문 구조

- `# 제목` (front-matter title과 동일)
- `> 요약` blockquote
- `## 핵심` → `## 상세` → (`## 예시`) → `## 관련 페이지` → `## 참고 / 출처`
- 링크: 페이지 `[제목](slug.md)`, 용어 `[[term-slug]]`

## 본문 길이 가이드

40~250줄. 넘으면 개념 단위로 분리.
