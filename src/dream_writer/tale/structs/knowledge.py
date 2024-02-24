from typing import List, Optional, Tuple

import numpy as np
from dream_writer.tale.writers.outline import Outline
from dream_writer.utils import (
    QAPair,
    builtin_to_struct,
    embed,
    struct_to_builtin,
)
from msgspec import json


class Knowledge:
    qa: QAPair
    q_emb: np.ndarray
    important: bool
    chapter_idx: List[int]

    def __init__(
        self,
        qa: QAPair,
        q_emb: np.ndarray,
        important: bool = False,
        chapter_idx: Optional[List[int]] = None,
    ) -> None:
        self.qa = qa
        self.q_emb = q_emb
        self.important = important
        self.chapter_idx = chapter_idx if chapter_idx else []

    def to_serializable_dict(self) -> dict:
        return {
            "qa": struct_to_builtin(self.qa),
            "q_emb": self.q_emb.tolist(),
            "important": self.important,
            "chapter_idx": self.chapter_idx,
        }

    @classmethod
    def from_dict(cls, k_dict: dict) -> "Knowledge":
        return cls(
            qa=builtin_to_struct(k_dict["qa"], QAPair),
            q_emb=np.array(k_dict["q_emb"]),
            important=k_dict["important"],
            chapter_idx=k_dict["chapter_idx"],
        )


class KnowledgeBase:
    knowledges: List[Knowledge]

    def __init__(self) -> None:
        self.knowledges = []

    def add_qa(self, qa_pair: QAPair, important: bool = False) -> None:
        self.knowledges.append(
            Knowledge(
                qa=qa_pair,
                q_emb=embed([qa_pair.问题])[0],
                important=important,
            )
        )

    def add_knowledge(self, knowledge: Knowledge) -> None:
        self.knowledges.append(knowledge)

    def get_knowleges_group_by_chapter(self) -> List[List[Knowledge]]:
        answer: List[List[Knowledge]] = []
        for knowledge in self.knowledges:
            for idx in knowledge.chapter_idx:
                while len(answer) <= idx:
                    answer.append([])
                answer[idx].append(knowledge)
        return answer

    def exists_like_q(self, q_emb, threshold: float = 0.3) -> bool:
        for knowledge in self.knowledges:
            if np.linalg.norm(knowledge.q_emb - q_emb) < threshold:
                return True
        return False

    def get_like_q(
        self, q_emb, threshold: float = 0.8, num_limit=10
    ) -> List[Knowledge]:
        retrieved: List[Tuple[Knowledge, float]] = []
        for knowledge in self.knowledges:
            dis = np.linalg.norm(knowledge.q_emb - q_emb)
            if dis < threshold:
                retrieved.append((knowledge, dis))
        retrieved.sort(key=lambda x: x[1])
        return [i[0] for i in retrieved[:num_limit]]

    def to_json(self) -> bytes:
        tmp = [i.to_serializable_dict() for i in self.knowledges]
        return json.encode(tmp)

    @classmethod
    def from_json(cls, k_json: bytes) -> "KnowledgeBase":
        self = cls()
        k_dicts = json.decode(k_json)
        self.knowledges = [Knowledge.from_dict(i) for i in k_dicts]
        return self

    @classmethod
    def from_outline(cls, outline: Outline) -> "KnowledgeBase":
        self = cls()
        # Init Knowledge Base
        for char in outline.主要人物:
            question = f"{char.名字}是谁？"
            answer = f"{char.名字} {','.join(char.身份)}. {', '.join(char.性格)}."
            print(question, answer)
            self.add_qa(QAPair(问题=question, 答案=answer), important=True)

        for thing in outline.主要事物:
            question = f"{thing.名字}是什么？"
            answer = f"{thing.名字}, {', '.join(thing.描述)}."
            print(question, answer)
            self.add_qa(QAPair(问题=question, 答案=answer), important=True)
        return self
