from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import zipfile
import shutil
import uuid

from app.services.rag_service import RAGService


router = APIRouter(
    prefix="/api",
    tags=["Repository"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
REPOSITORY_DIR = BASE_DIR / "data" / "repositories"


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

REPOSITORY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# SUPPORTED CODE FILES
# ============================================================

ALLOWED_EXTENSIONS = {
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


# ============================================================
# DIRECTORIES TO IGNORE
# ============================================================

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


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def is_safe_path(
    base_path: Path,
    target_path: Path
) -> bool:
    """
    Prevent ZIP path traversal attacks.
    """

    try:

        target_path.resolve().relative_to(
            base_path.resolve()
        )

        return True

    except ValueError:

        return False


def should_include_file(
    file_path: Path
) -> bool:
    """
    Check whether a file should be included
    in codebase analysis.
    """

    # Ignore unwanted directories
    if any(
        directory in file_path.parts
        for directory in IGNORED_DIRECTORIES
    ):
        return False

    # Check extension
    return (
        file_path.suffix.lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# UPLOAD REPOSITORY
# ============================================================

@router.post("/upload")
async def upload_repository(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )


    # --------------------------------------------------------
    # Validate ZIP extension
    # --------------------------------------------------------

    if not file.filename.lower().endswith(".zip"):

        raise HTTPException(
            status_code=400,
            detail="Only ZIP files are supported."
        )


    # --------------------------------------------------------
    # Generate repository ID
    # --------------------------------------------------------

    repository_id = str(
        uuid.uuid4()
    )


    zip_path = (
        UPLOAD_DIR
        / f"{repository_id}.zip"
    )

    repository_path = (
        REPOSITORY_DIR
        / repository_id
    )


    try:

        # ====================================================
        # STEP 1 — SAVE ZIP
        # ====================================================

        with open(
            zip_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )


        # ====================================================
        # STEP 2 — VALIDATE ZIP
        # ====================================================

        if not zipfile.is_zipfile(
            zip_path
        ):

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid ZIP archive."
            )


        # ====================================================
        # STEP 3 — CREATE REPOSITORY DIRECTORY
        # ====================================================

        repository_path.mkdir(
            parents=True,
            exist_ok=True
        )


        # ====================================================
        # STEP 4 — CHECK ZIP PATHS
        # ====================================================

        with zipfile.ZipFile(
            zip_path,
            "r"
        ) as zip_ref:

            for member in zip_ref.infolist():

                target_path = (
                    repository_path
                    / member.filename
                )

                if not is_safe_path(
                    repository_path,
                    target_path
                ):

                    raise HTTPException(
                        status_code=400,
                        detail="Unsafe ZIP file detected."
                    )


            # =================================================
            # STEP 5 — EXTRACT ZIP
            # =================================================

            zip_ref.extractall(
                repository_path
            )


        # ====================================================
        # STEP 6 — FIND SOURCE FILES
        # ====================================================

        source_files = []

        for path in repository_path.rglob("*"):

            if not path.is_file():
                continue

            if should_include_file(path):

                relative_path = (
                    path.relative_to(
                        repository_path
                    )
                )

                source_files.append(
                    str(relative_path)
                )


        # ====================================================
        # STEP 7 — CHECK REPOSITORY
        # ====================================================

        if not source_files:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No supported source code files "
                    "were found in the repository."
                )
            )


        # ====================================================
        # STEP 8 — INDEX REPOSITORY INTO RAG
        # ====================================================

        print(
            f"Starting RAG indexing for "
            f"{repository_id}..."
        )

        rag_service = RAGService()

        rag_result = (
            rag_service.index_repository(
                repository_id=repository_id
            )
        )


        print(
            f"RAG indexing completed. "
            f"Files: {rag_result['files_processed']}, "
            f"Chunks: {rag_result['chunks_created']}"
        )


        # ====================================================
        # STEP 9 — SUCCESS RESPONSE
        # ====================================================

        return {

            "success": True,

            "repository_id":
                repository_id,

            "filename":
                file.filename,

            "message":
                "Repository uploaded and indexed successfully.",

            "total_source_files":
                len(source_files),

            "files_processed":
                rag_result[
                    "files_processed"
                ],

            "chunks_created":
                rag_result[
                    "chunks_created"
                ],

            "files":
                source_files[:100],
        }


    # ========================================================
    # HANDLE HTTP ERRORS
    # ========================================================

    except HTTPException:

        if repository_path.exists():

            shutil.rmtree(
                repository_path
            )

        if zip_path.exists():

            zip_path.unlink()

        raise


    # ========================================================
    # HANDLE OTHER ERRORS
    # ========================================================

    except Exception as error:

        print(
            f"Repository processing error: "
            f"{error}"
        )


        if repository_path.exists():

            shutil.rmtree(
                repository_path
            )


        if zip_path.exists():

            zip_path.unlink()


        raise HTTPException(
            status_code=500,
            detail=(
                "Repository processing failed: "
                f"{str(error)}"
            )
        )