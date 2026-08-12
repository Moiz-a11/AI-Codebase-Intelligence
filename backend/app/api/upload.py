# Repository upload endpoints will go here.
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import zipfile
import shutil
import uuid

router = APIRouter(prefix="/api", tags=["Repository"])

BASE_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
REPOSITORY_DIR = BASE_DIR / "data" / "repositories"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
REPOSITORY_DIR.mkdir(parents=True, exist_ok=True)

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

IGNORED_DIRECTORIES = {
    "node_modules",
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
}


def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """
    Prevent ZIP path traversal attacks.
    """
    try:
        target_path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False


def should_include_file(file_path: Path) -> bool:
    """
    Check whether a file should be included in code analysis.
    """

    if any(part in IGNORED_DIRECTORIES for part in file_path.parts):
        return False

    return file_path.suffix.lower() in ALLOWED_EXTENSIONS


@router.post("/upload")
async def upload_repository(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file selected."
        )

    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=400,
            detail="Only ZIP repositories are supported."
        )

    repository_id = str(uuid.uuid4())

    zip_path = UPLOAD_DIR / f"{repository_id}.zip"
    repository_path = REPOSITORY_DIR / repository_id

    try:

        # Save uploaded ZIP
        with open(zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Create repository directory
        repository_path.mkdir(
            parents=True,
            exist_ok=True
        )

        # Validate ZIP
        if not zipfile.is_zipfile(zip_path):
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is not a valid ZIP archive."
            )

        # Extract safely
        with zipfile.ZipFile(zip_path, "r") as zip_ref:

            for member in zip_ref.infolist():

                target_path = repository_path / member.filename

                if not is_safe_path(
                    repository_path,
                    target_path
                ):
                    raise HTTPException(
                        status_code=400,
                        detail="Unsafe ZIP file detected."
                    )

            zip_ref.extractall(repository_path)

        # Find source files
        source_files = []

        for path in repository_path.rglob("*"):

            if path.is_file() and should_include_file(path):

                relative_path = path.relative_to(
                    repository_path
                )

                source_files.append(
                    str(relative_path)
                )

        return {
            "success": True,
            "repository_id": repository_id,
            "filename": file.filename,
            "message": "Repository uploaded successfully.",
            "total_source_files": len(source_files),
            "files": source_files[:100],
        }

    except HTTPException:
        if repository_path.exists():
            shutil.rmtree(repository_path)

        if zip_path.exists():
            zip_path.unlink()

        raise

    except Exception as error:

        if repository_path.exists():
            shutil.rmtree(repository_path)

        if zip_path.exists():
            zip_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Repository processing failed: {str(error)}"
        )