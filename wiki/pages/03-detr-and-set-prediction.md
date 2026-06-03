---
title: "DETR와 Set Prediction (이분 매칭)"
slug: 03-detr-and-set-prediction
summary: "객체 검출을 '집합 예측'으로 재정의하고 Hungarian 이분 매칭으로 NMS를 제거한 DETR의 핵심 아이디어. RT-DETR이 계승한 NMS-free 메커니즘의 뿌리."
tags: [detr, set-prediction, hungarian-matching, nms-free, transformer, object-query]
category: concept
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: domain-note
    ref: "DETR 계열 학습 노트"
related:
  - 02-rt-detr
  - 01-object-detection-overview
---

# DETR와 Set Prediction (이분 매칭)

> DETR은 검출을 **순서 없는 집합 예측**으로 보고, 예측-정답을 1:1로 묶는 이분 매칭을 학습 손실로 사용한다. 이로써 후처리 NMS가 사라진다.

## 핵심

전통적 검출기는 dense한 후보를 만든 뒤 NMS로 중복을 지운다. DETR(Carion et al., 2020)은 발상을 바꾼다.

1. 고정 개수 `N`개의 **object query**(학습되는 임베딩)를 디코더에 넣는다.
2. 각 query는 하나의 `(bbox, class)` 예측을 낸다 → 총 N개 예측 집합.
3. **Hungarian 알고리즘**으로 예측 N개와 정답 M개(나머지는 "no object")를 비용 최소가 되도록 1:1 매칭.
4. 매칭된 쌍에 대해서만 분류+박스 손실을 계산.

매칭이 1:1이므로 같은 객체에 여러 박스가 몰리지 않는다 → **NMS 불필요**. [[rt-detr]]은 이 NMS-free 골격을 그대로 쓰면서 인코더만 경량화했다.

## 상세

### 이분 매칭 비용

매칭 비용은 분류 확률과 박스 유사도(L1 + GIoU)의 합으로 정의된다. "어떤 예측이 어떤 정답을 담당할지"를 손실 계산 **전에** 결정하는 것이 핵심이며, 이 덕분에 손실이 순열 불변(permutation-invariant)이 된다.

### DETR의 약점과 RT-DETR의 보완

| DETR 약점 | 영향 | RT-DETR의 대응 |
|---|---|---|
| 느린 수렴(500 epoch) | 학습 비용 | IoU-aware query selection으로 좋은 초기 쿼리 제공 |
| 인코더 연산 과중 | 추론 느림 | AIFI + CCFM 분리로 경량화 |
| 작은 객체 약함 | AP_S 저하 | 다중 스케일 + CNN 지역 특징 결합 |

작은 객체 성능은 반도체 미세 결함 검출에서 직접적으로 중요하다 → [[semiconductor-defect-detection]].

## 관련 페이지

- [RT-DETR](02-rt-detr.md) — 이 메커니즘의 실시간 후계자
- [Object Detection 개요](01-object-detection-overview.md) — NMS의 한계 맥락

## 참고 / 출처

- Carion et al., "End-to-End Object Detection with Transformers" (DETR, 2020)
- Kuhn, "The Hungarian Method for the assignment problem" (1955)
