from typing import Dict, List

from msgspec import Struct
from proteus import ProteusMessage, ProteusMessagePrompt

from dream_writer.utils import (
    TrivalWriter,
    struct_to_builtin,
)


class TaleTimeIndicatorWriter(TrivalWriter):
    OUTLINE = "故事大纲"
    GIVEN_QA = "给定问答"

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
你正在构思一篇十分畅销的短篇小说的结构。根据以时间排序的{self.OUTLINE}，分析{self.GIVEN_QA}应属于故事中哪几个连续的时间点？如没有可放置的位置，可以返回空列表。使用以下 yaml 格式回复:
```yaml
TIME_NUM: []
```
""".strip(),
                ),
            ],
            templates={
                "default": f"{{input}}\n根据以时间排序的{self.OUTLINE}，分析{self.GIVEN_QA}应属于故事中哪几个连续的时间点？如没有可放置的位置，可以返回空列表。\n```yaml"
            },
        )
        super().__init__(prompt, temperature=0.2)

    def invoke(
        self,
        serial_details: List[str],
        given_qa: Dict[str, str],
    ) -> List[int]:
        class TimeNum(Struct, kw_only=True, frozen=True):
            TIME_NUM: List[int]

        time_num: TimeNum = self.write_yaml(
            {
                self.OUTLINE: serial_details,
                self.GIVEN_QA: struct_to_builtin(given_qa),
            },
            TimeNum,
        )

        return time_num.TIME_NUM
