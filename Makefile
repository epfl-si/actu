.PHONY: help
help:
	@echo "Main:"
	@echo "  make help                 — Display this help"
	@echo "Utilities:"
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
