import psycopg2
from dotenv import load_dotenv
import os
from typing import Optional
from app.commons.models import Config
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.sql import text
from app.commons.models import TextChunk


class Base(DeclarativeBase):
    pass


class POST_ORM:
    DEBUG = True

    def __init__(self) -> None:
        self.engine = create_engine(self.connection_url, echo=True)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.session = self.SessionLocal()
        self.is_connection_successfull()
        # self.create_tables()

    def create_tables(self):
        self._add_extension()
        Base.metadata.create_all(bind=self.engine)
        # with self.engine.connect() as connection:
        # # pgvector uzantısını ekleme
        #     connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        #     print("pgvector eklentisi başarıyla eklendi.")

        #     # text_chunks tablosunu oluşturma
        #     create_table_query = """
        #     CREATE TABLE IF NOT EXISTS text_chunks (
        #         id SERIAL PRIMARY KEY,
        #         chunk TEXT,
        #         embedding vector(1024)  -- Bu kısım embedding boyutuna göre değişebilir.
        #     );
        #     """
        #     connection.execute(text(create_table_query))
        #     connection.close()
        #     print("text_chunks tablosu başarıyla oluşturuldu.")

    def add_chunk(self, chunk_text, chunk_embedding):
        # chunk_embedding_str = '{' + ','.join(map(str, chunk_embedding)) + '}'
        new_chunk = TextChunk(chunk=chunk_text, embedding=chunk_embedding)
        # with self.engine.connect() as connection:
        #     sql = """
        #         INSERT INTO text_chunks (chunk, embedding)
        #         VALUES (%s, %d);
        #     """
        #     embedding_str = '{' + ','.join(map(str, chunk_embedding)) + '}'
        #     connection.execute(sql, (chunk_text, embedding_str))
        #     connection.close()

        self.session.add(new_chunk)
        self.session.commit()

    def get_chunks(self):
        return self.session.query(TextChunk).all()

    def search_nearest_chunks(self, query_embedding, top_k=5):
        with self.engine.connect() as connection:
            result = connection.execute(
                text("""
                SELECT id, chunk
                FROM text_chunks
                ORDER BY embedding <=> :query_embedding
                LIMIT :top_k
                """),
                {"query_embedding": query_embedding, "top_k": top_k}
            )
            return result.fetchall()

    def close(self):
        self.session.close()

    def is_connection_successfull(self):
        try:
            # Bağlantı testi
            connection = self.engine.connect()
            print("Bağlantı başarılı!")
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False

    @property
    def connection_url(self):
        def _read_env():
            load_dotenv()

            host = os.getenv("HOST")
            user = os.getenv("USER")
            password = os.getenv("PASSWORD")
            db_name = os.getenv("DB_NAME")

            DATABASE_URL = (
                f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db_name}"
            )
            return DATABASE_URL

        def _default_env():
            # db_name = "mydatabase"
            # user = "postgresql"
            # host = "localhost"
            # password = "password123"
            POSTGRES_USER =  'postgres_user'
            POSTGRES_PASSWORD =  'password123'
            POSTGRES_DB = 'mydatabase'
            DATABASE_URL = (
                f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
            )
            # return Config(db=db_name, user=user, password=password, host=host)
            return DATABASE_URL

        if not hasattr(self, "_connection_url"):
            if self.DEBUG:
                self._connection_url = _default_env()
            else:
                self._connection_url = _read_env()

        return self._connection_url

    def _add_extension(self):
        with self.engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
