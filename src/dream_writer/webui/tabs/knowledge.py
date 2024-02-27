from copy import deepcopy

import streamlit as st

from dream_writer.tale.pipeline import (
    generate_knowledge_base_from_outline,
)
from dream_writer.tale.structs import KnowledgeBase, Tale
from dream_writer.webui.resource import (
    answer_writer,
    question_writer,
    time_indicator,
)


def pop_knowledge(i: int, chapter_idx: int):
    knowledge_base: KnowledgeBase = st.session_state["knowledge_base"]
    knowledge_base.knowledges[i].chapter_idx.remove(chapter_idx)


def knowledge_tab():
    knowledge_base: KnowledgeBase = st.session_state["knowledge_base"]
    tale: Tale = st.session_state["tale"]

    if "knowledge_generated" not in st.session_state:

        def set_clicked():
            st.session_state["knowledge_generated"] = False

        st.button(
            "Generate Knowledge Base",
            type="primary",
            on_click=set_clicked,
        )

    if st.session_state.get("knowledge_generated", None) is False:
        st.session_state.pop("knowledge_generated")
        new_knowledge_base = deepcopy(knowledge_base)
        with st.status("Generating... Don't interrupt!!!", expanded=True) as status:
            progress_bar = st.progress(0)
            len_total = len(tale.all_details()) * 3
            for cnt, knowledge in enumerate(
                generate_knowledge_base_from_outline(
                    new_knowledge_base,
                    tale,
                    question_writer,
                    answer_writer,
                    time_indicator,
                )
            ):
                st.write(knowledge.qa)
                progress_bar.progress(cnt / len_total)
            status.success("Knowledge Base Generated")
            progress_bar.progress(1)
        knowledge_base = new_knowledge_base
        st.session_state["knowledge_base"] = knowledge_base
        st.session_state["knowledge_generated"] = True

    chapter_view, item_view = st.tabs(["By Chapter", "By Item"])
    st.write(
        """<style>
        [data-testid="stHorizontalBlock"] {
            align-items: end;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with item_view:
        for i, item in enumerate(knowledge_base.knowledges):
            row = st.columns([4, 1])
            with row[0]:
                st.caption(f"{i}. {item.qa.问题}")
                st.write(item.qa.答案)
                with st.expander("Matched Chapters"):
                    for idx in item.chapter_idx:
                        chapter = tale.get_chapter(idx)
                        st.write(
                            {
                                "chapter": chapter.NAME,
                                "details": chapter.DETAILS,
                            }
                        )
            with row[1]:
                st.button(
                    "Delete",
                    key=f"knowledge_delete_{i}",
                    on_click=pop_knowledge,
                    args=(i,),
                ),
            st.divider()

    with chapter_view:
        chapter_knowledges = knowledge_base.get_knowleges_group_by_chapter()

        for idx in range(len(chapter_knowledges)):
            chapter = tale.get_chapter(idx)
            st.caption(f"{chapter.NAME}")
            st.write("- " + "\n- ".join(chapter.DETAILS))
            with st.expander("Matched QA", expanded=True):
                for i, item in enumerate(chapter_knowledges[idx]):
                    row = st.columns([4, 1])
                    with row[0]:
                        st.caption(f"Q: {item.qa.问题}")
                        st.write(f"{item.qa.答案}")
                    with row[1]:
                        # to_edit = st.button(
                        #     "Edit",
                        #     key=f"knowledge_edit_{idx}_{i}",
                        # )
                        st.button(
                            "Delete",
                            key=f"knowledge_delete_1_{idx}_{i}",
                            on_click=pop_knowledge,
                            args=(knowledge_base.knowledges.index(item), idx),
                        )

                    # if to_edit:
                    #     with st.form(
                    #         key=f"knowledge_edit_{idx}_{i}_form", border=False
                    #     ):
                    #         q = st.text_input("Question", item.qa.问题)
                    #         a = st.text_input("Answer", item.qa.答案)

                    #         def save_edit(knowledge: Knowledge, q: str, a: str):
                    #             knowledge.qa = QAPair(问题=q, 答案=a)

                    #         st.form_submit_button(
                    #             "Save", on_click=save_edit, args=(item, q, a)
                    #         )
                    #         st.form_submit_button("Cancel")

                    st.divider()

    if st.session_state.get("knowledge_generated", None) is True:

        def set_next_tab():
            st.session_state["tab"] = "Composition"

        st.button("Next Step", type="primary", key="next", on_click=set_next_tab)
