from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import search
import nltk

nltk.download("punkt")

app = FastAPI()

# Allow all origins for CORS, useful for development environments
origins = ["*"]

# Add CORS middleware to the application to handle cross-origin requests
# This enables the app to accept requests from different origins,
# which is often necessary when the front-end and back-end are hosted on different domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Specifies which origins are allowed; '*' allows all
    allow_credentials=True,         # Whether to allow credentials such as cookies or HTTP authentication
    allow_methods=["*"],            # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],            # Allow all headers
)

# Include the router from the 'search' module. This registers the endpoints defined in the search router
app.include_router(search.router)
