SHELL := /bin/bash

mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
mkfile_dir := $(dir $(mkfile_path))

PYTHON_VERSION=3.14.4
PYTHON_VENV=actu

HADOLINT_IMAGE = hadolint/hadolint
HADOLINT_VERSION = v2.14.0-alpine
HADOLINT_VLOCAL = -v ${mkfile_dir}:/host:ro
HADOLINT = @docker run --rm ${HADOLINT_VLOCAL} ${HADOLINT_IMAGE}:${HADOLINT_VERSION}

TRIVY_IMAGE = aquasec/trivy
TRIVY_VERSION = 0.70.0
TRIVY_VCACHE = -v /tmp/trivy/:/root/.cache/
TRIVY_VLOCAL = -v /var/run/docker.sock:/var/run/docker.sock
TRIVY = @docker run --rm ${TRIVY_VCACHE} ${TRIVY_VLOCAL} ${TRIVY_IMAGE}:${TRIVY_VERSION}

.PHONY: help
help:
	@echo "Main:"
	@echo "  make help                 — Display this help"
	@echo "Utilities:"
	@echo "  make assets-build         — Build assets with Vite"
	@echo "  make black                — Lint Python code with black"
	@echo "  make coverage             — Run test suite with text coverage"
	@echo "  make coverage-html        — Run test suite with html coverage"
	@echo "  make create-venv          — Create Python venv with Pyenv"
	@echo "  make delete-venv          — Delete Python venv"
	@echo "  make eslint               — Lint JS code with eslint"
	@echo "  make flake8               — Lint Python code with flake8"
	@echo "  make hadolint             — Lint Dockerfile with hadolint"
	@echo "  make isort                — Lint Python code with isort"
	@echo "  make lint                 — Lint code"
	@echo "  make print-env            — Print environment variables"
	@echo "  make scan                 — Scan latest app image"
	@echo "  make stylelint            — Lint SCSS code with stylelint"
	@echo "  make test                 — Run test suite"
	@echo "  make translation          — Update translation files"
	@echo "Local development:"
	@echo "  make local-build          — Build actu for local development"
	@echo "  make local-build-force    — Force build actu for local development"
	@echo "  make local-up             — Brings up actu for local development"
	@echo "  make local-assets-exec    — Enter the local development assets container"
	@echo "  make local-django-exec    — Enter the local development django container"
	@echo "  make local-postgres-exec  — Enter the local development postgres container"
	@echo "Local production:"
	@echo "  make prod-build           — Build actu for local production"
	@echo "  make prod-build-force     — Force build actu for local production"
	@echo "  make prod-up              — Brings up actu for local production"
	@echo "  make prod-django-exec     — Enter the local production django container"
	@echo "  make prod-nginx-exec      — Enter the local production nginx container"
	@echo "  make prod-postgres-exec   — Enter the local production postgres container"
	@echo "OpenShift:"
	@echo "  make local-clone          — Clone production database to the local database"
	@echo "  make dev-clone            — Clone production database to the dev database"
	@echo "  make staging-clone        — Clone production database to the staging database"


CLONE_TARGETS := local-clone db-local-clone dev-clone db-dev-clone staging-clone db-staging-clone

ifneq ($(filter $(CLONE_TARGETS),$(MAKECMDGOALS)),)
include /keybase/team/epfl_actu/dev/db
export
include /keybase/team/epfl_actu/staging/db
export
include /keybase/team/epfl_actu/prod/db
export
endif

# To add all variable to your shell, use
# export $(xargs < /keybase/team/epfl_actu/local/env);
check-env:
ifeq ($(wildcard /keybase/team/epfl_actu/local/env),)
	@echo "Be sure to have access to /keybase/team/epfl_actu/local/env"
	@exit 1
else
include /keybase/team/epfl_actu/local/env
export
endif

.PHONY: print-env
print-env: check-env
	@echo "ACTU_SECRET_KEY=${ACTU_SECRET_KEY}"
	@echo "ACTU_DATABASE_HOST=${ACTU_DATABASE_HOST}"
	@echo "ACTU_DATABASE_PORT=${ACTU_DATABASE_PORT}"
	@echo "ACTU_DATABASE_NAME=${ACTU_DATABASE_NAME}"
	@echo "ACTU_DATABASE_USER=${ACTU_DATABASE_USER}"
	@echo "ACTU_DATABASE_PASSWORD=${ACTU_DATABASE_PASSWORD}"
	@echo "ACTU_TENANT_ID=${ACTU_TENANT_ID}"
	@echo "ACTU_OIDC_RP_CLIENT_ID=${ACTU_OIDC_RP_CLIENT_ID}"
	@echo "ACTU_OIDC_RP_CLIENT_SECRET=${ACTU_OIDC_RP_CLIENT_SECRET}"
	@echo "ACTU_API_USERNAME=${ACTU_API_USERNAME}"
	@echo "ACTU_API_PASSWORD=${ACTU_API_PASSWORD}"
	@echo "ACTU_API_RIGHT_ID=${ACTU_API_RIGHT_ID}"

.PHONY: create-venv
create-venv:
	@if [ ! -d "${HOME}/.pyenv/versions/${PYTHON_VERSION}" ]; then \
		pyenv install ${PYTHON_VERSION}; \
	fi
	@pyenv virtualenv ${PYTHON_VERSION} ${PYTHON_VENV}
	@echo ${PYTHON_VENV} > .python-version
	@pip install -r requirements/requirements-dev.txt

