PYTHON_VERSION=3.14.4
PYTHON_VENV=actu

.PHONY: help
help:
	@echo "Main:"
	@echo "  make help                 — Display this help"
	@echo "Utilities:"
	@echo "  make black                — Lint Python code with black"
	@echo "  make create-venv          — Create Python venv with Pyenv"
	@echo "  make delete-venv          — Delete Python venv"
	@echo "  make flake8               — Lint Python code with flake8"
	@echo "  make isort                — Lint Python code with isort"
	@echo "  make lint                 — Lint code"
	@echo "  make print-env            — Print environment variables"
	@echo "  make test                 — Run test suite"
	@echo "Local development:"
	@echo "  make local-build          — Build actu for local development"
	@echo "  make local-build-force    — Force build actu for local development"
	@echo "  make local-up             — Brings up actu for local development"
	@echo "  make local-django-exec    — Enter the local development django container"
	@echo "  make local-postgres-exec  — Enter the local development postgres container"

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

.PHONY: isort
isort:
	@docker exec -it --user root local-django-actu bash -c \
		"isort --check-only --diff ."

.PHONY: lint
lint: black isort flake8

.PHONY: test
test: lint
	@docker exec -it --user root local-django-actu bash -c \
		"python src/manage.py test"

.PHONY: local-build
local-build:
	@docker compose -f docker-compose-dev.yml build

.PHONY: local-build-force
local-build-force:
	@docker compose -f docker-compose-dev.yml build --force-rm --no-cache --pull

.PHONY: local-up
local-up:
	@docker compose -f docker-compose-dev.yml up

.PHONY: local-django-exec
local-django-exec:
	@docker exec -it --user root local-django-actu bash

.PHONY: local-postgres-exec
local-postgres-exec:
	@docker exec -it --user root local-postgres-actu bash
