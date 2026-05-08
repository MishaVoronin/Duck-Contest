FROM ghcr.io/astral-sh/uv:0.11.7-python3.14-trixie
WORKDIR /app
ADD uv.lock pyproject.toml ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
WORKDIR /app/src
COPY src/ .
RUN uv sync
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen
