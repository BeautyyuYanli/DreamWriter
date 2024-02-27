import os
import uuid
from typing import Any, List, Optional, Union

import msgspec
import numpy as np
import openai
from msgspec import Struct
from proteus import (
    LLMsConfig,
    ProteusMessagePrompt,
    ProteusTeller,
    history_store,
    llm_from_config,
)


class TrivalWriter(ProteusTeller):
    def __init__(self, prompt: ProteusMessagePrompt, temperature: float = 0.9):
        llm = llm_from_config(
            config=LLMsConfig(
                gemini=LLMsConfig.GeminiConfig(
                    generation_config={"temperature": temperature}
                )
            )
        )
        super().__init__(
            id=str(uuid.uuid4()),
            llm=llm,
            prompt=prompt,
            history=history_store.MemoryHistoryStore(),
            live_history_size=10,
            save_history=False,
        )

    def write_yaml(
        self,
        idea: Union[str, dict, list],
        structType: Any,
        retry: Optional[int] = None,
    ) -> Optional[msgspec.Struct]:
        cnt = 0
        while retry is None or cnt <= retry:
            try:
                ans = self.say_with_template(idea or "", "default")
                return yaml_to_struct(yaml_preprocess(ans), structType)
            except Exception:
                cnt += 1
                print(f"DEBUG: failed {cnt} times when writing yaml")
        return None


def yaml_preprocess(text: str) -> str:
    return text.strip().removeprefix("```yaml").removeprefix("```").removesuffix("```")


def yaml_to_builtin(text: str) -> dict:
    return msgspec.yaml.decode(text)


def builtin_to_yaml(data: dict) -> str:
    return msgspec.yaml.encode(data).decode()


def struct_to_yaml(struct: Any) -> str:
    return msgspec.yaml.encode(msgspec.to_builtins(struct)).decode()


def yaml_to_struct(text: str, structType: Any) -> Any:
    return msgspec.convert(msgspec.yaml.decode(text), structType)


def struct_to_builtin(struct: Any) -> dict:
    return msgspec.to_builtins(struct)


def builtin_to_struct(data: dict, structType: Any) -> Any:
    return msgspec.convert(data, structType)


if os.getenv("EMBEDDING_SERVICE_BASE", None):
    emb_openai = openai.OpenAI(
        base_url=os.getenv("EMBEDDING_SERVICE_BASE"),
        api_key="NOT_SET",
    )
else:
    emb_openai = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "NOT_SET"))


def embed(texts: List[str]) -> List[np.ndarray]:
    while True:
        res = emb_openai.embeddings.create(
            input=texts,
            model=(
                os.getenv("EMBEDDING_SERVICE_MODEL")
                if os.getenv("EMBEDDING_SERVICE_BASE", None)
                else "text-embedding-3-small"
            ),
        ).data
        break
    embeddings = [np.array(i.embedding) for i in res]
    return embeddings


class QAPair(Struct, kw_only=True, frozen=True):
    问题: str = "问题"
    答案: str
