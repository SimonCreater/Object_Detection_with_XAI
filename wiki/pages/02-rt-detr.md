---
title: "RT-DETR (Real-Time Detection Transformer)"
slug: 02-rt-detr
summary: "CNN 백본 + Efficient Hybrid Encoder(AIFI+CCFF) + Transformer 디코더를 결합하고 Uncertainty-minimal Query Selection으로 초기 쿼리 품질을 높여, NMS 없이 YOLO를 능가한 최초의 실시간 end-to-end 검출기. 본 연구의 핵심 모델."
tags: [rt-detr, detr, transformer, cnn-hybrid, real-time, nms-free, object-detection]
category: model
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "raw/RT-DETR.pdf"
    cite: "Zhao et al., DETRs Beat YOLOs on Real-time Object Detection, arXiv:2304.08069v3 (2024)"
related:
  - 01-object-detection-overview
  - 03-detr-and-set-prediction
  - 04-xai-for-object-detection
  - 08-semiconductor-defect-detection
---

# RT-DETR (Real-Time Detection Transformer)

> CNN 백본의 속도와 Transformer 디코더의 NMS-free end-to-end 추론을 결합한 **CNN-Transformer 하이브리드** 검출기. "DETRs Beat YOLOs"(Zhao et al., Baidu, 2023/24)가 제안한, **저자 표현 기준 최초의 실시간 end-to-end 검출기**다.

## 핵심

RT-DETR(Zhao et al., Baidu)은 **backbone → Efficient Hybrid Encoder → Transformer decoder + 보조 예측 헤드**로 구성된다(논문 Fig. 4).

```
이미지 → [CNN Backbone] → 마지막 3스테이지 특징 {S3, S4, S5}
        → [Efficient Hybrid Encoder]  (AIFI + CCFF)
        → [Uncertainty-minimal Query Selection]  (상위 300개 인코더 특징 = 초기 쿼리)
        → [Transformer Decoder + 보조 헤드 + 이분 매칭] → (bbox, class) 집합  (NMS 없음)
```

논문이 강조하는 두 가지 핵심 기여:

1. **Efficient Hybrid Encoder** — 다중 스케일 특징을 빠르게 처리하기 위해, **intra-scale 상호작용**과 **cross-scale 융합**을 분리(decouple)해 속도를 끌어올린다.
2. **Uncertainty-minimal Query Selection** — 분류 점수만 보던 기존 query selection과 달리, 분류·위치 품질의 불확실성을 명시적으로 최소화해 **고품질 초기 쿼리**를 디코더에 제공한다.

추가로, **재학습 없이** 디코더 레이어 수만 바꿔 속도/정확도를 조절(flexible speed tuning)할 수 있다.

## 상세

### 동기 (Why) — NMS가 만든 딜레마

YOLO 계열은 속도-정확도 균형이 좋지만 **NMS 후처리**가 필요하다. NMS는 (1) 추론 속도를 늦추고 (2) confidence·IoU 두 임계값이 속도·정확도를 동시에 불안정하게 만든다(논문 §3, Table 1: 임계값에 따라 NMS 커널 시간이 1.06~2.46 ms로 출렁임). 반면 DETR류는 NMS를 없앴지만 연산량이 커서 실시간이 안 됐다. RT-DETR은 "DETR의 NMS-free 장점을 유지하면서 실시간으로 만든다"를 목표로 한다.

### 1) Efficient Hybrid Encoder (AIFI + CCFF)

기존 DETR에서 인코더가 병목이다 — Deformable-DETR에서 인코더는 GFLOPs의 49%를 쓰면서 AP 기여는 11%에 불과(논문이 인용한 Lin et al.). RT-DETR은 변형(variant A~E) 실험으로 "intra-scale와 cross-scale를 동시에 처리하는 것은 비효율"임을 보이고, 두 모듈로 분리한다.

- **AIFI (Attention-based Intra-scale Feature Interaction)**: self-attention을 **최상위 스케일 S5에만** 적용. 의미 정보가 풍부한 고수준 특징에서만 개념 간 연결을 잡고, 저수준 특징의 intra-scale 상호작용은 불필요·혼란 위험이 있어 생략. (Ablation: S5에만 적용 시 D 대비 지연 35% 감소 + AP 0.4%p 향상.)
- **CCFF (CNN-based Cross-scale Feature Fusion)**: cross-scale 융합 경로에 **RepConv 기반 RepBlock**으로 구성된 fusion block들을 삽입해 인접 스케일을 융합(논문 Fig. 5).

수식으로는 `Q=K=V=Flatten(S5)`, `F5=Reshape(AIFI(Q,K,V))`, `O=CCFF({S3,S4,F5})` (논문 Eq. 1). 하이브리드 인코더(variant E)는 D 대비 지연 24% 감소.

