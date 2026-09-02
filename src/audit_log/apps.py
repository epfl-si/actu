from django.apps import AppConfig


class AuditLogConfig(AppConfig):
    name = "audit_log"
    verbose_name = "Audit Log"

    def ready(self):
        import audit_log.signals  # noqa: F401
