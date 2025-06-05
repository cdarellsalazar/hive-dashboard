FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

RUN mkdir -p application

RUN apt-get update && apt-get install -y curl

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]