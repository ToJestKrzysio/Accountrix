FROM ghcr.io/astral-sh/uv:python3.13-alpine

WORKDIR /app

COPY ./pyproject.toml ./uv.lock .python-version ./

RUN uv sync

COPY . .

EXPOSE 8000
ENV PYTHONPATH=/app
CMD ["uv", "run", "fastapi", "dev", "src/main.py", "--host", "0.0.0.0", "--port", "8000"]