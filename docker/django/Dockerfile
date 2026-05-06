FROM ubuntu:26.04 AS base

RUN ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime

RUN \
  apt-get update && \
  apt-get install -yqq --no-install-recommends \
    python3=* \
    python3-pip=* && \
  rm -rf /var/lib/apt/lists/* && \
  mkdir -p /public/static

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



FROM compile AS assets

ENV ACTU_SECRET_KEY="UNUSED" \
    DJANGO_SETTINGS_MODULE="configs.ocp" \
    ACTU_DATABASE_HOST="UNUSED" \
    ACTU_DATABASE_PORT="UNUSED" \
    ACTU_DATABASE_NAME="UNUSED" \
    ACTU_DATABASE_USER="UNUSED" \
    ACTU_DATABASE_PASSWORD="UNUSED"

COPY ./src /app/src
RUN \
  python src/manage.py collectstatic --noinput



FROM base AS production

COPY --from=assets /opt/venv /opt/venv
COPY --from=assets /app/src /app/src
COPY --from=assets /public/static /app/static
COPY ./docker/django/entrypoint-django-prod.sh /entrypoint.sh

RUN \
  chown -R 1000:0 /app /public && \
  chmod -R g=u /app /public && \
  chmod +x /entrypoint.sh

VOLUME /public/static
USER 1000
EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
