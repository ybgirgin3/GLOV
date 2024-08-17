from fastapi import FastAPI
from .routers import search
import nltk

nltk.download("punkt")

app = FastAPI()

app.include_router(search.router)
