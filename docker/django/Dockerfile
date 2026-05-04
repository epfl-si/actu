FROM ubuntu:26.04 AS base

RUN ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime

RUN \
  apt-get update && \
  apt-get install -yqq --no-install-recommends \
    python3=* \
    python3-pip=* && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV LANG="C.UTF-8" \
    PYTHONUNBUFFERED="1" \
    PYTHONIOENCODING="UTF-8" \
    VIRTUAL_ENV="/opt/venv" \
    PATH="/opt/venv/bin:$PATH"



FROM base AS compile

RUN \
  apt-get update && \
  apt-get install -yqq --no-install-recommends \
    gettext=* \
    python3-dev=* \
    python3-venv=* && \
  rm -rf /var/lib/apt/lists/*

COPY ./requirements /app/requirements

RUN \
  python3 -m venv "$VIRTUAL_ENV" && \
  pip install --no-cache-dir -r requirements/requirements.txt



FROM compile AS development

ENV PYTHONDONTWRITEBYTECODE="1"

RUN \
  pip install --no-cache-dir -r requirements/requirements-dev.txt

CMD ["python", "src/manage.py", "runserver", "0.0.0.0:8000"]
