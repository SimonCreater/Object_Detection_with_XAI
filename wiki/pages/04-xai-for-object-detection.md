---
title: "Object Detection을 위한 XAI"
slug: 04-xai-for-object-detection
summary: "검출기의 '왜 이 영역을 이 클래스로 봤는가'를 설명하는 XAI 방법론 분류. 분류 전용 XAI를 검출(다중 객체·bbox·attention)로 확장할 때의 쟁점과 GradCAM++/AttnLRP/Visual Precision Search의 위치."
tags: [xai, explainability, saliency, attribution, object-detection, interpretability]
category: concept
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: domain-note
    ref: "XAI for detection 연구 노트"
related:
  - 05-gradcam-plus-plus
  - 06-lrp
  - 07-visual-precision-search
  - 02-rt-detr
---

# Object Detection을 위한 XAI

> 검출기가 특정 박스/클래스를 출력한 근거를 사람이 검증 가능한 형태(히트맵·개념 점수·관련성)로 드러내는 기법군. 분류 XAI를 **다중 객체 + 위치 + attention** 환경으로 확장해야 한다.

## 핵심

XAI(eXplainable AI) 방법은 크게 세 축으로 나뉜다.

| 축 | 질문 | 본 위키의 대표 기법 |
|---|---|---|
| **Gradient/CAM (saliency)** | 어느 **픽셀**이 중요했나? | [[gradcam-plus-plus]] |
| **Relevance 역전파** | 출력 점수를 입력·잠재 뉴런까지 **분해**하면? | [[lrp]] (AttnLRP) |
| **블랙박스 탐색** | 모델 내부 없이 **어느 영역**이 검출을 만드나? | [[visual-precision-search]] |

분류기에서는 출력이 단일 logit이라 단순하지만, 검출기는 **객체마다** 별도의 클래스·박스 출력을 가지므로 "어떤 객체의 어떤 출력을 설명할지" 타깃 지정이 선행돼야 한다.

## 상세

### 검출 XAI의 고유 쟁점

1. **타깃 선택**: 특정 detection(특정 query/박스)의 class logit 또는 objectness를 설명 대상으로 잡아야 한다.
2. **bbox 회귀 설명**: 분류 logit뿐 아니라 좌표 회귀에 기여한 영역도 별개 관심사.
3. **하이브리드 구조**: [[rt-detr]]은 CNN+Transformer 혼합 → CNN 단에는 CAM류, attention 단에는 LRP/attention rollout이 적합.
4. **충실성(faithfulness)**: 히트맵이 "보기 좋은가"가 아니라 "모델 결정을 실제로 반영하는가"를 deletion/insertion 곡선 등으로 검증.

### 본 연구의 멀티 XAI 전략 (Why)

단일 기법은 RT-DETR 전 구간을 설명하지 못한다. 따라서:

- **GradCAM++** — CNN 백본/특징맵 단계의 공간적 근거(어디).
- **AttnLRP** — 출력 점수를 attention 단계를 통과해 입력·잠재 뉴런까지 보존적으로 분해(얼마나).
- **Visual Precision Search** — 모델 내부 없이 "검출을 만든 최소 영역"을 탐색해 오검출 원인 진단(블랙박스 검증).

세 결과를 교차 검증해 검출 판단의 신뢰도를 높인다. 표현 자체의 기하가 어떻게 형성·변형되는지는 [[manifold-geometry-interpretability]]·[[pruning-robustness-geometry]]로 보완한다. (이 멀티-XAI 감사 전략을 적용한 응용 예: [[semiconductor-defect-detection]].)

## 관련 페이지

- [GradCAM++](05-gradcam-plus-plus.md) · [LRP/AttnLRP](06-lrp.md) · [Visual Precision Search](07-visual-precision-search.md)
- [RT-DETR](02-rt-detr.md) — 설명 대상 모델

## 참고 / 출처

- Selvaraju et al., "Grad-CAM" (2017) / Chattopadhyay et al., "Grad-CAM++" (2018)
- Achtibat et al., "AttnLRP" (2024); Bach et al., "On Pixel-Wise Explanations (LRP)" (2015)
- Chen et al., "Interpreting Object-level Foundation Models via Visual Precision Search" (2025)
