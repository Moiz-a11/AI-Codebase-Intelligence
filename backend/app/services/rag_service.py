from pathlib import Path

from app.rag.chunker import chunk_code
from app.rag.vector_store import VectorStore


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".html",
    ".css",
    ".scss",
    ".json",
    ".xml",
    ".sql",
    ".go",
    ".rs",
    ".php",
    ".rb",
}


IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}


class RAGService:

    def __init__(self):

        self.vector_store = VectorStore()

    def index_repository(
        self,
        repository_id: str,
    ):

        base_dir = (
            Path(__file__)
            .resolve()
            .parents[3]
        )

        repository_path = (
            base_dir
            / "data"
            / "repositories"
            / repository_id
        )

        if not repository_path.exists():

            raise FileNotFoundError(
                "Repository not found."
            )

        all_chunks = []

        processed_files = set()

        for file_path in repository_path.rglob("*"):

            if not file_path.is_file():
                continue

            if any(
                directory in file_path.parts
                for directory in IGNORED_DIRECTORIES
            ):
                continue

            if (
                file_path.suffix.lower()
                not in SUPPORTED_EXTENSIONS
            ):
                continue

            try:

                code = file_path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                relative_path = (
                    file_path.relative_to(
                        repository_path
                    )
                )

                chunks = chunk_code(
                    code=code,
                    file_path=str(relative_path),
                )

                if chunks:

                    processed_files.add(
                        str(relative_path)
                    )

                    all_chunks.extend(chunks)

            except Exception as error:

                print(
                    f"Skipping {file_path}: {error}"
                )

        chunks_created = (
            self.vector_store.add_chunks(
                repository_id=repository_id,
                chunks=all_chunks,
            )
        )

        return {
            "repository_id": repository_id,
            "files_processed": len(
                processed_files
            ),
            "chunks_created": chunks_created,
        }