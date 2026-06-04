from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend


class ToAdminEmailBackend(EmailBackend):
    """Custom email backend that forwards all emails to administrators."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.admin_emails = [
            admin[1]
            for admin in settings.ADMINS
            if isinstance(admin, tuple) and len(admin) >= 2
        ]

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        for email in email_messages:
            original_recipients = email.recipients()
            if original_recipients:
                subject_suffix = (
                    f" (original recipients: {';'.join(original_recipients)})"
                )
                email.subject = f"{email.subject}{subject_suffix}"

                email.to = self.admin_emails
                email.bcc = []
                email.cc = []

                email.extra_headers["X-Forwarded-To-Admins"] = "True"

        return super().send_messages(email_messages)
