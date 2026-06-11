# (예시 원문) Focal Loss 메모

> 이 파일은 raw/ 투입 → 위키 통합 절차를 연습하기 위한 **예시 자료**입니다.
> Claude Code 에서 `/new-wiki-page raw/example_note.md` 를 실행해 보세요.

## 메모 내용

Focal Loss 는 one-stage 검출기의 클래스 불균형 문제를 다루기 위해 제안된 손실 함수다.
표준 cross-entropy 에 변조 계수 (1 - p_t)^gamma 를 곱해, 이미 잘 분류된(쉬운) 배경
샘플의 손실 기여를 줄이고 어려운 샘플에 학습을 집중시킨다.

- gamma = 0 이면 표준 CE 와 동일, gamma 가 클수록 쉬운 샘플 억제가 강해진다 (논문 실험은 gamma=2 중심).
- 클래스 가중 alpha 와 함께 쓰는 alpha-balanced 형태가 실용적으로 더 낫다고 보고된다.
- RetinaNet 은 이 손실 + FPN 백본으로, anchor 기반 one-stage 가 two-stage 정확도를
  따라잡을 수 있음을 보였다.

## 출처

- Lin et al., "Focal Loss for Dense Object Detection", ICCV 2017. arXiv:1708.02002
