---
title: "Faster R-CNN과 Two-stage 검출"
slug: 09-faster-rcnn-two-stage
summary: "RPN(Region Proposal Network)으로 영역 후보를 거의 무료로 생성하고 Fast R-CNN으로 분류·회귀하는 대표적 two-stage 검출기. anchor 개념의 출발점이자 RT-DETR의 NMS-free·query 설계와 대비되는 기준선."
tags: [faster-rcnn, two-stage, rpn, anchor, region-proposal, object-detection]
category: model
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "Faster-Rcnn.pdf"
    cite: "Ren, He, Girshick, Sun, Faster R-CNN, arXiv:1506.01497v3 (2016)"
related:
  - 01-object-detection-overview
  - 02-rt-detr
  - 03-detr-and-set-prediction
---

# Faster R-CNN과 Two-stage 검출

> 영역 후보(region proposal)를 별도 알고리즘(Selective Search)이 아니라 **신경망(RPN)**으로 생성해, 검출망과 합성곱 특징을 공유함으로써 "거의 무료"로 후보를 만든 검출기. RT-DETR이 극복하려는 **anchor·NMS·후보 단계**의 기준선이다.

## 핵심

Faster R-CNN(Ren et al., Microsoft Research, 2015)은 두 모듈로 구성된 **단일 통합 네트워크**다.

```
이미지 → [공유 Conv layers] → 특징맵
        ├─→ [RPN] → 영역 후보(proposals) + objectness 점수   (= "어디를 볼지" 알려주는 attention)
        └─→ [RoI Pooling → Fast R-CNN] → 클래스 + bbox 정밀화
```

- **핵심 기여 = RPN(Region Proposal Network)**: 특징맵 위를 슬라이딩하는 작은 FCN이 각 위치에서 객체 경계와 objectness를 동시에 예측. 검출망과 conv 특징을 공유하므로 후보 생성의 한계 비용이 이미지당 **약 10 ms**에 불과(Selective Search는 CPU에서 약 2초).
- 결과: VGG-16 기준 이미지당 후보 300개만으로 **5 fps**(전 단계 포함), PASCAL VOC 2007/2012·MS COCO에서 당시 SOTA.

## 상세

### Anchor — 다중 스케일을 위한 회귀 기준

각 슬라이딩 위치에서 **k개의 anchor box**(기본 3 scale × 3 aspect ratio = 9개)를 기준으로 후보를 예측한다. `reg` 레이어는 4k개 좌표, `cls` 레이어는 2k개 objectness 점수를 출력. 이미지·필터 피라미드 대신 "anchor 피라미드"를 써서 **단일 스케일 이미지/필터**로 다중 스케일을 다루므로 빠르다. anchor는 **translation-invariant**해 모델 크기도 작다.

### 학습 목표

RPN은 multi-task loss를 최소화한다 — `L = (1/N_cls)ΣL_cls(p_i, p*_i) + λ(1/N_reg)Σ p*_i L_reg(t_i, t*_i)` (논문 Eq. 1). 양성 anchor 판정: GT와 IoU 최고이거나 IoU>0.7; 음성: 모든 GT와 IoU<0.3. bbox 회귀는 anchor 대비 중심·로그 스케일 파라미터화(Eq. 2)를 쓰고 smooth-L1 손실. λ에는 둔감(1~100 범위에서 mAP ±1%).

### 특징 공유 학습 (4-step Alternating Training)

RPN과 Fast R-CNN이 conv를 공유하도록 (1) RPN 학습 → (2) 그 후보로 Fast R-CNN 학습 → (3) 공유 conv 고정 후 RPN 고유층만 미세조정 → (4) 공유 conv 고정 후 Fast R-CNN 고유층 미세조정. (근사 joint training도 제공, 학습시간 25~50% 단축.)

### NMS의 역할 (여기서 RT-DETR과 갈린다)

RPN 후보들은 서로 크게 겹치므로 **cls 점수 기준 NMS(IoU 임계 0.7)**로 약 2000개로 줄이고 상위 N개를 검출에 사용한다. 논문은 NMS가 정확도를 해치지 않는다고 보고하지만, NMS는 본질적으로 (1) 후처리 단계, (2) 임계값 하이퍼파라미터, (3) 미분 단절을 남긴다. [[rt-detr]]은 이분 매칭으로 이 단계를 통째로 제거한다 → [[detr-and-set-prediction]].

### 성능 (대표 수치)

- PASCAL VOC 2007 test (VGG-16, 후보 300): 07 학습 69.9% mAP, 07+12 학습 73.2%, COCO+07+12 78.8%.
- MS COCO test-dev (VGG-16): 42.1% mAP@.5 / 21.5% mAP@[.5,.95]. ResNet-101로 교체 시 COCO val 41.5/21.2 → **48.4/27.2**로 상승 — "더 좋은 특징에서 더 큰 이득"을 보이며 ILSVRC·COCO 2015 다수 트랙 1위의 토대.
- 속도(VGG-16, K40): conv 141 + proposal 10 + region-wise 47 = 총 **198 ms (5 fps)**. ZF net은 17 fps.

### 본 연구에서의 위치

Faster R-CNN은 **two-stage 정확도 기준선**이자 anchor·NMS·후보 단계의 원형이다. 반도체 결함처럼 정밀 위치가 중요한 경우 여전히 강하지만, 인라인 throughput과 NMS 하이퍼파라미터 부담 때문에 본 연구는 NMS-free·query 기반 [[rt-detr]]을 주 모델로 채택했다. 두 모델 대비는 "후보+NMS" vs "집합 예측"의 차이를 보여준다.

## 관련 페이지

- [Object Detection 개요](01-object-detection-overview.md) — two/one-stage·DETR 계보
- [RT-DETR](02-rt-detr.md) — NMS·anchor를 제거한 후속 설계
- [DETR와 Set Prediction](03-detr-and-set-prediction.md) — 이분 매칭으로 NMS를 없애는 원리

## 참고 / 출처

- 원본 논문: [Faster-Rcnn.pdf](../../Faster-Rcnn.pdf)
- Ren, He, Girshick, Sun, "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks", arXiv:1506.01497v3, 2016.
