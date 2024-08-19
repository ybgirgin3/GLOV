from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError
from app.commons.models import TextChunk


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


class POST_ORM:
    DEBUG = True

    def __init__(self) -> None:
        """Initializes the POST_ORM class, setting up the database engine and session."""
        self.engine = create_engine(self.connection_url, echo=True)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self.session = self.SessionLocal()
        self.is_connection_successfull()
        # self.create_tables()

    def create_tables(self):
        """Creates database tables and adds necessary extensions."""
        self._add_extension()
        Base.metadata.create_all(bind=self.engine)

    def add_chunk(self, chunk_text, chunk_embedding):
        """
        Adds a new text chunk with its corresponding embedding to the database.

        Args:
            chunk_text (str): The text chunk to be stored.
            chunk_embedding (list or array): The embedding vector for the text chunk.
        """
        try:
            # Create a new TextChunk instance
            new_chunk = TextChunk(chunk=chunk_text, embedding=chunk_embedding)

            # Add the instance to the session and commit the transaction
            self.session.add(new_chunk)
            self.session.commit()
        except IntegrityError:
            # Rollback the transaction in case of an integrity error
            self.session.rollback()
            print(f"Chunk with text '{chunk_text}' already exists.")

    def get_chunks(self):
        """
        Retrieves all text chunks stored in the database.

        Returns:
            list: A list of all TextChunk objects in the database.
        """
        return self.session.query(TextChunk).all()

    def search_nearest_chunks(self, query_embedding, top_k: int = 5):
        """
        Searches for the nearest text chunks based on a query embedding.

        Args:
            query_embedding (list or array): The embedding vector to search against.
            top_k (int): The number of closest chunks to return. Default is 5.

        Returns:
            list: A list of rows representing the nearest chunks and their embeddings.
        """
        embedding_str = ",".join(map(str, query_embedding))

        # KNN SQL query to find the nearest neighbors
        knn_query = text(
            f"""
            SELECT id, chunk, embedding
            FROM text_chunks
            ORDER BY embedding <=> ARRAY[{embedding_str}]::vector
            LIMIT :k;
        """
        )

        # Execute the query and fetch the results
        with self.engine.connect() as connection:
            result = connection.execute(knn_query, {"k": top_k})
            rows = result.fetchall()
        return rows

    def close(self):
        """Closes the current database session."""
        self.session.close()

    def is_connection_successfull(self):
        """
        Tests the database connection to ensure it is successful.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        try:
            # Test the database connection
            connection = self.engine.connect()
            print("Bağlantı başarılı!")
            connection.close()
            return True
        except Exception as e:
            print(e)
            return False

    @property
    def connection_url(self):
        """
        Constructs the database connection URL based on environment variables or defaults.

        Returns:
            str: The database connection URL.
        """
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
            POSTGRES_USER = "postgres_user"
            POSTGRES_PASSWORD = "password123"
            POSTGRES_DB = "mydatabase"
            DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@postgres:5432/{POSTGRES_DB}"
            # DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{POSTGRES_DB}"
            return DATABASE_URL

        if not hasattr(self, "_connection_url"):
            if self.DEBUG:
                self._connection_url = _default_env()
            else:
                self._connection_url = _read_env()

        return self._connection_url

    def _add_extension(self):
        """Adds the 'vector' extension to the PostgreSQL database if it doesn't already exist."""
        with self.engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

    def _is_exists(self, params: dict):
        """
        Checks if a record exists in the database based on provided conditions.

        Args:
            params (dict): A dictionary containing the model and where clause.

        Returns:
            bool: True if the record exists, False otherwise.
        """
        model = params.get("model", None)
        assert model, "model have to be defined"

        where_clause = params.get("where", None)
        assert where_clause, "where have to be defined"

        x = self.session.query(model).where(model.where_clause).first()

        return x is not None
