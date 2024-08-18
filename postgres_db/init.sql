CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE text_chunks (
    id SERIAL PRIMARY KEY,
    chunk TEXT,
    embedding vector(1024)
);

