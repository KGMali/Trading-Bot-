FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry
COPY pyproject.toml ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY . .

CMD ["python", "-m", "leekbot.cli", "run", "--mode", "paper", "--config", "leekbot/config/sample.config.yaml"]
