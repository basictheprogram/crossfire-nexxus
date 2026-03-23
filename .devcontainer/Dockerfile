# hadolint ignore=DL3007
FROM ghcr.io/astral-sh/uv:latest AS uv
FROM mcr.microsoft.com/devcontainers/python:dev-3.14-trixie
LABEL maintainer="tanner@real-time.com"

ENV LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PYTHONUNBUFFERED=1

ARG USERNAME=vscode
ARG USER_UID=3000
ARG USER_GID=3000

# hadolint ignore=DL3008
RUN rm -f /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    tzdata \
    libonig-dev \
    python3-dev \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    git \
    git-lfs \
    less \
    zip \
    unzip \
    vim-tiny \
    openssh-client \
    shfmt \
    shellcheck \
    && apt-get autoremove \
    && apt-get clean  \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/$USERNAME  \
    && if ! getent group ${USERNAME}; then groupadd --gid ${USER_UID} $USERNAME; fi \
    && if ! id -u ${USERNAME} > /dev/null 2>&1; then useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}; fi

COPY --from=uv --chown=${USERNAME}: /uv /uvx /bin/

EXPOSE 8000
