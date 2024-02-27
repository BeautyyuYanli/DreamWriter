from typing import List, Optional

from msgspec import Struct

from dream_writer.tale.writers.outline import Outline
from dream_writer.utils import (
    struct_to_builtin,
)


class Chapter(Struct, kw_only=True):
    NAME: str
    DETAILS: List[str]
    CONTENT: Optional[str] = None
    SUMMARY: Optional[str] = None


class Tale(Struct, kw_only=True):
    CHAPTERS: List[Chapter]
    MAIN_CHARACTERS: List[Outline.主要人物Struct]
    MAIN_THINGS: List[Outline.主要事物Struct]

    @classmethod
    def from_outline(cls, outline: Outline) -> "Tale":
        return cls(
            CHAPTERS=[
                Chapter(NAME=name, DETAILS=details)
                for name, details in struct_to_builtin(outline.剧情梗概).items()
            ],
            MAIN_CHARACTERS=outline.主要人物,
            MAIN_THINGS=outline.主要事物,
        )

    def all_details(self, with_idx: bool = False) -> List[str]:
        if with_idx:
            details = [
                f"{idx}. {detail}" for idx, detail in enumerate(self.all_details())
            ]
            return details
        else:
            return [detail for chapter in self.CHAPTERS for detail in chapter.DETAILS]

    def get_detail(self, idx: int) -> str:
        return self.all_details()[idx]

    def get_chapter(self, idx: int) -> Chapter:
        return self.CHAPTERS[idx]

    def get_chapter_idx_by_detail_idx(self, detail_idx: int) -> int:
        for i, chapter in enumerate(self.CHAPTERS):
            if detail_idx < len(chapter.DETAILS):
                return i
            detail_idx -= len(chapter.DETAILS)
        raise ValueError("Index out of range")

    def to_completed_text(self) -> str:
        return "\n".join([chapter.CONTENT or "" for chapter in self.CHAPTERS])
