import dataclasses
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column

from pgvector.sqlalchemy import Vector


@dataclasses.dataclass
class Config:
    """
    A data class to hold database configuration parameters.

    Attributes:
        host (Optional[str]): The hostname of the database server.
        user (Optional[str]): The username for database access.
        password (Optional[str]): The password for database access.
        db_name (Optional[str]): The name of the database.
    """
    host: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    db_name: Optional[str] = None


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""
    pass


class TextChunk(Base):
    """
    SQLAlchemy ORM model for the text_chunks table.

    Attributes:
        id (int): Primary key, unique identifier for each text chunk.
        chunk (str): The text content of the chunk.
        embedding (Vector): The embedding vector associated with the text chunk.
    """
    __tablename__ = "text_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk = Column(Text, nullable=False)
    embedding = Column(Vector(1024))
