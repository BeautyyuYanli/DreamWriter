from dream_writer.tale.pipeline import (
    composite_tale,
    generate_knowledge_base_from_outline,
    generate_outline,
    match_all_knowledge_chapter_idx,
)
from dream_writer.tale.writers import (
    TaleAnswerWriter,
    TaleCompletionWriter,
    TaleOutlineWriter,
    TaleQuestionWriter,
    TaleSummaryWriter,
    TaleTimeIndicatorWriter,
)
from dream_writer.utils import struct_to_yaml

outline_writer = TaleOutlineWriter()
question_writer = TaleQuestionWriter()
answer_writer = TaleAnswerWriter()
summary_writer = TaleSummaryWriter()
time_indicator = TaleTimeIndicatorWriter()
completion_writer = TaleCompletionWriter()

knowledge_base, tale = generate_outline(
    outline_writer, "一个探险者和一个人工智能在末日后重建世界的故事"
)
match_all_knowledge_chapter_idx(knowledge_base, tale, time_indicator)

with open("src/dream_writer/tale/pre_tale.yaml", "w") as f:
    f.write(struct_to_yaml(tale))
with open("src/dream_writer/tale/pre_knowledge.json", "wb") as f:
    f.write(knowledge_base.to_json())

# with open("src/dream_writer/tale/pre_tale.yaml", "r") as f:
#     tale: Tale = yaml_to_struct(f.read(), Tale)
# with open("src/dream_writer/tale/pre_knowledge.json", "rb") as f:
#     knowledge_base: KnowledgeBase = KnowledgeBase.from_json(f.read())


for _ in generate_knowledge_base_from_outline(
    knowledge_base,
    tale,
    question_writer,
    answer_writer,
    time_indicator,
):
    pass

with open("src/dream_writer/tale/knowledge.json", "wb") as f:
    f.write(knowledge_base.to_json())


# with open("src/dream_writer/tale/pre_tale.yaml", "r") as f:
#     tale: Tale = yaml_to_struct(f.read(), Tale)
# with open("src/dream_writer/tale/knowledge.json", "rb") as f:
#     knowledge_base: KnowledgeBase = KnowledgeBase.from_json(f.read())

composite_tale(completion_writer, summary_writer, tale, knowledge_base)

with open("src/dream_writer/tale/tale.yaml", "w") as f:
    f.write(struct_to_yaml(tale))

with open("src/dream_writer/tale/output.txt", "w") as f:
    f.write(tale.to_completed_text())
