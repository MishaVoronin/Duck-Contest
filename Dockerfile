FROM ghcr.io/astral-sh/uv:0.11.7-python3.14-trixie
WORKDIR /
ADD uv.lock /
ADD pyproject.toml /
WORKDIR /src
ADD src/main.py .
COPY src/api ./api
COPY src/templates ./templates

