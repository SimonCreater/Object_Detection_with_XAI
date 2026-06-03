# Wiki Journal — append-only 변경 기록

MCP Wiki Tool 의 모든 쓰기 작업(wiki_create / wiki_update / wiki_append)이
`wiki_core._journal()` 에 의해 시간순으로 자동 기록된다. 사람이 직접 편집하지 않는다.

형식: `- \`ISO타임스탬프\` **action** \`slug\` — detail`

> editor 에이전트가 쓰기 툴을 호출할 때마다 아래에 한 줄씩 추가된다(감사 추적).
