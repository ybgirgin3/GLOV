from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.postgresqlorm import POST_ORM
from app.services.embedding_service import embedding_service, _embed_text

router = APIRouter(prefix="/search")
orm = POST_ORM()

@router.get("/query")
async def search(url: str, query: str, top_k: Optional[int] = 5):
    try:
        # get pdf, seperate to chunks and index to postgresql
        embedding_service(url)

        # embed the question
        embedded_query = _embed_text(query)[0]
        
        results = orm.search_nearest_chunks(embedded_query, top_k=5)

        orm.close()

        return {
            "results": [
                {"chunk": result.chunk, "id": result.id} for result in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
