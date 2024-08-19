from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services.postgresqlorm import POST_ORM
from app.services.embedding_service import embedding_service, _embed_text

# Create a new router for search-related endpoints
router = APIRouter(prefix="/search")
orm = POST_ORM()


@router.get("/")
def home():
    """
    Simple endpoint to check if the API is working.

    Returns:
        dict: A dictionary with a welcome message.
    """
    return {"welcome": "homeee"}


@router.get("/query")
async def search(url: str, query: str, top_k: int = 5):
    """
    Searches for the nearest text chunks in the database based on a query.

    Args:
        url (str): The URL of the PDF file to process.
        query (str): The query text to search for.
        top_k (int): The number of nearest chunks to return. Default is 5.

    Returns:
        dict: A dictionary containing the search results.

    Raises:
        HTTPException: If an error occurs during processing, a 500 HTTP error is raised.
    """
    try:
        # Process the PDF file: get it, split it into chunks, and index chunks into PostgreSQL
        embedding_service(url)

        # Embed the query text
        embedded_query = _embed_text(query)[0]

        # Search for the nearest chunks in the database
        results = orm.search_nearest_chunks(embedded_query, top_k=top_k)

        # Close the database connection
        orm.close()

        # Return the search results
        return {
            "results": [{"chunk": result.chunk, "id": result.id} for result in results]
        }

    except Exception as e:
        # Raise an HTTP exception if there is an error
        raise HTTPException(status_code=500, detail=str(e))
