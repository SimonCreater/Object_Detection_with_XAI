---
title: "Grad-CAM++"
slug: 05-gradcam-plus-plus
summary: "마지막 컨볼루션 특징맵의 그래디언트를 가중합해 클래스별 위치 히트맵을 만드는 Grad-CAM의 개선판. 픽셀별 2차 그래디언트 가중치로 다중·소형 객체 설명을 강화한다."
tags: [gradcam, gradcam-plus-plus, saliency, cam, gradient, xai]
category: method
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "Grad-cam++.pdf"
    cite: "Chattopadhyay, Sarkar, Howlader, Balasubramanian, Grad-CAM++, arXiv:1710.11063v3 (2018)"
related:
  - 04-xai-for-object-detection
  - 06-lrp
  - 02-rt-detr
---

# Grad-CAM++

> 타깃 클래스 점수의 그래디언트를 마지막 컨볼루션 특징맵에 역전파해 채널별 가중치를 구하고, 이를 가중합해 **클래스 식별 히트맵**을 만든다. ++ 버전은 픽셀별 가중치를 정교화해 다중·소형 객체에 강하다.

## 핵심

Grad-CAM은 특징맵 `A^k`에 대한 클래스 점수 `y^c`의 그래디언트를 공간 평균해 채널 중요도 `α_k`를 구한 뒤 `ReLU(Σ_k α_k A^k)`로 히트맵을 만든다.

**Grad-CAM++** 는 `α_k`를 단순 평균이 아니라 **2차·3차 그래디언트 기반 픽셀별 가중치**로 계산한다(논문 Eq. 11; class score를 지수함수에 통과시키면 closed-form으로 단일 backward pass에 계산 가능, Eq. 19). 효과:

- 한 이미지에 **같은 클래스 객체가 여러 개** 있을 때 각각을 포착.
- **작은 객체**의 기여가 평균에 묻히지 않음 → 반도체 미세 결함에 유리.
- 모든 `α_k^{ij}=1/Z`이면 Grad-CAM으로 환원되는 **일반화**(generalization)다.

논문 검증(VGG-16): ImageNet에서 Average Drop 36.84%(Grad-CAM 46.56%, 낮을수록 좋음), Win 70.72%; PASCAL VOC 2012 localization mLoc(δ=0.5) 0.28 vs 0.16. 이미지 캡셔닝·3D 행동인식에도 일반화된다.

## 상세

### 동작 흐름

```
타깃: detection d의 class logit y^c
1) y^c 를 마지막 conv 특징맵 A^k 로 역전파
2) 픽셀별 가중치 α_k^{ij} 계산 (Grad-CAM++ 공식: 2차/3차 미분 항)
3) w_k = Σ_{ij} α_k^{ij} · ReLU(∂y^c/∂A_k^{ij})
4) L = ReLU( Σ_k w_k A^k )  →  업샘플 → 입력 해상도 히트맵
```

### 검출기·RT-DETR 적용

[[rt-detr]]의 **CNN 백본 마지막 특징맵**을 타깃 레이어로 잡고, 설명할 detection의 class logit을 `y^c`로 둔다. attention 디코더 단계는 그래디언트가 희석되므로 CNN 단 설명에 한정하고, 전역 근거는 [[lrp]]·attention rollout으로 보완한다.

### 장단점

| 장점 | 단점 |
|---|---|
| 구현 단순, 모델 비침습(gradient만 필요) | conv 특징맵 해상도에 한정(거친 히트맵) |
| 다중/소형 객체 ↑ (vs Grad-CAM) | attention/transformer 단계 설명엔 부적합 |

## 관련 페이지

- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — 기법 분류 속 위치
- [LRP](06-lrp.md) — 보존적 분해로 보완

## 참고 / 출처

- 원본 논문: [Grad-cam++.pdf](../../Grad-cam++.pdf)
- Chattopadhyay, Sarkar, Howlader, Balasubramanian, "Grad-CAM++: Improved Visual Explanations for Deep Convolutional Networks", arXiv:1710.11063v3, 2018.
- Selvaraju et al., "Grad-CAM" (2017) — 일반화 대상이 된 원조 기법.
