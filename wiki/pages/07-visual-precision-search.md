---
title: "Visual Precision Search (검출용 블랙박스 XAI)"
slug: 07-visual-precision-search
summary: "Grounding DINO·Florence-2 같은 객체수준 foundation model의 결정을 설명하는 gradient-free 탐색 기반 XAI. 입력을 superpixel sub-region으로 희소화하고 consistency·collaboration 점수의 submodular 함수로 핵심 영역을 적은 수로 정확히 찾아낸다."
tags: [visual-precision-search, vps, detection-xai, black-box, submodular, grounding-dino, florence-2, saliency]
category: method
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "raw/Interpreting Object-level Foundation Models via Visual Precision Search.pdf"
    cite: "Chen et al., Interpreting Object-level Foundation Models via Visual Precision Search, arXiv:2411.16198v4 (2025)"
related:
  - 04-xai-for-object-detection
  - 05-gradcam-plus-plus
  - 02-rt-detr
---

# Visual Precision Search (검출용 블랙박스 XAI)

> 객체수준 foundation model(Grounding DINO, Florence-2)이 "왜 이 객체를 검출했는가"를, **모델 내부 파라미터를 우회**하고 입력 영역 탐색만으로 설명하는 XAI. gradient·perturbation 방식의 한계(부정확한 위치·노이즈)를 피해, **적은 수의 sub-region**으로 정확한 attribution map을 만든다.

## 핵심

검출 XAI에는 두 진영의 한계가 있다(논문 Fig. 1):

- **Gradient 기반(ODAM 등)**: vision-text feature fusion 때문에 위치 정밀도가 떨어진다.
- **Perturbation 기반(D-RISE 등)**: 샘플링 아티팩트로 saliency map이 노이즈투성이.

**Visual Precision Search(VPS)**의 접근:

1. 입력을 superpixel 분할로 **희소한 sub-region 집합**으로 나눈다.
2. 각 sub-region의 중요도를 두 관점의 점수로 평가: **consistency score**(이 영역이 정확한 검출을 뒷받침하는 단서인가) + **collaboration score**(영역들의 조합 효과).
3. 이 둘을 **submodular 함수**로 묶어, region search로 집합을 반복 확장하며 핵심 영역을 찾는다. 이론적 boundary 보장 포함.
4. gradient-free → 멀티모달 fusion에서 생기는 위치 오류를 원천 회피.

## 상세

### 평가와 성능

데이터셋 RefCOCO·MS COCO·LVIS에서, faithfulness 기준 SOTA(D-RISE) 대비:

- **Grounding DINO**: MS COCO +23.7%, RefCOCO +20.1%, LVIS +31.6%.
- **Florence-2**(MLLM 기반): MS COCO +50.7~102.9%, RefCOCO +66.9%.
- **실패 분석**: 검출 오분류·미검출의 원인을 입력 수준에서 규명(Insertion +36.7~64.3%) — 단순 시각화를 넘어 정량 벤치마크 제공.

### "적은 영역으로 충분/충분조건" 관점

VPS의 목표는 (1) **적은 영역만 노출해도 정확히 검출**되고, (2) 그 핵심 영역을 제거하면 **빠르게 검출 실패**가 일어나는 영역을 찾는 것. 즉 검출 결정의 최소 충분 근거를 식별한다 — Average Drop류 faithfulness 철학과 통한다.

### RT-DETR/검출기 적용

VPS는 모델 내부를 보지 않는 **블랙박스** 방법이라 [[rt-detr]]처럼 CNN+attention이 섞인 하이브리드에도 그대로 쓸 수 있다. gradient가 attention fusion을 통과하며 흐릿해지는 문제([[gradcam-plus-plus]]의 약점)를 피하고, "어느 입력 패치가 이 검출을 만들었나"를 검증한다. 반도체 결함 검출에서는 "결함 박스를 만든 최소 영역"을 찾아 오검출(배경 텍스처 의존 등)을 진단하는 데 직접 쓸 수 있다 → [[xai-for-object-detection]].

### 장단점

| 장점 | 단점 |
|---|---|
| 블랙박스(내부 파라미터 불필요), fusion 위치 오류 회피 | 영역 탐색 반복 → forward pass 비용 |
| 적은 영역으로 정밀한 attribution, 실패 원인 분석 | superpixel 분할 입도에 의존 |
| 이론적 boundary 보장(submodular) | 잠재 뉴런 수준 설명은 아님([[lrp]]/AttnLRP 보완) |

## 관련 페이지

- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — 검출 XAI 기법 분류
- [Grad-CAM++](05-gradcam-plus-plus.md) — gradient 기반 대비
- [LRP/AttnLRP](06-lrp.md) — 내부(잠재) 관점의 보완

## 참고 / 출처

- 원본 논문: [Interpreting Object-level Foundation Models via Visual Precision Search.pdf](../../raw/Interpreting%20Object-level%20Foundation%20Models%20via%20Visual%20Precision%20Search.pdf)
- Chen, Liang, Li, Liu, Li, Huang, Zhang, Cao, "Interpreting Object-level Foundation Models via Visual Precision Search", arXiv:2411.16198v4, 2025. (코드: github.com/RuoyuChen10/VPS)
