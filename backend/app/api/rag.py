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


rag_service = RAGService()

retriever = CodeRetriever()

llm_service = LLMService()


@router.post("/index")
def index_repository(
    request: IndexRequest
):

    try:

        result = (
            rag_service.index_repository(
                request.repository_id
            )
        )

        return {
            "success": True,
            **result,
        }

    except FileNotFoundError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.post("/query")
def query_repository(
    request: QueryRequest
):

    try:

        # ==========================================
        # STEP 1 — RETRIEVE RELEVANT CODE
        # ==========================================

        results = retriever.retrieve(
            repository_id=request.repository_id,
            query=request.question,
            top_k=request.top_k,
        )

        if not results:

            return {
                "success": True,
                "question": request.question,
                "answer": (
                    "I could not find enough "
                    "relevant code in the repository "
                    "to answer this question."
                ),
                "results": [],
            }


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


    except Exception as error:

        print(
            f"RAG query error: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )