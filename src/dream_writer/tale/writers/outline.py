from typing import List

from msgspec import Struct, field
from proteus import ProteusMessage, ProteusMessagePrompt

from dream_writer.utils import (
    TrivalWriter,
    struct_to_yaml,
)


class Outline(Struct, kw_only=True, frozen=True):
    class 剧情梗概Struct(Struct, kw_only=True, frozen=True):
        背景章: List[str] = field(default_factory=lambda: ["背景"])
        开端章: List[str] = field(default_factory=lambda: ["开端"])
        发展章: List[str] = field(default_factory=lambda: ["发展"])
        下滑章: List[str] = field(default_factory=lambda: ["下滑"])
        低谷章: List[str] = field(default_factory=lambda: ["低谷"])
        转折章: List[str] = field(default_factory=lambda: ["转折"])
        高潮章: List[str] = field(default_factory=lambda: ["高潮"])
        结局章: List[str] = field(default_factory=lambda: ["结局"])

    class 主要人物Struct(Struct, kw_only=True, frozen=True):
        名字: str = "人物1"
        性格: List[str] = field(default_factory=lambda: ["性格"])
        身份: List[str] = field(default_factory=lambda: ["身份"])

    class 主要事物Struct(Struct, kw_only=True, frozen=True):
        名字: str = "事物1"
        描述: List[str] = field(default_factory=lambda: ["描述"])

    剧情梗概: 剧情梗概Struct = 剧情梗概Struct()
    主要人物: List[主要人物Struct] = field(
        default_factory=lambda: [Outline.主要人物Struct()]
    )
    主要事物: List[主要事物Struct] = field(
        default_factory=lambda: [Outline.主要事物Struct()]
    )


# print(yaml.dump(to_builtins(Outline()), allow_unicode=True, sort_keys=False))


class TaleOutlineWriter(TrivalWriter):
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
你正在写一篇十分畅销的短篇小说。使用以下 yaml 格式写出小说的大纲:
```yaml
{struct_to_yaml(Outline())}
```
其中剧情梗概的每个阶段都要有 2 句内容，主要人物和主要事物可以有多个。故事中的每个实体都要有名字和描述。
""".strip(),
                ),
            ],
            templates={"default": "{input}\n以 yaml 格式写出小说的大纲:\n```yaml"},
        )
        super().__init__(prompt)

    def invoke(self, insight: str) -> Outline:
        return self.write_yaml({"写作灵感": insight}, Outline)
