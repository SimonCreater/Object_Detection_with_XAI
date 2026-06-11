# Source Index — 원본 자료 ↔ Wiki 페이지 매핑

객체검출 LLM Wiki의 각 페이지가 어느 자료에서 유래했는지 추적한다. 페이지 추가/갱신 시 함께 갱신한다.

## 매핑 테이블

| Wiki 페이지 | 원본 자료 | 분량 | 변환 일자 | 상태 |
|---|---|---|---|---|
| [01-object-detection-overview](../pages/01-object-detection-overview.md) | 도메인 노트 | — | 2026-06-03 | stable |
| [02-rt-detr](../pages/02-rt-detr.md) | [RT-DETR.pdf](../../raw/RT-DETR.pdf) | 논문 | 2026-06-03 | stable |
| [03-detr-and-set-prediction](../pages/03-detr-and-set-prediction.md) | 도메인 노트 (DETR) | — | 2026-06-03 | stable |
| [04-xai-for-object-detection](../pages/04-xai-for-object-detection.md) | 도메인 노트 (XAI) | — | 2026-06-03 | stable |
| [05-gradcam-plus-plus](../pages/05-gradcam-plus-plus.md) | [Grad-cam++.pdf](../../raw/Grad-cam++.pdf) | 논문 | 2026-06-03 | stable |
| [06-lrp](../pages/06-lrp.md) | [AttnLRP.pdf](../../raw/AttnLRP.pdf) | 논문 | 2026-06-03 | stable |
| [07-visual-precision-search](../pages/07-visual-precision-search.md) | [Interpreting Object-level … Visual Precision Search.pdf](../../raw/Interpreting%20Object-level%20Foundation%20Models%20via%20Visual%20Precision%20Search.pdf) | 논문 | 2026-06-03 | stable |
| [08-semiconductor-defect-detection](../pages/08-semiconductor-defect-detection.md) | 연구 노트 (응용) | — | 2026-06-03 | stable |
| [09-faster-rcnn-two-stage](../pages/09-faster-rcnn-two-stage.md) | [Faster-Rcnn.pdf](../../raw/Faster-Rcnn.pdf) | 논문 | 2026-06-03 | stable |
| [10-manifold-geometry-interpretability](../pages/10-manifold-geometry-interpretability.md) | [When Models Manipulate Manifolds.pdf](../../raw/When%20Models%20Manipulate%20Manifolds.pdf) | 논문 | 2026-06-03 | stable |
| [11-pruning-robustness-geometry](../pages/11-pruning-robustness-geometry.md) | [“Understanding Robustness Lottery” A Geometric.pdf](../../raw/%E2%80%9CUnderstanding%20Robustness%20Lottery%E2%80%9D%20A%20Geometric.pdf) | 논문 | 2026-06-03 | stable |

## 변환 노트

- **출처 검증**: 02·05·06·07·09·10·11 페이지는 `raw/` 의 실제 PDF 논문을 읽고 작성·정정했다(수치·인용 근거 명시). 01·03·04·08은 연구 도메인 노트 + 공개 논문 인용. (원문 PDF는 저작권·용량 문제로 git 에는 포함되지 않음)
- **TCAV 제거**: 이전 `07-tcav`는 근거 논문이 없어 삭제하고, 실제 보유 논문 기반 `07-visual-precision-search`(검출용 블랙박스 XAI)로 대체했다.
- **시점 의존 표현 제거**: 절대 표현으로 작성.
- **MCP 연동**: 본 위키 디렉토리(`wiki/`)가 `../tools/mcp_server.py`의 `WIKI_ROOT`.

## 미래 확장 후보

본문 `[[wikilink]]` 중 아직 전용 페이지가 없는 것 — 사용자 요청 시 추가:

- `[[attention-rollout]]` — Transformer attention 시각화(LRP 보완)
- `[[deformable-detr]]` — RT-DETR 이전 효율 변형
- 신규 결함 클래스 페이지(분포 변화 시 editor 에이전트가 추가)
