from typing import List

from proteus import ProteusMessage, ProteusMessagePrompt

from dream_writer.utils import TrivalWriter


class TaleSummaryWriter(TrivalWriter):
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
                    content="""
你正在整理一篇十分畅销的短篇小说的草稿。将以上草稿用三句话进行总结，使用以下 yaml 格式:
```yaml
- 句子1
- 句子2
- 句子3
```
""".strip(),
                ),
            ],
            templates={"default": "{input}\n将以上草稿用三句话进行总结:\n```yaml"},
        )
        super().__init__(prompt)

    def invoke(
        self,
        draft: str,
    ) -> str:
        return "\n".join(self.write_yaml({"DRAFT": draft}, List[str]))
