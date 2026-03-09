FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy and install dependencies first (layer caching)
# Using CPU-only torch index as primary, PyPI as fallback for other packages
COPY apps/semantic-reranker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple/

# Copy application source and data
COPY apps/semantic-reranker/src/ src/
COPY apps/semantic-reranker/data/ data/
COPY apps/semantic-reranker/main.py .
COPY apps/semantic-reranker/evaluate.py .
COPY apps/semantic-reranker/benchmark.py .
COPY apps/semantic-reranker/generate_report.py .
COPY apps/semantic-reranker/entrypoint.sh .
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
