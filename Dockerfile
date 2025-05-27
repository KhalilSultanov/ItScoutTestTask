FROM python:3.11-slim

ENV POETRY_VERSION=1.8.2
ENV PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --with dev

COPY . .

RUN chmod +x wait-for-it.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
