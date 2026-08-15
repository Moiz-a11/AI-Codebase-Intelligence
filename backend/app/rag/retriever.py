# Relevant-code retrieval.
from app.rag.vector_store import VectorStore


class CodeRetriever:

    def __init__(self):

        self.vector_store = VectorStore()

    def retrieve(
        self,
        repository_id: str,
        query: str,
        top_k: int = 5,
    ):

        results = self.vector_store.search(
            repository_id=repository_id,
            query=query,
            top_k=top_k,
        )

        documents = results.get(
            "documents",
            [[]]
        )[0]

        metadatas = results.get(
            "metadatas",
            [[]]
        )[0]

        distances = results.get(
            "distances",
            [[]]
        )[0]

        retrieved_chunks = []

        for index, document in enumerate(documents):

            metadata = metadatas[index]

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )

            retrieved_chunks.append(
                {
                    "text": document,
                    "file_path": metadata.get(
                        "file_path"
                    ),
                    "start_line": metadata.get(
                        "start_line"
                    ),
                    "end_line": metadata.get(
                        "end_line"
                    ),
                    "distance": distance,
                }
            )

        return retrieved_chunks