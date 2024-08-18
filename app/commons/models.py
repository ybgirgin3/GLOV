import dataclasses
from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column

from pgvector.sqlalchemy import Vector




@dataclasses.dataclass
class Config:
    host: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    db_name: Optional[str] = None


class Base(DeclarativeBase):
    pass


class TextChunk(Base):
    __tablename__ = "text_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk = Column(Text, nullable=False)
    embedding = Column(Vector(1024))
