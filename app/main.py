from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search
import nltk

nltk.download("punkt")

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
