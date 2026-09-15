# Vintage capture job (ops/VINTAGE-CAPTURE.md). Render runs this image on a
# schedule; the command is the capture CLI. openssl and curl are for the
# manifest timestamping step; uv brings Python and the locked dependencies.
FROM python:3.14-slim
RUN apt-get update && apt-get install -y --no-install-recommends openssl curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.9.18 /uv /uvx /bin/
WORKDIR /app
ENV UV_LINK_MODE=copy UV_COMPILE_BYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --group capture --group registers --no-install-project
COPY . .
RUN uv sync --frozen --no-dev --group capture --group registers
ENTRYPOINT ["uv", "run", "--no-sync", "--group", "capture", "--group", "registers", "grid-mysteries"]
CMD ["capture", "run"]
