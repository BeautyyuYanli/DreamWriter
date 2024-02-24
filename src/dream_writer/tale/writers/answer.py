from typing import List

from dream_writer.tale.writers.outline import Outline
from dream_writer.utils import QAPair, TrivalWriter, struct_to_yaml
from msgspec import Struct
from proteus import ProteusMessage, ProteusMessagePrompt


class Answer(Struct, kw_only=True, frozen=True):
    ANSWER: str = "answer"


class TaleAnswerWriter(TrivalWriter):
    GIVEN_QUESTION = "给定的问题"

    def __init__(
        self,
    ):
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
你正在构思一篇十分畅销的短篇小说的片段。使用以下 yaml 格式回答:
```yaml
{struct_to_yaml(Answer())}
```
""".strip(),
                ),
            ],
            templates={
                "default": f"""
{{input}}
如果已知信息可以回答 {self.GIVEN_QUESTION}, 但较为模糊，则发挥想象力将答案补充具体，越有创意越好，越具体越好；
否则，借由 {self.GIVEN_QUESTION} 构思新剧情，越有创意越好，越具体越好。
回答在一行以内:
```yaml
""".strip()
            },
        )
        super().__init__(prompt)

    def invoke(
        self,
        all_details: List[str],
        main_character: Outline.主要人物Struct,
        main_things: Outline.主要事物Struct,
        related_qa: List[QAPair],
        given_question: str,
    ) -> QAPair:
        answer: Answer = self.write_yaml(
            {
                "OUTLINE": all_details,
                "MAIN_CHARACTERS": main_character,
                "MAIN_THINGS": main_things,
                "RELATED_QA": related_qa,
                self.GIVEN_QUESTION: given_question,
            },
            Answer,
        )
        return QAPair(问题=given_question, 答案=answer.ANSWER)
