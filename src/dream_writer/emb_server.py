from typing import List

from llmspec import EmbeddingData, EmbeddingRequest, EmbeddingResponse, TokenUsage
from mosec import ClientError, Runtime, Server, Worker
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "intfloat/multilingual-e5-large"


class Embedding(Worker):
    def __init__(self):
        self.model_name = "intfloat/multilingual-e5-large"
        self.model = SentenceTransformer(DEFAULT_MODEL)

    def deserialize(self, req: bytes) -> EmbeddingRequest:
        return EmbeddingRequest.from_bytes(req)

    def serialize(self, resp: EmbeddingResponse) -> bytes:
        return resp.to_json()

    def forward(self, req: EmbeddingRequest) -> EmbeddingResponse:
        if req.model != self.model_name:
            raise ClientError(
                f"the requested model {req.model} is not supported by "
                f"this worker {self.model_name}"
            )
        if isinstance(req.input, str):
            input_texts = [req.input]
        elif isinstance(req.input, list) and isinstance(req.input[0], str):
            input_texts = req.input
        else:
            raise NotImplementedError("Input a list of tokens is not supported")

        embeddings: List[List[float]] = self.model.encode(
            input_texts, normalize_embeddings=True
        ).tolist()

        resp = EmbeddingResponse(
            data=[
                EmbeddingData(embedding=emb, index=i)
                for i, emb in enumerate(embeddings)
            ],
            model=self.model_name,
            usage=TokenUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
            ),
        )
        return resp


if __name__ == "__main__":
    server = Server()
    emb = Runtime(Embedding)
    server.register_runtime(
        {
            "/v1/embeddings": [emb],
            "/embeddings": [emb],
        }
    )
    server.run()
