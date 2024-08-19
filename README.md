# GLOV-TASK

## Overview

This project is a text extraction and search system that uses PostgreSQL with the `pgvector` extension to index and search text extracted from PDF documents. It incorporates various technologies including FastAPI for the web framework, SQLAlchemy for ORM, and PyTorch with Transformers for text embedding.

## Features

- Extract text from PDF files.
- Split text into manageable chunks.
- Compute embeddings for text chunks using a pre-trained model.
- Store text chunks and their embeddings in PostgreSQL.
- Search for the nearest text chunks based on a query embedding.

## Technologies

- **FastAPI**: Web framework for building APIs.
- **SQLAlchemy**: ORM for database interactions.
- **pgvector**: PostgreSQL extension for vector similarity search.
- **PyTorch**: Deep learning library used for model inference.
- **Transformers**: Library for using pre-trained models for text embeddings.
- **requests**: Library for HTTP requests.
- **PyPDF2**: Library for PDF file handling.

## Installation

### Prerequisites

- Python 3.7+
- PostgreSQL with `pgvector` extension
- Docker (for containerized deployment)

### Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```
2. **Install Dependencies**
   Create a virtual environment and install the required packages

   ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
   ```

3. **Setup PostgreSQL**
   Ensure PostgreSQL is running with the pgvector extension. You can use Docker to set up PostgreSQL with pgvector.

   ```bash
   docker pull pgvector/pgvector:pg16
   ```

### Try on Docker

```bash
docker-compose up --build
```

### EXAMPLE API

- You can try it with below url

```bash
https://glov.onrender.com/docs
```

### USAGE

**API ENDPOINTS**

- Home
  - Route: `/search/`
  - Method: `GET`
  - Description: A simple endpoint to check if the API is working.
  - Response:
    ```bash
    {
      "welcome": "homeee"
    }
    ```
- Search
  - Route: `/search/query/`
  - Method: `GET`
  - Description: Processes a PDF from the provided URL, splits the text into chunks, computes embeddings, and searches for similar chunks based on a query.
  - Query Parameters:
    - url (str): The URL of the PDF file.
    - query (str): The query text to search for.
    - top_k (int): Number of nearest chunks to return (default is 5).
  - Response:
    ```bash
    {
      "results": [
        {
          "chunk": "Text chunk content",
          "id": 1
        },
        ...
      ]
    }
    ```

### Code Overview

- app/services/postgresqlorm.py
  - POST_ORM: Class for handling PostgreSQL database operations including creating tables, adding text chunks, and performing similarity searches.
- app/services/embedding_service.py
  - embedding_service(url: str): Main service function to process a PDF, extract text, split into chunks, compute embeddings, and upload to the database.
  - \_get_pdf(url: str) -> str: Downloads a PDF from the given URL.
  - \_extract_text(path: str): Extracts text from the PDF file.
  - \_seperate_to_chunk(text: str) -> list[str]: Splits text into chunks.
  - \_embed_text(text): Computes embeddings for the text.
  - \_upload_to_db(chk, embedding): Uploads text chunks and their embeddings to the database.
- app/routers/search.py
  - home(): Simple endpoint to check API health.
  - search(url: str, query: str, top_k: int): Processes a PDF from the URL, computes query embedding, and retrieves nearest text chunks.

### License

- This project is licensed under the MIT License. See the LICENSE file for details.
