---
title: "반도체 이미지 결함 검출"
slug: 08-semiconductor-defect-detection
summary: "웨이퍼·다이 이미지에서 scratch/particle/bridge/void 등 미세 결함을 RT-DETR로 검출하고 XAI(GradCAM++/AttnLRP/Visual Precision Search)로 판단 근거를 검증하는 응용 도메인. 본 위키의 최종 목적지."
tags: [semiconductor, defect-detection, wafer, application, small-object, xai-audit]
category: application
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: domain-note
    ref: "반도체 결함 검출 연구 노트"
related:
  - 02-rt-detr
  - 04-xai-for-object-detection
  - 07-visual-precision-search
  - 01-object-detection-overview
---

# 반도체 이미지 결함 검출

> 반도체 웨이퍼/다이의 광학·SEM 이미지에서 미세 결함을 검출하는 과제. 작은 객체·심한 클래스 불균형·높은 오검출 비용이라는 특성 때문에 [[rt-detr]] + 멀티 XAI 조합을 사용한다.

## 핵심

검사 파이프라인은 다음과 같다.

```
웨이퍼/다이 이미지 → [RT-DETR] → 결함 후보 (bbox, class, conf)
                  → [XAI: GradCAM++ / AttnLRP / Visual Precision Search] → 판단 근거 검증
                  → 합·부 판정 + 결함 맵 리포트
```

대표 결함 클래스: **scratch(긁힘)**, **particle(입자)**, **bridge(단락)**, **void(공동)**, **open(단선)**.

## 상세

### 도메인 난점 (Why XAI 필요)

| 난점 | 영향 | 대응 |
|---|---|---|
| 결함이 매우 작음 | AP_S 저하, 누락 | [[rt-detr]] 다중 스케일 + [[gradcam-plus-plus]]로 소형 객체 검증 |
| 클래스 불균형(정상≫결함) | 과소검출 / 편향 | [[visual-precision-search]]로 "검출을 만든 최소 영역" 탐색·오검출 진단 |
| 오검출 비용 큼(양품 폐기/불량 유출) | 신뢰성 요구 | [[lrp]] 보존적 attribution으로 근거 검증 |
| 새로운 결함 패턴 | 분포 변화 | 위키에 신규 결함 페이지 누적(에이전트가 갱신) |

### 멀티 XAI 감사 워크플로우

1. RT-DETR이 결함을 검출.
2. **GradCAM++** 로 "어느 영역"을 봤는지 히트맵 확인 — 결함 위치와 일치하는가?
3. **AttnLRP** 로 attention 단계까지 포함한 보존적 관련성 확인 — 배경 의존은 없는가?
4. **Visual Precision Search** 로 "결함 박스를 만든 최소 영역"을 탐색 — 배경 텍스처 의존 등 오검출 원인을 입력 수준에서 감사.
5. 세 결과가 합치하면 신뢰, 불일치하면 재검토/재라벨.

이 워크플로우 지식이 본 LLM Wiki에 페이지로 축적되고, MCP Wiki Tool을 통해 LLM 에이전트가 질의·갱신한다.

### 왜 LLM Wiki로 관리하는가 (What-Why-How)

- **What**: RT-DETR·XAI·결함 도메인 지식의 단일 출처(single source of truth).
- **Why**: 연구가 진행되며 결함 클래스·XAI 해석 노하우가 빠르게 늘어 → 검색·갱신 가능한 구조 필요.
- **How**: markdown + front-matter 페이지를 MCP 툴로 노출, 편집/챗봇 에이전트가 read/write.

## 관련 페이지

- [RT-DETR](02-rt-detr.md) — 검출 모델
- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — 검증 기법군
- [Visual Precision Search](07-visual-precision-search.md) — 검출 근거 영역 탐색·오검출 진단

## 참고 / 출처

- 반도체 결함 검출 연구 노트 (도메인 정의 문서 docs/01_knowledge_domain.md)
- MixedWM38 / WM-811K 등 공개 웨이퍼 맵 데이터셋(참고)
