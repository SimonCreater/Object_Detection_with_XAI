---
title: "Pruning 강건성의 기하 (Robustness Lottery의 기하 시각 분석)"
slug: 11-pruning-robustness-geometry
summary: "신경망 pruning이 내부 특징 표현의 기하를 어떻게 바꾸고 그것이 강건성(robustness)과 어떻게 연결되는지를, 교차엔트로피 손실에서 분해한 세 기하 특징(Angle·L2 Norm·Margin)으로 비교 분석하는 XAI·시각화 연구. 3단계 계층적 비교 시스템으로 pruning 방법·corruption 벤치마크·모델·샘플을 대조한다."
tags: [pruning, robustness, geometry, angle-norm-margin, feature-representation, visual-analytics, xai, imagenet-c]
category: concept
status: stable
created: 2026-06-03
updated: 2026-06-03
source:
  - type: pdf
    ref: "“Understanding Robustness Lottery” A Geometric.pdf"
    cite: "Li et al. (Utah SCI / LLNL), “Understanding Robustness Lottery”: A Geometric Visual Comparative Analysis of Neural Network Pruning Approaches, IEEE TVCG (2024), DOI 10.1109/TVCG.2024.3514996"
related:
  - 10-manifold-geometry-interpretability
  - 04-xai-for-object-detection
  - 06-lrp
---

# Pruning 강건성의 기하 (Robustness Lottery의 기하 시각 분석)

> "왜 어떤 pruning은 모델을 더 **강건(robust)**하게 만들고 어떤 것은 더 취약하게 만드는가"를, **손실 함수에서 분해한 기하 특징**으로 설명하는 시각 분석(visual analytics) 연구. Li et al.(Utah SCI Institute / Lawrence Livermore National Lab, IEEE TVCG 2024)은 마지막 특징 인코딩 층의 표현 기하를 **Angle·L2 Norm·Margin** 세 지표로 측정해, pruning 방법·corruption 벤치마크·모델·샘플을 다층으로 대조한다.

## 핵심

[[manifold-geometry-interpretability]]가 "표현의 기하 구조"를 mechanistic하게 본다면, 이 페이지는 같은 렌즈를 **모델 압축(pruning)과 강건성**에 적용한다. 핵심 발견:

- **손실에서 분해한 기하 특징**: 분류용 교차엔트로피 손실 `−log P(y=i|x)`을 전개하면 예측 확률이 마지막 층 특징 벡터 `X⃗`의 **L2 norm**, 클래스 방향 `W⃗_i`와의 **각(angle θ)**, 그리고 결정 경계까지의 **margin**으로 표현된다(논문 Eq. 1~3). 즉 세 지표는 임의의 부수적 변동이 아니라 **예측에 직접 연결된** 양이다.
  - **L2 Norm** `‖X⃗‖`: 출력 확신도(confidence)에 영향.
  - **Angle** `θ`: 작을수록 해당 클래스로 분류될 확률↑. 오분류 샘플은 정답 클래스 방향과 **큰 각**을 가진다.
  - **Margin**: 결정 경계까지의 최소 거리 = **예측 강건성**의 척도. margin이 크면 큰 corruption·perturbation을 견딘다(오분류 시 음수로 부호화).
- **3단계 계층적 비교 시각화**: (1) pruning 방법·평가 벤치마크 비교 → (2) 모델 특징 표현 비교 → (3) 샘플 단위 비교. 6개 연동 뷰(Evaluation Table, Geometric Similarity, Local/Global Geometry, Geometric Attribution, Sample)로 구성.
- **Robustness Lottery 통찰**: 학습 없이 무작위 초기화에서 부분망을 찾는 **MPTs(Multi-Prize lottery Tickets, biprop)**가 corruption(ImageNet-C/CIFAR-C)에 의외로 강건한데, 그 비결이 일반 학습/재학습 모델과 **뚜렷이 다른 latent 기하**(각의 분산은 작고 평균은 큼)에 있음을 시각적으로 규명. 파라미터 수 감소만으로는 설명되지 않는 **고유 기하**가 강건성에 기여.

## 상세

### 왜 출력이 아니라 기하인가

