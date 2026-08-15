from sentence_transformers import SentenceTransformer


MODEL_NAME = "BAAI/bge-base-en-v1.5"


class EmbeddingService:
    _instance = None

    def __new__(cls):
        """
        Create only one EmbeddingService instance.
        """

        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        # Prevent loading the model more than once
        if getattr(self, "_initialized", False):
            return

        print(
            f"Loading embedding model: {MODEL_NAME}"
        )

        self.model = SentenceTransformer(
            MODEL_NAME
        )

        self._initialized = True

        print(
            "Embedding model loaded successfully."
        )

    def embed_documents(self, texts):

        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=16,
        )

        return embeddings.tolist()

    def embed_query(self, query):

        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
        )

        return embedding.tolist()