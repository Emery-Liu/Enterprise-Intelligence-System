FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY relevance_matching ./relevance_matching

EXPOSE 1000

CMD ["uvicorn", "relevance_matching.src.main:app", "--host", "0.0.0.0", "--port", "1000"]