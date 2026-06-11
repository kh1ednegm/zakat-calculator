FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Arabic font for PDF reports (falls back to Helvetica if download fails)
RUN mkdir -p app/static/fonts \
    && curl -fsSL -o app/static/fonts/Amiri-Regular.ttf \
       https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf || true

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
