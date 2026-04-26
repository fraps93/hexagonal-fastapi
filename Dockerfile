FROM python:3.10-slim AS base

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/
COPY main.py .

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
