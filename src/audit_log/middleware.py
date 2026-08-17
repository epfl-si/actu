import contextvars

current_user = contextvars.ContextVar("current_user", default=None)


class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = (
            request.user
            if hasattr(request, "user") and request.user.is_authenticated
            else None
        )
        token = current_user.set(user)

        response = self.get_response(request)

        current_user.reset(token)
        return response
