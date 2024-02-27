import streamlit as st

from dream_writer.tale.writers import (
    TaleAnswerWriter,
    TaleCompletionWriter,
    TaleOutlineWriter,
    TaleQuestionWriter,
    TaleSummaryWriter,
    TaleTimeIndicatorWriter,
)


@st.cache_resource
def get_writers():
    writers = (
        TaleOutlineWriter(),
        TaleAnswerWriter(),
        TaleTimeIndicatorWriter(),
        TaleCompletionWriter(),
        TaleSummaryWriter(),
        TaleQuestionWriter(),
    )
    return writers


(
    outline_writer,
    answer_writer,
    time_indicator,
    completion_writer,
    summary_writer,
    question_writer,
) = get_writers()
