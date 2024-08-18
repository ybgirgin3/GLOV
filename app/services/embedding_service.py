import requests
import tempfile
import uuid


from app.services.postgresqlorm import POST_ORM

import torch
import nltk
from PyPDF2 import PdfReader
from transformers import AutoTokenizer, AutoModel

tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-large-en")
model = AutoModel.from_pretrained("BAAI/bge-large-en")

post_orm = POST_ORM()


class PDFGetError(BaseException):
    pass


class PDFWriteError(BaseException):
    pass


class PDFReadError(BaseException):
    pass



def _get_pdf(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise PDFGetError()

    fn = f"{tempfile.gettempdir()}{uuid.uuid4()}"

    try:
        with open(fn, "wb") as f:
            f.write(response.content)
    except Exception as e:
        raise PDFWriteError()

    return fn


def _extract_text(path: str = "/full/path/to/pdf") -> str:
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()

    except Exception as e:
        raise PDFReadError()

    return text


def _seperate_to_chunk(text: str) -> list[str]:
    chunks = nltk.tokenize.sent_tokenize(text)
    chunks = [" ".join(chunks[i : i + 100]) for i in range(0, len(chunks), 100)]
    return chunks


def _embed_text(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return torch.mean(outputs.last_hidden_state, dim=1).detach().numpy().tolist()

def _upload_to_db(chk, embedding):
  # Her parçanın embedding'ini hesapla ve veritabanına ekle
    # chunk_text = ' '.join(chunk_words)
    # chunk_embedding = get_embedding(chunk_text)[0]
    try:
        post_orm.add_chunk(chk, embedding)
    except Exception as e:
        print(e)

def embedding_service(url: str):
    # get pdf
    pdf_path: str = _get_pdf(url=url)

    # extract text
    text: str = _extract_text(pdf_path)

    # 100 word chunk
    chunks = _seperate_to_chunk(text)

    # upload chunks to redis and return embeddings
    for chk in chunks:
        embedding = _embed_text(chk)[0]
        _upload_to_db(chk, embedding=embedding)

    

