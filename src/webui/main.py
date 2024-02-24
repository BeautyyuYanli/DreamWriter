import streamlit as st
import streamlit_shadcn_ui as ui

from webui.tabs import composition_tab, knowledge_tab, outline_tab

tab = ui.tabs(
    ["Outline", "Knowledge", "Composition"],
    default_value="Outline",
    key="tab",
)

if tab == "Outline":
    outline_tab()

if tab == "Knowledge":
    if "tale" not in st.session_state or "knowledge_base" not in st.session_state:
        st.write("Please generate outline first.")
    knowledge_tab()


if tab == "Composition":
    if "tale" not in st.session_state or "knowledge_base" not in st.session_state:
        st.write("Please generate outline first.")
    composition_tab()
