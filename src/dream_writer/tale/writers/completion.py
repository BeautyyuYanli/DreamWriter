from typing import Dict, List, Optional

from proteus import ProteusMessage, ProteusMessagePrompt

from dream_writer.utils import (
    TrivalWriter,
)


class TaleCompletionWriter(TrivalWriter):

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
                    content="你正在创作一篇十分畅销的短篇小说。",
                ),
            ],
        )
        super().__init__(prompt)

    def invoke(
        self,
        related_qa: List[Dict[str, str]],
        current_chapter_theme: str,
        current_chapter: List[str],
        previous_content: str,
        next_chapter: Optional[List[str]],
        is_last_chapter: bool = False,
    ) -> str:
        RELATED_QA = "相关问答"
        PREVIOUS_CONTENT = "前文"
        NEXT_CHAPTHER = "下文"
        INSTRUCTION = "指示"

        instruction = f"""
利用以上 {RELATED_QA} ，围绕 {current_chapter_theme} 的大纲，编写该章节。
{{}}
描写越长越细致越好，但切勿超出 {current_chapter_theme} 的大纲，只能基于 {current_chapter_theme} 的大纲进行填充，又必须完整完成 {current_chapter_theme} 的大纲。同时要做到承上启下。
如果 {RELATED_QA} 中有超出 {current_chapter_theme} 的大纲的内容，可以忽略。
""".strip()
        with_prev = f"要求承接 {PREVIOUS_CONTENT} 进行连贯地续写，但切勿重复 {PREVIOUS_CONTENT} 中已有的剧情。逻辑应与 {PREVIOUS_CONTENT} 一致，可以忽略 {RELATED_QA} 中存在冲突的逻辑。"
        without_prev = ""
        with_next = f"本章节只是全文的一部分，切勿写出结局，结尾要导向 {NEXT_CHAPTHER} 的开头，但切勿写出 {NEXT_CHAPTHER} 中存在的剧情，可以忽略 {RELATED_QA} 中存在于 {NEXT_CHAPTHER} 的剧情。切勿做出总结。"
        without_next = "本章节要设计一个简单而壮丽的结局，并总结全文。"

        instruction = (
            instruction.format(with_prev + without_next)
            if is_last_chapter
            else (
                instruction.format(without_prev + with_next)
                if previous_content == ""
                else instruction.format(with_prev + with_next)
            )
        )

        prompt = {
            RELATED_QA: related_qa,
            **({PREVIOUS_CONTENT: previous_content} if previous_content != "" else {}),
            current_chapter_theme: current_chapter,
            **({NEXT_CHAPTHER: next_chapter} if next_chapter is not None else {}),
            INSTRUCTION: instruction,
        }
        return self.write_yaml(
            prompt,
            str,
        )