출력 확률(softmax)은 흔히 **over-calibration** 문제가 있어 신뢰하기 어렵고, 2D 차원축소(t-SNE 등)는 정보 손실로 downstream 분석의 신뢰를 떨어뜨린다. 이 연구는 마지막 분류 직전 층(linear+softmax 입력)의 **고차원 특징**을, 손실과 직접 연결된 기하 지표로 **손실 없이 요약**해 모델 간 비교를 가능케 한다. 지표는 손실에서 유도되므로 **아키텍처 독립**(CNN·Transformer 공통)이다.

### Pruning 방법군과 corruption 평가

비교 대상 pruning: **Random / Magnitude(가중치 절댓값) / Gradient-based(1·2차 미분, Hessian) / MPTs(biprop)**. 강건성 평가는 Hendrycks & Dietterich의 corruption 벤치마크(노이즈·블러·날씨·디지털 19~20종, severity 1~5; MNIST-C·CIFAR-C·**ImageNet-C**). 시스템은 corruption 벤치마크 간 **중복성(redundancy)**도 드러내(예: Gaussian blur↔zoom blur 유사) 평가 파이프라인을 간소화한다.

### 시각 분석 시스템 (6개 뷰)

| 뷰 | 역할 | 대응 task |
|---|---|---|
| Evaluation Table | pruning ratio×corruption 정확도 개요(히스토그램) | T1 |
| Geometric Similarity | 각 표현을 30k차원 기하 벡터→UMAP, MST로 유사도 비교 | T1·T2 |
| Local Geometry | 클래스별 angle/L2 산점도, 두 모델 Δ 비교 | T3 |
| Global Geometry | n+3 평행좌표 + 밀도, 클래스 혼동 구조 | T3 |
| Geometric Attribution | occlusion perturbation으로 픽셀별 기하 민감도 heat map | T5 |
| Sample | 선택 샘플 원본 이미지 검사 | T4 |

### 본 위키에서의 연결

이 관점은 [[manifold-geometry-interpretability]]의 "feature manifold" 아이디어와 짝을 이룬다 — 한쪽은 개수 같은 ordinal 양의 manifold 표현을, 이쪽은 분류 결정의 angle/norm/margin 기하를 본다. 검출기 맥락에서도 **pruning으로 RT-DETR을 인라인 throughput에 맞게 경량화**할 때, 이 기하 지표는 "압축 후에도 결함 검출의 강건성이 유지되는가"를 진단하는 도구가 될 수 있다. attribution 계열([[gradcam-plus-plus]]·[[lrp]]·[[visual-precision-search]])이 "어느 입력이 기여했나"를 본다면, 이 연구는 "표현 기하가 어떻게 변했나"를 본다 → [[xai-for-object-detection]].

> 적용 메모: 원 논문은 분류(CIFAR/ImageNet) 사례지만, 지표가 손실에서 유도돼 **모달리티·아키텍처 독립**이다. 본 위키에서는 검출기 경량화·강건성 분석의 **개념적 토대**로 분류한다.

## 관련 페이지

- [Manifold 기하 해석](10-manifold-geometry-interpretability.md) — 표현 기하의 mechanistic 관점
- [Object Detection을 위한 XAI](04-xai-for-object-detection.md) — attribution 관점과 대비
- [LRP/AttnLRP](06-lrp.md) — 보존적 attribution과의 보완

## 참고 / 출처

- 원본 논문: [“Understanding Robustness Lottery” A Geometric.pdf](../../%E2%80%9CUnderstanding%20Robustness%20Lottery%E2%80%9D%20A%20Geometric.pdf)
- Z. Li, S. Liu, X. Yu, K. Bhavya, J. Cao, J. D. Diffenderfer, P.-T. Bremer, V. Pascucci, "“Understanding Robustness Lottery”: A Geometric Visual Comparative Analysis of Neural Network Pruning Approaches", IEEE Transactions on Visualization and Computer Graphics, 2024. DOI 10.1109/TVCG.2024.3514996.
- 관련: Frankle & Carbin, "Lottery Ticket Hypothesis" (2019); Diffenderfer & Kailkhura, "Multi-Prize Lottery Tickets" (2021); Hendrycks & Dietterich, "Benchmarking … Common Corruptions (ImageNet-C)" (2019).
