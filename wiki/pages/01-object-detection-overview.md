---
title: "Object Detection 개요"
slug: 01-object-detection-overview
summary: "이미지 안의 객체를 '어디에(bbox) + 무엇인지(class)' 동시에 찾는 과제. two-stage·one-stage·DETR 계열로 발전했고 본 위키의 출발점이 되는 상위 개념."
tags: [object-detection, bounding-box, two-stage, one-stage, detr, computer-vision]
category: concept
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: domain-note
    ref: "RT-DETR 기반 반도체 결함 검출 연구 노트"
related:
  - 02-rt-detr
  - 04-xai-for-object-detection
  - 08-semiconductor-defect-detection
---

# Object Detection 개요

> 이미지 안의 객체를 **위치(bounding box)** 와 **클래스(label)** 로 동시에 예측하는 컴퓨터 비전 과제. 분류(classification)와 위치추정(localization)을 결합한 문제다.

## 핵심

Object Detection은 입력 이미지에서 *N개의* 객체에 대해 `(x, y, w, h, class, confidence)` 튜플 집합을 출력한다. 단일 객체를 가정하는 image classification과 달리, **객체 수가 가변적**이고 **위치 회귀와 분류를 동시에** 풀어야 한다는 점이 본질적 난점이다.

검출기 계보는 크게 세 갈래다.

| 계열 | 대표 모델 | 특징 |
|---|---|---|
| **Two-stage** | R-CNN, Fast/Faster R-CNN | 영역 후보(RPN) → 분류·회귀. 정확하지만 느림 |
| **One-stage** | YOLO, SSD, RetinaNet | 후보 없이 한 번에 dense 예측. 빠르지만 NMS 의존 |
| **Transformer / Set-prediction** | DETR, Deformable DETR, [[rt-detr]] | 객체를 집합으로 보고 **NMS 없이** end-to-end 예측 |

본 위키가 다루는 [[rt-detr]]은 세 번째 계열에 속하면서 CNN 백본의 속도와 Transformer의 전역 추론을 결합한 하이브리드다.

## 상세

### 평가 지표

- **IoU (Intersection over Union)**: 예측 박스와 정답 박스의 겹침 비율. 매칭 임계값(예: 0.5)의 기준.
- **mAP (mean Average Precision)**: 클래스별 Precision-Recall 곡선 아래 면적(AP)의 평균. COCO에서는 IoU 0.50:0.95 평균을 쓴다.
- **AP_S / AP_M / AP_L**: 작은/중간/큰 객체에 대한 AP. 반도체 미세 결함은 **AP_S**가 핵심.

### NMS와 그 한계

One-stage·two-stage 검출기는 중복 박스를 **NMS(Non-Maximum Suppression)** 후처리로 제거한다. NMS는 (1) 하이퍼파라미터(IoU 임계값)에 민감하고 (2) 밀집 객체에서 정답을 지우며 (3) end-to-end 미분이 끊긴다. DETR 계열은 **이분 매칭(bipartite matching)** 으로 NMS를 제거해 이 문제를 우회한다 → [[rt-detr]] 참고.

### 왜 이 도메인인가 (Why)

반도체 웨이퍼·다이 이미지에서 결함(scratch, particle, bridge 등)은 **작고**, **클래스 불균형이 심하며**, **오검출 비용이 크다**. 따라서 (1) 작은 객체 검출 성능, (2) 추론 속도(인라인 검사), (3) **설명가능성(XAI)** — "왜 이 영역을 결함으로 판단했는가"를 검증할 수단이 모두 필요하다. 본 위키는 이 세 축을 [[rt-detr]] · [[gradcam-plus-plus]] 등 XAI · [[semiconductor-defect-detection]]으로 나눠 정리한다.

## 관련 페이지

- [RT-DETR](02-rt-detr.md) — 본 연구에서 사용하는 검출 모델
- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — 검출기 설명가능성 개요
- [반도체 결함 검출](08-semiconductor-defect-detection.md) — 응용 도메인

## 참고 / 출처

- Ren et al., "Faster R-CNN" (2015)
- Carion et al., "End-to-End Object Detection with Transformers (DETR)" (2020)
- Lin et al., "Microsoft COCO" — mAP 평가 프로토콜
