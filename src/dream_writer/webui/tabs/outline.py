import streamlit as st
from streamlit_ace import st_ace

from dream_writer.tale.pipeline import (
    match_all_knowledge_chapter_idx,
)
from dream_writer.tale.structs import KnowledgeBase, Tale
from dream_writer.tale.writers import (
    Outline,
)
from dream_writer.utils import (
    struct_to_yaml,
    yaml_to_struct,
)
from dream_writer.webui.resource import (
    outline_writer,
    time_indicator,
)


def outline_tab():
    with st.form(key="form_outline"):
        insight = st.text_input(
            "Insight", "一个探险者和一个人工智能在末日后重建世界的故事"
        )
        gen_button = st.form_submit_button("Generate Outline")

        if gen_button:
            with st.spinner("Generating..."):
                st.session_state["outline"] = outline_writer.invoke(insight)
        if "outline" in st.session_state:
            outline: Outline = st.session_state["outline"]
            edited_outline_str = st_ace(
                struct_to_yaml(outline),
                language="yaml",
                theme="tomorrow_night",
                auto_update=True,
            )
            submit_buttom = st.form_submit_button("Save and Init")
            if submit_buttom:
                edited_outline: Outline = yaml_to_struct(edited_outline_str, Outline)
                st.session_state["outline"] = edited_outline
                with st.spinner("Initializing Knowledge Base..."):
                    tale = Tale.from_outline(edited_outline)
                    knowledge_base = KnowledgeBase.from_outline(edited_outline)

                    print("start matching")
                    # print("Matching: ", knowledge.qa.问题, knowledge.qa.答案)
                    match_all_knowledge_chapter_idx(
                        knowledge_base, tale, time_indicator
                    )
                    st.session_state["tale"] = tale
                    st.session_state["knowledge_base"] = knowledge_base
                    if "knowledge_generated" in st.session_state:
                        st.session_state.pop("knowledge_generated")

            if "knowledge_base" in st.session_state:

                def set_tab():
                    st.session_state["tab"] = "Knowledge"

                st.form_submit_button("Next Step", type="primary", on_click=set_tab)
