---
title: "mAP (mean Average Precision)"
slug: map
aliases: [mean-average-precision, ap]
summary: "클래스별 Precision-Recall 곡선 아래 면적(AP)의 평균. 객체 검출의 표준 정확도 지표."
related: [01-object-detection-overview, iou]
---

# mAP (mean Average Precision)

각 클래스마다 confidence를 낮춰가며 Precision-Recall 곡선을 그리고 그 아래 면적(AP)을 구한 뒤, 전 클래스 평균을 낸 값이 mAP다. COCO 프로토콜은 [[iou]] 임계값 0.50~0.95(0.05 간격)의 AP를 평균한다(mAP@[.5:.95]). 객체 크기별 AP_S/AP_M/AP_L로 세분하며, 반도체 미세 결함은 작은 객체 지표인 **AP_S**가 특히 중요하다.
