FROM python:3.11-slim

WORKDIR /app

# Install deps first (Docker layer cache)
COPY requirements.deploy.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway sets PORT env var; default to 8001 for local
ENV PORT=8001

# Shell form so $PORT is expanded at runtime
CMD uvicorn server:app --host 0.0.0.0 --port ${PORT}
