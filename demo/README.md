# demo/ — 실사용 화면 증명

![실사용 스크린샷](demo_screenshot.png)

`demo_screenshot.png` 는 **실제 지식베이스(연구 노트·논문 기반 위키 11페이지)** 가 이 도구의
웹 뷰어(`tools/app.py`, http://127.0.0.1:5000)에 렌더링된 화면이다.

- 좌측: 카테고리(개념/모델/방법/응용)별 페이지 사이드바
- 중앙: `02-rt-detr` 페이지 본문 (front-matter 칩 + markdown 렌더 + 위키링크)
- 우측: Wiki Chatbot 패널 — 위키 검색 기반 Q&A 와 출처 칩

같은 화면을 직접 재현하려면:

```powershell
py tools/app.py
# 브라우저: http://127.0.0.1:5000/demo/02-rt-detr
```
