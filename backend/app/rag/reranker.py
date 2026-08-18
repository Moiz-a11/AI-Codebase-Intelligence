# Optional BGE reranker integration.
from sentence_transformers import CrossEncoder


class CodeReranker:

    def __init__(self):

        print(
            "Loading reranking model..."
        )

        self.model = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

        print(
            "Reranking model loaded."
        )

    def rerank(
        self,
        query: str,
        results: list,
        top_k: int = 5,
    ):

        if not results:
            return []

        pairs = []

        for result in results:

            pairs.append(
                (
                    query,
                    result["text"]
                )
            )

        scores = self.model.predict(
            pairs
        )

        scored_results = []

        for result, score in zip(
            results,
            scores
        ):

            result_copy = result.copy()

            result_copy["rerank_score"] = float(
                score
            )

            scored_results.append(
                result_copy
            )

        scored_results.sort(
            key=lambda item:
                item["rerank_score"],
            reverse=True
        )

        return scored_results[:top_k]