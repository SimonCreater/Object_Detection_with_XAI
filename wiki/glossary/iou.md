---
title: "IoU (Intersection over Union)"
slug: iou
aliases: [intersection-over-union, 자카드]
summary: "두 박스의 교집합 면적을 합집합 면적으로 나눈 겹침 비율. 검출 매칭·NMS·mAP의 기준값."
related: [01-object-detection-overview, map]
---

# IoU (Intersection over Union)

예측 박스와 정답 박스가 얼마나 겹치는지를 `교집합 / 합집합` 으로 측정한다(0~1). 값이 클수록 정확히 겹친 것. 검출 평가에서 "이 예측이 정답인가"를 가르는 임계값(예: 0.5)으로 쓰이고, [[map]] 계산과 NMS의 중복 판정 기준이 된다. GIoU/DIoU/CIoU는 비겹침·중심거리·종횡비를 반영한 확장이다.
