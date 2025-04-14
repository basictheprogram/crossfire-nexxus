ARG DEBIAN_VERSION=bookworm
ARG UV_VERSION=latest
ARG VARIANT=3.13

# Stage 1: UV CLI
FROM ghcr.io/astral-sh/uv:$UV_VERSION AS uv

# Stage 2: Base image
FROM python:$VARIANT-slim-$DEBIAN_VERSION AS base

WORKDIR /app

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock /app/

# Stage 2: Build dependencies and install Python packages
# FROM python:$VARIANT-slim-$DEBIAN_VERSION AS builder
FROM base AS builder

WORKDIR /app

COPY --from=uv /uv /uvx /bin/

# hadolint ignore=DL3008
RUN apt-get update -qq \
    && apt-get install -qq --no-install-recommends \
    libonig-dev \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


# COPY pyproject.toml uv.lock ./
RUN uv venv .venv \
    && uv pip install mysqlclient

RUN uv sync --frozen --no-install-project --only-dev


# Stage 3: Final runtime image
FROM python:$VARIANT-slim-$DEBIAN_VERSION AS final
LABEL maintainer="Bob Tanner <tanner@real-time.com>"

WORKDIR /app

COPY --from=builder /app /app
COPY --from=uv /uv /uvx /bin/
# COPY pyproject.toml uv.lock ./

ENV PYTHONDONTWRITEBYTECODE=True
ENV PYTHONUNBUFFERED=True
ENV UV_LINK_MODE=copy
# After copying files and before installing packages
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN uv sync --frozen --no-install-project --no-dev \
    && if ! getent group vscode; then groupadd --gid 3000 vscode; fi \
    && if ! id -u vscode > /dev/null 2>&1; then useradd --uid 3000 --gid 3000 -m vscode; fi

COPY --chown=vscode:vscode src/ ./

# hadolint ignore=DL3008
RUN apt-get update -qq \
    && apt-get install -qq --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -f pyproject.toml \
    && apt-get autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000

CMD ["sh", "/app/scripts/nexxus.sh"]
