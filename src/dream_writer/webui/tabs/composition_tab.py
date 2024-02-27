from typing import Optional

import streamlit as st

from dream_writer.tale.pipeline import (
    composite_chapter,
)
from dream_writer.tale.structs import KnowledgeBase, Tale
from dream_writer.webui.resource import (
    completion_writer,
    summary_writer,
)


def composition_tab():
    knowledge_base: KnowledgeBase = st.session_state["knowledge_base"]
    tale: Tale = st.session_state["tale"]
    num_chapters = len(tale.CHAPTERS)
    qa_group_by_chapter = [
        [knowledge.qa for knowledge in chapter_group]
        for chapter_group in knowledge_base.get_knowleges_group_by_chapter()
    ]
    while len(qa_group_by_chapter) < num_chapters:
        qa_group_by_chapter.append([])

    for i, chapter in enumerate(tale.CHAPTERS):
        st.caption(f"{chapter.NAME}")
        st.write("- " + "\n- ".join(chapter.DETAILS))

        placeholder = st.empty()
        st.caption("*Click 'Save Edition' if you modify the content")

        row = st.columns([1, 1])
        with row[0]:
            if st.button("Generate Content", key=f"generate_{chapter.NAME}"):
                with st.spinner(f"Generating Content for {chapter.NAME}"):
                    composite_chapter(
                        i,
                        completion_writer,
                        summary_writer,
                        tale,
                        qa_group_by_chapter,
                    )

        new_content: Optional[str] = None
        if chapter.CONTENT is not None:
            with placeholder:
                new_content = st.text_area(
                    f"{chapter.NAME} Content",
                    value=chapter.CONTENT,
                    height=300,
                    key=f"content_{chapter.NAME}",
                    label_visibility="collapsed",
                )

        with row[1]:
            if st.button(
                "Save Edition",
                key=f"save_{chapter.NAME}",
            ):
                with st.spinner(f"Generate Summary for {chapter.NAME}"):
                    chapter.CONTENT = new_content
                    chapter.SUMMARY = summary_writer.invoke(new_content)
                    st.toast(f"Content for {chapter.NAME} saved")
        st.divider()

    with st.expander("Full Tale", expanded=True):
        st.write(
            "\n\n".join(
                [
                    (chapter.CONTENT or "").replace(
                        "\n",
                        "\n\n",
                    )
                    for chapter in tale.CHAPTERS
                ]
            )
        )
