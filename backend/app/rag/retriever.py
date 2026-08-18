# Relevant-code retrieval.

from app.rag.vector_store import VectorStore
from app.rag.reranker import CodeReranker


# Files/directories that usually don't contain
# useful application logic.
IGNORED_NAMES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb",
    "composer.lock",
    "poetry.lock",
}


IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".next",
    ".cache",
}


class CodeRetriever:

    def __init__(self):

        self.vector_store = VectorStore()

        self.reranker = CodeReranker()


    # ==========================================
    # FILE RELEVANCE FILTER
    # ==========================================

    def _is_relevant_file(
        self,
        file_path: str,
    ):

        normalized_path = (
            file_path
            .replace("\\", "/")
            .lower()
        )

        file_name = (
            normalized_path
            .split("/")[-1]
        )


        # Ignore lock files
        if file_name in IGNORED_NAMES:
            return False


        # Ignore generated/dependency directories
        path_parts = set(
            normalized_path.split("/")
        )

        if path_parts.intersection(
            IGNORED_DIRECTORIES
        ):
            return False


        return True


    # ==========================================
    # RETRIEVE + FILTER + RERANK
    # ==========================================

    def retrieve(
        self,
        repository_id: str,
        query: str,
        top_k: int = 5,
    ):

        # ------------------------------------------
        # STEP 1
        # Retrieve more candidates than needed.
        # ------------------------------------------

        candidate_k = max(
            top_k * 3,
            15
        )


        results = self.vector_store.search(
            repository_id=repository_id,
            query=query,
            top_k=candidate_k,
        )


        # ------------------------------------------
        # STEP 2
        # Extract ChromaDB results.
        # ------------------------------------------

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


        # ------------------------------------------
        # STEP 3
        # Convert ChromaDB results into
        # our standard format.
        # ------------------------------------------

        for index, document in enumerate(
            documents
        ):

            metadata = (
                metadatas[index]
                if index < len(metadatas)
                else {}
            )

            distance = (
                distances[index]
                if index < len(distances)
                else None
            )


            file_path = metadata.get(
                "file_path",
                ""
            )


            # --------------------------------------
            # FILE FILTER
            # --------------------------------------

            if not self._is_relevant_file(
                file_path
            ):
                continue


            retrieved_chunks.append(
                {
                    "text": document,

                    "file_path": file_path,

                    "start_line": metadata.get(
                        "start_line"
                    ),

                    "end_line": metadata.get(
                        "end_line"
                    ),

                    "distance": distance,
                }
            )


        # ------------------------------------------
        # No relevant results
        # ------------------------------------------

        if not retrieved_chunks:

            print(
                "No relevant code chunks found."
            )

            return []


        # ------------------------------------------
        # STEP 4
        # Cross-encoder reranking
        # ------------------------------------------

        final_results = (
            self.reranker.rerank(
                query=query,
                results=retrieved_chunks,
                top_k=top_k,
            )
        )


        # ------------------------------------------
        # STEP 5
        # Debug information
        # ------------------------------------------

        print(
            "\n========== RAG RETRIEVAL =========="
        )

        print(
            f"Query: {query}"
        )

        print(
            f"Initial candidates: "
            f"{len(documents)}"
        )

        print(
            f"After filtering: "
            f"{len(retrieved_chunks)}"
        )

        print(
            f"Final results: "
            f"{len(final_results)}"
        )


        for index, result in enumerate(
            final_results
        ):

            score = result.get(
                "rerank_score",
                0
            )

            print(
                f"{index + 1}. "
                f"{result['file_path']} "
                f"(rerank score: "
                f"{score:.4f})"
            )


        print(
            "==================================\n"
        )


        return final_results