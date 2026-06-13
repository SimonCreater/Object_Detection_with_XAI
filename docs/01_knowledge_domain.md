# 지식 도메인 정의서 — Object Detection & XAI (설명가능 객체검출)

> 제출물 ①: 본 LLM Wiki Tool 이 다루는 **지식 도메인**을 정의하는 문서.
> (수업 주제 자체가 아니라, 연구에서 실제로 다루는 도메인을 대상으로 한다.)

## 1. 도메인 한 줄 정의

**객체검출 모델(RT-DETR·DETR·Faster R-CNN)** 의 작동 원리와, 그 판단 근거를
**XAI(Grad-CAM++ · AttnLRP · Visual Precision Search)** 및 **표현 기하 해석**으로 검증·감사하는
**"설명가능한 객체검출(Explainable Object Detection)" 연구 지식 영역**.
검출기·XAI 기법 논문을 정확히 정리·연결하는 것이 1차 목표이며, 반도체 결함검출 등은 이를 적용하는 응용 사례다.

## 2. 왜 이 도메인인가 (Why this domain)

- 강의 주제(Agentic Coding)를 그대로 위키화하면 평가가 엄격해질 수 있어, **연구자 본인이 실제 수행 중인 주제**를 택했다.
- 객체검출·XAI 분야는 (a) 모델·해석 기법 논문이 빠르게 늘고, (b) 모델·기법·응용이 얽힌 다층 지식이라
  **검색·갱신 가능한 단일 출처(single source of truth)** 가 실질적으로 필요하다 → LLM Wiki 의 동기와 정확히 부합.
- 즉 핵심은 **검출 논문과 XAI 논문을 잘 설명·연결하는 지식 베이스**이고, 특정 응용(반도체 등)에 종속되지 않는다.

## 3. 지식 범위 (Scope) — 3개 축

| 축 | 내용 | 대응 위키 페이지 |
|---|---|---|
| **모델** | RT-DETR, DETR/Set-prediction, NMS-free, Faster R-CNN(two-stage 기준선) | `02-rt-detr`, `03-detr-and-set-prediction`, `09-faster-rcnn-two-stage` |
| **설명가능성(XAI)** | Grad-CAM++, AttnLRP, Visual Precision Search, 검출용 XAI 일반론 | `04-xai-for-object-detection`, `05~07` |
| **표현 기하 해석** | feature manifold mechanistic 해석, pruning·robustness 기하(Angle/Norm/Margin) | `10-manifold-geometry-interpretability`, `11-pruning-robustness-geometry` |
| **응용(사례)** | 멀티-XAI 감사 워크플로우의 적용 예 — 반도체 결함검출은 그 중 하나 | `08-semiconductor-defect-detection` |
| (공통 개념) | 객체검출 개요, IoU/mAP/NMS 용어 | `01`, glossary `iou/map/nms` |

총 **본문 11 페이지 + 용어 3개**, 카테고리 `concept/model/method/application` 로 분류.

## 4. 핵심 엔터티 & 관계 (지식 그래프)

```
[Object Detection]──계열──>[DETR/Set Prediction]──실시간화──>[RT-DETR]
        │                                                      │설명대상
        │(응용)                                                 ▼
        ▼                                       [XAI for Object Detection]
[결함검출 등 응용]<──검증── Grad-CAM++ / AttnLRP / Visual Precision Search ◄────┘
                          + 표현 기하 해석(manifold · pruning robustness)
```

- RT-DETR 은 DETR 의 NMS-free 골격을 계승하면서 인코더를 경량화한 하이브리드. (대비 기준선: Faster R-CNN의 anchor·NMS·후보 단계.)
- 세 XAI 기법은 **상호 보완**(픽셀-어디 / 보존적-얼마나 / 블랙박스 탐색-최소근거영역)으로 단일 기법 한계를 메운다. 표현 기하 해석(manifold·pruning robustness)은 "표현 자체가 어떻게 형성·변형되나"를 본다.
- 핵심 목표는 **검출 모델의 작동 원리 + 그 판단 근거(XAI)** 를 정확히 설명·연결하는 것. 반도체 결함검출은 이를 검증하는 응용 사례 하나다.

## 5. 사용자(독자) & 사용 시나리오

| 사용자 | 질문 예 | Wiki Tool 동작 |
|---|---|---|
| 연구자(본인) | "RT-DETR 의 AIFI 가 뭐였지?" | chatbot → `wiki_search`→`wiki_get` |
| 협업자 | "왜 NMS 가 필요 없어?" | chatbot 이 `03` 페이지 요약 + 출처 링크 |
| 에이전트(자동) | 새 논문·기법 정리 시 페이지 추가 | editor → `wiki_create`/`wiki_append` (저널 기록) |

## 6. 경계 (Out of scope)

- 모델 학습 코드/하이퍼파라미터 튜닝 로그(별도 실험 트래커 영역).
- 데이터셋 원본 이미지(저작/보안). 위키는 **지식·해석**만 보유.
- 일반 컴퓨터비전 전반(분류/세그멘테이션)은 필요 시 `[[future-slug]]` 후보로만 표시.

## 7. 출처

- `raw/` 의 실제 논문 7편을 정독해 작성: RT-DETR, Faster R-CNN, Grad-CAM++, AttnLRP, Visual Precision Search, When Models Manipulate Manifolds, "Understanding Robustness Lottery" — 각 페이지 하단 "참고/출처" 참조.
- 도메인 노트: 객체검출·XAI 연구 진행 기록(01·03·04 페이지), 응용 사례 노트(08 반도체 결함검출).
