from requests import request

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.rag.retriever import CodeRetriever
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService


router = APIRouter(
    prefix="/api/rag",
    tags=["RAG"],
)


class IndexRequest(BaseModel):

    repository_id: str


class QueryRequest(BaseModel):

    repository_id: str

    question: str = Field(
        min_length=1
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
    )
    review_mode: bool = False
    review_category: str = "general"


rag_service = RAGService()

retriever = CodeRetriever()

llm_service = LLMService()


@router.post("/index")
def index_repository(request: IndexRequest):

    try:

        if not request.repository_id.strip():
            raise HTTPException(
                status_code=400,
                detail="Repository ID is missing."
            )

        result = rag_service.index_repository(
            request.repository_id
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail="The repository is empty. "
                       "Please upload a repository containing code files."
            )

        return {
            "success": True,
            **result
        }

    except HTTPException:
        raise

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Repository not found. "
                   "Please upload the repository again."
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        print(f"Repository indexing error: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to index the repository. "
                "Please try uploading the repository again."
            )
        )

@router.post("/query")
def query_repository(
    request: QueryRequest
):

    try:

        if not request.repository_id.strip():

            raise HTTPException(
                status_code=400,
                detail="Please upload a repository first.",
            )

        if not request.question.strip():

            raise HTTPException(
                status_code=400,
                detail="Please enter a question.",
            )

        # ==========================================
        # STEP 1 — RETRIEVE RELEVANT CODE
        # ==========================================

        results = retriever.retrieve(
            repository_id=request.repository_id,
            query=request.question,
            top_k=request.top_k,
        )


        # ==========================================
        # STEP 2 — BUILD CONTEXT
        # ==========================================

        context_parts = []

        for index, result in enumerate(results):

            context_parts.append(
                f"""
SOURCE {index + 1}

FILE:
{result["file_path"]}

LINES:
{result["start_line"]}-{result["end_line"]}

CODE:
{result["text"]}
"""
            )

        context = "\n".join(
            context_parts
        )


        # ==========================================
        # STEP 3 — SEND CONTEXT TO QWEN
        # ==========================================

        answer = llm_service.generate(
            question=request.question,
            context=context,
            review_mode=request.review_mode,
            review_category=request.review_category,
        )

        # ==========================================
        # STEP 3.5 — BUILD SOURCE CITATIONS
        # ==========================================

        sources = []

        for result in results:

            sources.append({
            "file_path": result.get("file_path"),
            "start_line": result.get("start_line"),
            "end_line": result.get("end_line"),
            "rerank_score": result.get("rerank_score"),
            })


        # ==========================================
        # STEP 4 — RETURN ANSWER + SOURCES
        # ==========================================

        return {
        "success": True,
        "question": request.question,
        "answer": answer,
        "sources": sources,
        "results": results,
        }

    except HTTPException:
        raise

    except RuntimeError as error:
        message = str(error)

        print(f"RAG/LLM error: {message}")

        # Ollama unavailable
        if (
            "Ollama" in message
            or "AI service" in message
            or "connect" in message.lower()
        ):
            raise HTTPException(
                status_code=503,
                detail=message,
            )

        # LLM timeout
        if "too long" in message.lower():
            raise HTTPException(
                status_code=504,
                detail=message,
            )

        raise HTTPException(
            status_code=500,
            detail=message,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=(
                "Repository not found. "
                "Please upload and index the repository again."
            ),
        )

    except Exception as error:
        print(f"RAG query error: {error}")

        raise HTTPException(
            status_code=500,
            detail=(
                "Something went wrong while analyzing "
                "the repository. Please try again."
            ),
        )