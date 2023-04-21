# syntax=docker/dockerfile:1.2
FROM python:3.11

RUN groupadd -g 3000 -r builder && useradd -u 3000 -r -g builder -s /usr/sbin/nologin builder

USER builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/builder/.poetry/bin:${PATH}" \
    POETRY_HOME="/home/builder/.poetry" \
    POETRY_VERSION=1.4.2

WORKDIR /home/builder/
RUN curl -sSL -o install-poetry.py https://install.python-poetry.org/ \
    && python3 install-poetry.py \
    && rm install-poetry.py

WORKDIR /home/builder/vistral
COPY --chown=builder:builder . .
RUN poetry build
#RUN poetry publish