.PHONY: delete-venv
delete-venv:
	@pyenv virtualenv-delete --force ${PYTHON_VENV}
	@rm .python-version

.PHONY: black
black:
	@docker exec -it --user root local-django-actu bash -c \
		"black --check --diff ."

.PHONY: flake8
flake8:
	@docker exec -it --user root local-django-actu bash -c \
		"flake8"

.PHONY: hadolint
hadolint:
	@${HADOLINT} sh -c "hadolint /host/docker/*/Dockerfile"

.PHONY: isort
isort:
	@docker exec -it --user root local-django-actu bash -c \
		"isort --check-only --diff ."

.PHONY: eslint
eslint:
	@docker exec -it --user root local-assets-actu sh -c \
		"npm run eslint"

.PHONY: stylelint
stylelint:
	@docker exec -it --user root local-assets-actu sh -c \
		"npm run stylelint"

.PHONY: lint
lint: hadolint black isort flake8 stylelint eslint

.PHONY: assets-build
assets-build:
	@docker exec -it --user root local-assets-actu sh -c \
		"npm run build"

.PHONY: test
test: lint assets-build
	@docker exec -it --user root local-django-actu bash -c \
		"DJANGO_SETTINGS_MODULE='configs.ci' python src/manage.py test"

.PHONY: translation
translation:
	@docker exec -it --user root local-django-actu bash -c \
		"python src/manage.py makemessages --all --no-location --no-wrap"

.PHONY: coverage
coverage:
	@docker exec -it --user root local-django-actu bash -c \
		"DJANGO_SETTINGS_MODULE='configs.ci' coverage run src/manage.py test"
	@docker exec -it --user root local-django-actu bash -c \
		"coverage report"

.PHONY: coverage-html
coverage-html:
	@docker exec -it --user root local-django-actu bash -c \
		"DJANGO_SETTINGS_MODULE='configs.ci' coverage run src/manage.py test"
	@docker exec -it --user root local-django-actu bash -c \
		"coverage html"
	@docker cp local-django-actu:/app/htmlcov .
	@echo -e "\nOpen file://${mkfile_dir}htmlcov/index.html"

.PHONY: scan
scan:
	@${TRIVY} clean --scan-cache
	@${TRIVY} image --severity HIGH,CRITICAL prod-django-actu:latest

.PHONY: local-build
local-build:
	@docker compose -f docker-compose-dev.yml build

.PHONY: local-build-force
local-build-force:
	@docker compose -f docker-compose-dev.yml build --force-rm --no-cache --pull

.PHONY: local-up
local-up:
	@docker compose -f docker-compose-dev.yml up

.PHONY: local-assets-exec
local-assets-exec:
	@docker exec -it --user root local-assets-actu sh

.PHONY: local-django-exec
local-django-exec:
	@docker exec -it --user root local-django-actu bash

.PHONY: local-postgres-exec
local-postgres-exec:
	@docker exec -it --user root local-postgres-actu bash

.PHONY: prod-build
prod-build:
	@docker compose build

.PHONY: prod-build-force
prod-build-force:
	@docker compose build --force-rm --no-cache --pull

.PHONY: prod-up
prod-up:
	@docker compose up

.PHONY: prod-django-exec
prod-django-exec:
	@docker exec -it --user root prod-django-actu bash

.PHONY: prod-nginx-exec
prod-nginx-exec:
	@docker exec -it --user root prod-nginx-actu sh

.PHONY: prod-postgres-exec
prod-postgres-exec:
	@docker exec -it --user root prod-postgres-actu bash

check-postgres-dump:
	@type pg_dump > /dev/null 2>&1 || { echo >&2 "Please install postgresql-client-18."; exit 1; }

db-dump: check-postgres-dump
	@PGPASSWORD="$(P_PGPASSWORD)" pg_dump \
		-h $(P_PGHOST) \
		-p $(P_PGPORT) \
		-U $(P_PGUSER) \
		-d $(P_PGDATABASE) \
		--format=custom --file=/tmp/actu.sql

.PHONY: db-local-clone
db-local-clone: db-dump
	@PGPASSWORD="$(ACTU_DATABASE_PASSWORD)" pg_restore \
		-h 127.0.0.1 \
		-p 25432 \
		-U $(ACTU_DATABASE_USER) \
		-d $(ACTU_DATABASE_NAME) \
		--clean --no-owner --no-privileges /tmp/actu.sql

.PHONY: db-dev-clone
db-dev-clone: db-dump
	@PGPASSWORD="$(D_PGPASSWORD)" pg_restore \
		-h $(D_PGHOST) \
		-p $(D_PGPORT) \
		-U $(D_PGUSER) \
		-d $(D_PGDATABASE) \
		--clean --no-owner --no-privileges /tmp/actu.sql

.PHONY: db-staging-clone
db-staging-clone: db-dump
	@PGPASSWORD="$(S_PGPASSWORD)" pg_restore \
		-h $(S_PGHOST) \
		-p $(S_PGPORT) \
		-U $(S_PGUSER) \
		-d $(S_PGDATABASE) \
		--clean --no-owner --no-privileges /tmp/actu.sql

.PHONY:
local-clone: db-local-clone

.PHONY:
dev-clone: db-dev-clone

.PHONY:
staging-clone: db-staging-clone
