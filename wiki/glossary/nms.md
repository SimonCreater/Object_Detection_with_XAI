---
title: "NMS (Non-Maximum Suppression)"
slug: nms
aliases: [non-maximum-suppression, 비최대억제]
summary: "겹치는 중복 박스 중 confidence 최댓값만 남기고 억제하는 후처리. DETR/RT-DETR은 이분 매칭으로 이를 제거한다."
related: [03-detr-and-set-prediction, 02-rt-detr]
---

# NMS (Non-Maximum Suppression)

같은 객체에 몰린 여러 후보 박스 중 confidence가 가장 높은 것을 남기고, 그것과 [[iou]]가 임계값 이상인 나머지를 제거하는 후처리다. one-stage/two-stage 검출기에 필수지만 (1) IoU 임계값 튜닝에 민감, (2) 밀집 객체에서 정답을 지움, (3) end-to-end 미분 단절이라는 단점이 있다. [[03-detr-and-set-prediction]]의 이분 매칭은 예측-정답을 1:1로 묶어 NMS 자체를 없앤다.
