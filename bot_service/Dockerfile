FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml /app/pyproject.toml
RUN uv sync

COPY . /app

CMD ["uv", "run", "python", "-m", "app.main"]
