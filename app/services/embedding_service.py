import requests
import tempfile
import uuid

from app.services.postgresqlorm import POST_ORM

import torch
import nltk
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModel

# Initialize tokenizer and model for text embedding
tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en")
model = AutoModel.from_pretrained("BAAI/bge-large-en")

# Initialize the ORM for PostgreSQL
post_orm = POST_ORM()


class PDFGetError(BaseException):
    """Exception raised for errors in fetching the PDF."""
    pass


class PDFWriteError(BaseException):
    """Exception raised for errors in writing the PDF to disk."""
    pass


class PDFReadError(BaseException):
    """Exception raised for errors in reading the PDF content."""
    pass


def _get_pdf(url: str) -> str:
    """
    Downloads a PDF from the given URL and saves it to a temporary file.

    Args:
        url (str): The URL of the PDF file to download.

    Returns:
        str: The path to the saved temporary PDF file.

    Raises:
        PDFGetError: If the HTTP request to download the PDF fails.
        PDFWriteError: If there is an error writing the PDF file to disk.
    """
    response = requests.get(url)
    if response.status_code != 200:
        raise PDFGetError("Failed to fetch PDF from URL.")

    fn = f"{tempfile.gettempdir()}/{uuid.uuid4()}.pdf"

    try:
        with open(fn, "wb") as f:
            f.write(response.content)
    except Exception as e:
        raise PDFWriteError("Failed to write PDF to disk.")

    return fn


def _extract_text(path: str = "/full/path/to/pdf") -> str:
    """
    Extracts text from the PDF file at the given path.

    Args:
        path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.

    Raises:
        PDFReadError: If there is an error reading the PDF file.
    """
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    except Exception as e:
        raise PDFReadError("Failed to read text from PDF.")

    return text


def _seperate_to_chunk(text: str) -> list[str]:
    """
    Splits the given text into chunks of approximately 100 sentences each.

    Args:
        text (str): The text to be split into chunks.

    Returns:
        list[str]: A list of text chunks.
    """
    chunks = nltk.tokenize.sent_tokenize(text)
    chunks = [" ".join(chunks[i: i + 100]) for i in range(0, len(chunks), 100)]
    return chunks


def _embed_text(text):
    """
    Computes the embedding of the given text using a pre-trained model.

    Args:
        text (str): The text to be embedded.

    Returns:
        list: The embedding of the text as a list of floats.
    """
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return torch.mean(outputs.last_hidden_state, dim=1).detach().numpy().tolist()


def _upload_to_db(chk, embedding):
    """
    Uploads a text chunk and its embedding to the database.

    Args:
        chk (str): The text chunk to be uploaded.
        embedding (list): The embedding vector for the text chunk.
    """
    try:
        post_orm.add_chunk(chk, embedding)
    except Exception as e:
        print(f"Error uploading chunk to database: {e}")


def embedding_service(url: str):
    """
    Main service function to process a PDF document and upload text chunks with embeddings to the database.

    Args:
        url (str): The URL of the PDF file to process.
    """
    # Get PDF file from URL
    pdf_path: str = _get_pdf(url=url)

    # Extract text from the PDF file
    text: str = _extract_text(pdf_path)

    # Split text into chunks of approximately 100 sentences
    chunks = _seperate_to_chunk(text)

    # Upload each chunk and its embedding to the database
    for chk in chunks:
        embedding = _embed_text(chk)[0]
        _upload_to_db(chk, embedding=embedding)
