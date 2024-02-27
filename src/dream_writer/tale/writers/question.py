from typing import Any, List

from proteus import ProteusMessage, ProteusMessagePrompt

from dream_writer.utils import TrivalWriter


class TaleQuestionWriter(TrivalWriter):
    GIVEN_DETAIL = "给定的情节"

    def __init__(self):
        prompt = ProteusMessagePrompt(
            identity=[
                ProteusMessage(
                    role="system",
                    content="你是一个获得过无数文学奖的天才小说家。",
                )
            ],
            instruct=[
                ProteusMessage(
                    role="system",
                    content=f"""
你正在构思一篇十分畅销的短篇小说的片段。聚焦于{self.GIVEN_DETAIL}提出问题。使用以下 yaml 格式:
```yaml
- 问题1
- 问题2
```
""".strip(),
                ),
            ],
            templates={
                "default": f"{{input}}\n聚焦于{self.GIVEN_DETAIL}提出3个问题，要求分析 {self.GIVEN_DETAIL} 中的对象提问，例如“是什么”/“为什么”/“怎么做”。每行仅一个问号，不要标序号:\n```yaml"
            },
        )
        super().__init__(prompt)

    def invoke(
        self, all_details: Any, main_character: Any, main_things: Any, given_detail: str
    ) -> List[str]:
        return self.write_yaml(
            {
                "OUTLINE": all_details,
                "MAIN_CHARACTERS": main_character,
                "MAIN_THINGS": main_things,
                self.GIVEN_DETAIL: given_detail,
            },
            List[str],
        )
