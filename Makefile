PYTHON_VERSION=3.14.4
PYTHON_VENV=actu

.PHONY: help
help:
	@echo "Main:"
	@echo "  make help                 — Display this help"
	@echo "Utilities:"
	@echo "  make create-venv          — Create Python venv with Pyenv"
	@echo "  make delete-venv          — Delete Python venv"
	@echo "  make print-env            — Print environment variables"

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
