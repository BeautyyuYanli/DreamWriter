from typing import Any, Generator, List, Optional, Tuple

from dream_writer.tale.structs.knowledge import Knowledge, KnowledgeBase
from dream_writer.tale.structs.tale import Tale
from dream_writer.tale.writers import (
    TaleAnswerWriter,
    TaleCompletionWriter,
    TaleOutlineWriter,
    TaleQuestionWriter,
    TaleSummaryWriter,
    TaleTimeIndicatorWriter,
)
from dream_writer.utils import QAPair, embed, struct_to_builtin, struct_to_yaml


def generate_outline(
    outline_writer: TaleOutlineWriter, insight: str
) -> Tuple[KnowledgeBase, Tale]:
    # outline: Outline = writer.write_yaml(
    #     {"写作灵感": "一个探险者和一个人工智能在末日后重建世界的故事"}, Outline
    # )
    # with open("src/dream_writer/tale/tmp.yaml", "w") as f:
    #     f.write(struct_to_yaml(outline))
    # with open("src/dream_writer/tale/tmp.yaml", "r") as f:
    #     outline: Outline = yaml_to_struct(f.read(), Outline)
    outline = outline_writer.invoke(insight)
    print(struct_to_yaml(outline))
    return KnowledgeBase.from_outline(outline), Tale.from_outline(outline)


def generate_knowledge_from_question(
    question: str,
    tale: Tale,
    knowledge_base: KnowledgeBase,
    answer_writer: TaleAnswerWriter,
    time_indicator: TaleTimeIndicatorWriter,
    q_emb: Optional[List[float]] = None,
    all_details: Optional[List[str]] = None,
) -> Knowledge:
    q_emb = q_emb if q_emb is not None else embed([question])[0]
    all_details = all_details if all_details is not None else tale.all_details()

    related_qa = [i.qa for i in knowledge_base.get_like_q(q_emb)]
    answer = answer_writer.invoke(
        all_details=all_details,
        main_character=tale.MAIN_CHARACTERS,
        main_things=tale.MAIN_THINGS,
        related_qa=related_qa,
        given_question=question,
    )
    qapair = QAPair(问题=question, 答案=answer.答案)
    knowledge = Knowledge(
        qa=qapair,
        q_emb=q_emb,
    )
    match_knowledge_chapter_idx(knowledge, tale, time_indicator)
    return knowledge


def generate_knowledge_base_from_outline(
    knowledge_base: KnowledgeBase,
    tale: Tale,
    question_writer: TaleQuestionWriter,
    answer_writer: TaleAnswerWriter,
    time_indicator: TaleTimeIndicatorWriter,
) -> Generator[Knowledge, Any, None]:
    all_details = tale.all_details()
    for detail in all_details:
        # 2 times * 3 questions
        questions: List[str] = question_writer.invoke(
            all_details=all_details,
            main_character=struct_to_builtin(tale.MAIN_CHARACTERS),
            main_things=struct_to_builtin(tale.MAIN_THINGS),
            given_detail=detail,
        )
        # ) + question_writer.invoke(
        #     all_details=all_details,
        #     main_character=struct_to_builtin(tale.MAIN_CHARACTERS),
        #     main_things=struct_to_builtin(tale.MAIN_THINGS),
        #     given_detail=detail,
        # )
        q_emb_list = embed(questions)
        for idx, question in enumerate(questions):
            q_emb = q_emb_list[idx]
            if knowledge_base.exists_like_q(q_emb):
                print(f"Skip: {question}")
                continue
            knowledge = generate_knowledge_from_question(
                question,
                tale,
                knowledge_base,
                answer_writer,
                time_indicator,
                q_emb,
                all_details,
            )
            if len(knowledge.chapter_idx) > 0:
                knowledge_base.add_knowledge(knowledge)
            yield knowledge


def match_knowledge_chapter_idx(
    knowledge: Knowledge,
    tale: Tale,
    time_indicator: TaleTimeIndicatorWriter,
    exceed_threshold: int = 4,
) -> None:

    print("Matching: ", knowledge.qa.问题, knowledge.qa.答案)
    # print(knowledge.qa.问题, knowledge.qa.答案)
    ids: List[int] = time_indicator.invoke(
        tale.all_details(with_idx=True), struct_to_builtin(knowledge.qa)
    )
    if len(ids) > exceed_threshold and not knowledge.important:
        print(f"Exceed threshold: {len(ids)}")
        return
    for id in ids:
        print(id, ". ", tale.get_detail(id))
    chapter_ids = [tale.get_chapter_idx_by_detail_idx(i) for i in ids]
    knowledge.chapter_idx = list(set(chapter_ids))


def match_all_knowledge_chapter_idx(
    knowledge_base: KnowledgeBase,
    tale: Tale,
    time_indicator: TaleTimeIndicatorWriter,
    exceed_threshold: int = 4,
) -> None:
    for knowledge in knowledge_base.knowledges:
        match_knowledge_chapter_idx(knowledge, tale, time_indicator, exceed_threshold)
    return knowledge_base


def composite_chapter(
    chapter_idx: int,
    completion_writer: TaleCompletionWriter,
    summary_writer: TaleSummaryWriter,
    tale: Tale,
    qa_group_by_chapter: List[List[QAPair]],
):
    i = chapter_idx
    chapter = tale.CHAPTERS[i]
    num_chapters = len(tale.CHAPTERS)

    theme = chapter.NAME
    details = chapter.DETAILS
    is_last_chapter = i == num_chapters - 1
    next_details = tale.CHAPTERS[i + 1].DETAILS if not is_last_chapter else None

    current_content = completion_writer.invoke(
        related_qa=struct_to_builtin(qa_group_by_chapter[i]),
        current_chapter_theme=theme,
        current_chapter=details,
        previous_content=(
            "\n".join([(x.SUMMARY or "") for x in tale.CHAPTERS[:i]]) if i > 0 else ""
        ),
        next_chapter=next_details,
        is_last_chapter=is_last_chapter,
    )
    current_content = current_content.split("\n")
    current_content = "\n".join(current_content[:-1])
    summary = summary_writer.invoke(current_content)
    chapter.CONTENT = current_content
    chapter.SUMMARY = summary
    print(current_content)


def composite_tale(
    completion_writer: TaleCompletionWriter,
    summary_writer: TaleSummaryWriter,
    tale: Tale,
    knowledge_base: KnowledgeBase,
) -> None:
    num_chapters = len(tale.CHAPTERS)
    qa_group_by_chapter = [
        [knowledge.qa for knowledge in chapter_group]
        for chapter_group in knowledge_base.get_knowleges_group_by_chapter()
    ]
    for i, _chapter in enumerate(tale.CHAPTERS):
        composite_chapter(
            i,
            completion_writer,
            summary_writer,
            tale,
            knowledge_base,
            num_chapters,
            qa_group_by_chapter,
        )
