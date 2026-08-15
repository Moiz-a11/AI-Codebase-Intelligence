from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag_service import RAGService
from app.rag.retriever import CodeRetriever


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

        results = retriever.retrieve(
            repository_id=request.repository_id,
            query=request.question,
            top_k=request.top_k,
        )

        return {
            "success": True,
            "question": request.question,
            "results": results,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )