from pathlib import Path

import chromadb

from app.rag.embeddings import EmbeddingService


BASE_DIR = Path(__file__).resolve().parents[3]

CHROMA_PATH = BASE_DIR / "data" / "chroma"

CHROMA_PATH.mkdir(
    parents=True,
    exist_ok=True
)


class VectorStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_PATH)
        )

        # Shared embedding model
        self.embedding_service = EmbeddingService()

    def get_collection(
        self,
        repository_id: str
    ):

        collection_name = (
            "repo_"
            + repository_id.replace("-", "_")
        )

        return self.client.get_or_create_collection(
            name=collection_name
        )

    def add_chunks(
        self,
        repository_id: str,
        chunks: list,
    ):

        if not chunks:
            return 0

        collection = self.get_collection(
            repository_id
        )

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "file_path": chunk["file_path"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
            }
            for chunk in chunks
        ]

        ids = [
            f"{repository_id}_{index}"
            for index in range(len(chunks))
        ]

        embeddings = (
            self.embedding_service
            .embed_documents(documents)
        )

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return len(chunks)

    def search(
        self,
        repository_id: str,
        query: str,
        top_k: int = 5,
    ):

        collection = self.get_collection(
            repository_id
        )

        query_embedding = (
            self.embedding_service
            .embed_query(query)
        )

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        return results