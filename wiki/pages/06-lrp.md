---
title: "LRP와 AttnLRP (Transformer용 Layer-wise Relevance Propagation)"
slug: 06-lrp
summary: "출력 점수를 보존 규칙(relevance conservation)에 따라 층별로 입력까지 역분배하는 XAI. AttnLRP는 softmax·행렬곱·LayerNorm 등 비선형 연산에 대한 전용 규칙을 Deep Taylor Decomposition으로 유도해, 단일 backward pass로 Transformer의 입력·잠재 뉴런까지 충실하게 설명한다."
tags: [lrp, attnlrp, relevance-propagation, attribution, conservation, transformer-lrp, xai]
category: method
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "raw/AttnLRP.pdf"
    cite: "Achtibat et al., AttnLRP: Attention-Aware Layer-Wise Relevance Propagation for Transformers, arXiv:2402.05602v2 (2024)"
related:
  - 04-xai-for-object-detection
  - 05-gradcam-plus-plus
  - 02-rt-detr
---

# LRP와 AttnLRP (Transformer용 Layer-wise Relevance Propagation)

> 모델 출력 점수 `R`을, 각 층에서 **합이 보존되도록** 뉴런들에게 비례 분배하며 입력까지 역전파한다. 결과는 "각 입력이 출력에 기여한 관련성(relevance)"의 보존적 맵이다. **AttnLRP**(Achtibat et al., Fraunhofer HHI, 2024)는 이를 Transformer의 비선형 연산에 맞게 확장한 최신 변형이다.

## 핵심

LRP의 불변식은 **관련성 보존(conservation)**이다: 어떤 층의 관련성 총합 = 다음 층의 총합 = … = 출력 점수.

```
Σ_i R_i^(l) = Σ_j R_j^(l+1) = f(x)
```

LRP는 신경망을 층별 DAG로 보고, 각 뉴런을 함수 노드로 **개별 분해**한다(additive explanatory model 계열 — SHAP·DeepLIFT·Gradient×Input과 같은 가족). 그래디언트 saliency와 달리 양/음 기여를 보존적으로 추적해 노이즈가 적다. 단일 backward pass로 모든 층의 잠재(latent) attribution까지 얻을 수 있어, perturbation/SHAP류 대비 계산 효율이 압도적이다.

## 상세

### 왜 Transformer엔 표준 LRP가 부족한가

논문 핵심 동기: Transformer에는 **softmax, bi-linear 행렬곱(query·key 곱), LayerNorm** 같은 연산이 있는데, 표준 LRP 규칙은 이들에 제대로 적용되지 않아 (1) 수치 불안정 또는 (2) 낮은 faithfulness를 낳는다. 또 attention map 자체나 attention rollout(Abnar & Zuidema; Chefer et al.)은 **클래스 비특이적**이고 ViT에서 체커보드 아티팩트를 만들며 softmax 출력까지만 설명한다.

### AttnLRP의 기여

- **Deep Taylor Decomposition** 틀에서 비선형 attention 연산(softmax·행렬곱·정규화)에 대한 **새 LRP 규칙**을 유도 — 보존성을 지키면서 비선형 구간을 통과해 관련성을 분배.
- **입력뿐 아니라 잠재 뉴런**까지 충실히 attribute → 개념 기반(concept) 설명, 뉴런 활성/비활성으로 출력 조작(예: "Arctic"→"Desert") 가능(논문 Fig. 2, ActMax 결합).
- LLaMa 2, Mixtral 8x7b(MoE), Flan-T5, **ViT** 등에서 SmoothGrad·Grad×AttnRoll·KernelSHAP 대비 faithfulness·효율 모두 우위(논문 Fig. 1, §4.1). 오픈소스 라이브러리 제공(LRP-eXplains-Transformers).

### 전파 규칙 (composite LRP)

| 규칙 | 용도 |
|---|---|
| **LRP-0** | 기본(수치 불안정) |
| **LRP-ε** | 작은 ε로 안정화, 중간 층 |
| **LRP-γ / αβ** | 양의 기여 강조, 하위(입력 근접) 층 |
| **AttnLRP 규칙** | softmax·행렬곱·LayerNorm 등 Transformer 비선형 연산 전용 |

층 종류·위치에 따라 규칙을 조합(composite)하는 것이 실무 표준이다.

### RT-DETR 적용

순수 CAM이 어려운 [[rt-detr]]의 **AIFI(attention)·Transformer 디코더 단계**에 AttnLRP가 적합하다. RT-DETR은 ViT류와 같은 self-attention·행렬곱·LayerNorm을 쓰므로, AttnLRP 규칙으로 attention을 통과해 입력 토큰·잠재 뉴런까지 관련성을 분배할 수 있다. 즉 [[gradcam-plus-plus]]가 **CNN 백본 단**을, AttnLRP가 **attention 단**을 담당하는 분업이 가능하다 → [[xai-for-object-detection]].

### 장단점

| 장점 | 단점 |
|---|---|
| 보존성 → 정량적·신뢰성 높은 attribution | 층별/연산별 전용 규칙 구현 부담 |
| 단일 backward pass로 잠재 뉴런까지 설명 | 규칙 선택이 결과에 민감 |
| AttnLRP로 Transformer 비선형 연산까지 충실 | 검출(객체 단위) 태스크 적용은 추가 설계 필요 |

## 관련 페이지

- [Object Detection을 위한 XAI](04-xai-for-object-detection.md)
- [Grad-CAM++](05-gradcam-plus-plus.md) — CNN 단 보완 기법
- [RT-DETR](02-rt-detr.md) — attention 단 설명 대상

## 참고 / 출처

- 원본 논문: [AttnLRP.pdf](../../raw/AttnLRP.pdf)
- Achtibat, Hatefi, Dreyer, Jain, Wiegand, Lapuschkin, Samek, "AttnLRP: Attention-Aware Layer-Wise Relevance Propagation for Transformers", arXiv:2402.05602v2, 2024.
- Bach et al., "On Pixel-Wise Explanations … by LRP" (2015); Montavon et al., "LRP: An Overview" (2019) — LRP 원리.