> 정정 메모: 흔한 오기인 **"CCFM"은 틀렸고 정식 명칭은 CCFF**다. AIFI는 전 스케일이 아니라 **S5에만** 적용된다.

### 2) Uncertainty-minimal Query Selection

기존 query selection은 **classification score**만으로 상위 K개 인코더 특징을 골랐다. 그러나 검출기는 범주와 위치를 함께 모델링해야 하므로, 분류 점수만 보면 **위치 신뢰도가 낮은 특징**이 초기 쿼리로 뽑혀 불확실성이 커진다.

RT-DETR은 위치 분포 P와 분류 분포 C의 불일치로 **불확실성 U**를 정의하고, 이를 손실에 넣어 경사하강으로 직접 최소화한다(논문 Eq. 2~3):

```
U(X̂) = ‖ P(X̂) − C(X̂) ‖
L(X̂, Ŷ, Y) = L_box(b̂, b) + L_cls(U(X̂), ĉ, c)
```

효과: 상위 300개 선택 특징 중 분류·IoU가 모두 0.5 초과인 "양질" 비율이 vanilla 0.30 → 0.67로 증가(Table 4), AP +0.8%p(47.9 → 48.7).

> 정정 메모: 이 기법의 정식 명칭은 **Uncertainty-minimal Query Selection**이다. "IoU-aware Query Selection"이라는 이름은 틀렸다.

### 3) 유연한 속도 튜닝 (재학습 불필요)

디코더는 6레이어(기본)로 학습하되, **추론 시 마지막 일부 레이어를 떼어내 속도를 높일 수 있다**. Ablation(Table 5): RT-DETR-R50-Det6에서 5번째 레이어로 추론하면 AP는 0.1%p만 손실(53.1 → 53.0)하면서 지연이 9.3 → 8.8 ms로 감소. 인라인 검사처럼 throughput 제약이 강한 반도체 검사 환경에 잘 맞는 특성이다.

### 성능 (COCO val2017, T4 GPU / TensorRT FP16)

| 모델 | AP | FPS | #Params |
|---|---|---|---|
| **RT-DETR-R50** | **53.1%** | **108** | 42M |
| **RT-DETR-R101** | **54.3%** | **74** | 76M |
| (참고) DINO-Deformable-DETR-R50 | 50.9% | 5 | 47M |

- RT-DETR-R50은 **DINO-Deformable-DETR-R50 대비 +2.2%p AP, FPS 약 21배**(108 vs 5).
- Objects365 사전학습 후 fine-tune 시 R50/R101 = **55.3% / 56.2%** AP.
- 주요 하이퍼파라미터: 쿼리 300개, AIFI 1레이어, CCFF RepBlock 3개, embedding dim 256, 헤드 8개, 특징 스케일 3개, 디코더 6레이어, AdamW(lr 1e-4).

### 한계

다른 DETR과 마찬가지로 **소형 객체(AP_S)**가 최강 YOLO보다 약하다 — R50은 L급 최고(YOLOv8-L) 대비 AP_S 0.5%p 낮고, R101은 X급 최고(YOLOv7-X) 대비 0.9%p 낮다(논문 §6). 반도체 미세 결함처럼 작은 타깃이 많은 도메인에선 이 점을 보완 설계해야 한다.

### 본 연구에서의 사용

반도체 이미지 결함 검출의 백본 모델로 RT-DETR을 사용한다. NMS-free 특성 덕에 밀집된 결함에서 중복 억제로 인한 누락이 줄고, 디코더 레이어 조절로 인라인 throughput에 맞출 수 있다. 단 attention은 블랙박스이므로 "왜 이 영역을 결함으로 봤는가"를 [[gradcam-plus-plus]]·[[lrp]] 같은 XAI로 검증한다 → [[xai-for-object-detection]].

### XAI 적용 시 유의점

RT-DETR은 CNN 백본(국소)과 attention(전역)이 섞여 있다. **CNN 단계**는 Grad-CAM++ 류 gradient-CAM이, **attention 단계**는 attention-aware LRP([[lrp]]에서 다루는 AttnLRP)가 자연스럽다. 단일 기법으로 전 구간을 설명하기 어렵다는 점이 본 연구의 동기 중 하나다.

## 관련 페이지

- [Object Detection 개요](01-object-detection-overview.md) — 검출기 계보 속 RT-DETR의 위치
- [DETR와 Set Prediction](03-detr-and-set-prediction.md) — NMS-free 이분 매칭의 원리
- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — 하이브리드 모델 설명 전략

## 참고 / 출처

- 원본 논문: [RT-DETR.pdf](../../raw/RT-DETR.pdf)
- Zhao, Lv, Xu, Wei, Wang, Dang, Liu, Chen, "DETRs Beat YOLOs on Real-time Object Detection", arXiv:2304.08069v3, 2024. (Baidu Inc. / Peking University)
