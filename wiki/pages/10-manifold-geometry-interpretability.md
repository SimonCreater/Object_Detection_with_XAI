---
title: "Manifold 기하 해석 (특징 다양체 관점의 해석가능성)"
slug: 10-manifold-geometry-interpretability
summary: "신경망이 스칼라 양(개수·위치 등)을 저차원 곡면(feature manifold) 위에 표현하고 기하 변환으로 계산한다는 mechanistic 해석 관점. Anthropic의 linebreaking 사례에서 attention head가 manifold를 '회전·정렬'해 경계를 감지하는 과정을 분석한다."
tags: [interpretability, feature-manifold, geometry, mechanistic, attention, representation, xai]
category: concept
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "When Models Manipulate Manifolds.pdf"
    cite: "Gurnee et al. (Anthropic), When Models Manipulate Manifolds: The Geometry of a Counting Task, arXiv:2601.04480v1 (2026)"
related:
  - 04-xai-for-object-detection
  - 06-lrp
  - 11-pruning-robustness-geometry
---

# Manifold 기하 해석 (특징 다양체 관점의 해석가능성)

> "모델 내부는 어떤 개념을 어떤 **기하 구조**로 표현하고, 그 위에서 어떻게 계산하는가"를 묻는 mechanistic 해석 관점. Anthropic이 Claude 3.5 Haiku의 **고정폭 텍스트 줄바꿈(linebreaking)** 과제를 분석해, 개수(count)가 저차원 곡면(feature manifold) 위에 표현됨을 밝혔다.

## 핵심

본 위키의 검출/XAI 페이지들이 "어느 픽셀이 결정에 기여했나(attribution)"를 다룬다면, 이 페이지는 한 단계 더 들어가 **"표현의 기하 구조"** 자체를 본다. 핵심 발견(논문):

- **개수의 manifold 표현**: 토큰 길이, 현재 줄 글자수, 줄 폭 제약, 남은 글자수 등은 각각 residual stream의 저차원 부분공간에 **곡률이 큰 1차원 곡면**으로 표현된다. 이는 이산 feature 가족(생물의 place cell과 유사)으로도, 연속 manifold로도 **이중 해석**된다.
- **경계 감지**: attention head의 QK 행렬이 한 counting manifold를 **회전시켜** 다른 manifold에 특정 offset으로 정렬 → 두 개수 차이가 목표 범위에 들 때 큰 내적 발생. 여러 head가 다른 offset으로 협력해 "남은 글자수"를 정밀 추정.
- **선형 결정 경계**: "남은 글자수"와 "다음 단어 길이"를 **거의 직교**하는 부분공간에 배치해, 줄바꿈 여부가 선형 분리 가능해진다.
- 곡률은 다수 attention head가 **분산적으로** 만든다(단일 컴포넌트로는 분산 부족). causal intervention과 "visual illusion"(메커니즘을 교란하는 문자열)으로 검증.

## 상세

### Feature ↔ Geometry 이중성

dictionary feature(SAE류 이산 feature)는 메커니즘을 **발견**하는 비지도 진입점이고, attribution graph는 특정 예측에 중요한 feature를 드러낸다. 명시적으로 parametrize 가능한 양(정수 개수 등)에서는 이산 feature 집합을 **연속 manifold와 그 변환**으로 동등하게 기술할 수 있어, 경계 감지 같은 연산이 더 명료해진다. 단, 복잡·비정형 개념에는 manifold 추출이 어렵다("complexity tax").

### 왜 manifold인가 (capacity vs distinguishability)

1..N 정수를 N개 직교 차원으로 쓰면 비효율적이고, 1차원만 쓰면 표현력이 부족하다. 모델은 내재차원 1(개수)을 1 < d ≪ N 차원에 "물결치듯(rippling)" 임베딩해 **용량 제약과 값 구분성**을 최적 절충한다. ripple은 feature superposition 관점의 간섭(interference)에 대응.

### 본 위키에서의 연결

이 관점은 [[lrp]]/AttnLRP의 "attention을 통과하는 attribution"이나 [[rt-detr]]의 attention 단계 해석을 **기하적으로** 재조명한다. 검출기에서도 위치·스케일 같은 ordinal 양이 내부에서 어떤 기하로 표현되는지가 오검출·강건성 이해의 단서가 될 수 있다 → [[pruning-robustness-geometry]]의 기하 특징(Angle/Norm/Margin) 관점과 짝을 이룬다.

> 적용 메모: 이 논문은 LLM(텍스트) 과제 사례지만, "표현의 기하"라는 렌즈는 모달리티 독립적이다. 본 위키에서는 검출기 attention 해석의 **개념적 토대**로 분류한다.

## 관련 페이지

- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — attribution 관점과 대비
- [LRP/AttnLRP](06-lrp.md) — attention 내부 관련성 분배
- [Pruning 강건성의 기하](11-pruning-robustness-geometry.md) — 기하 특징으로 표현 비교

## 참고 / 출처

- 원본 논문: [When Models Manipulate Manifolds.pdf](../../When%20Models%20Manipulate%20Manifolds.pdf)
- Gurnee, Ameisen, Kauvar, Tarng, Pearce, Olah, Batson (Anthropic), "When Models Manipulate Manifolds: The Geometry of a Counting Task", arXiv:2601.04480v1, 2026. (Transformer Circuits, 2025-10-21)
