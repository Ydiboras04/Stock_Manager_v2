FROM python:3.13-slim
WORKDIR /app
# Same pinned versions as local development and CI.
COPY requirements.txt pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic.ini ./
COPY alembic ./alembic
EXPOSE 8000
# Apply migrations, then start the API.
CMD ["sh", "-c", "alembic upgrade head && uvicorn stock.api.main:app --host 0.0.0.0 --port 8000"]
