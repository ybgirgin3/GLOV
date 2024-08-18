FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    postgresql \
    postgresql-contrib \
    postgresql-server-dev-all

RUN git clone https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    rm -rf /pgvector

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["fastapi", "run", "main.py", "--port", "80"]

