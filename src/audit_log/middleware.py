from contextvars import ContextVar

current_user = ContextVar("current_user", default=None)


class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        token = current_user.set(user)

        try:
            response = self.get_response(request)
        finally:
            current_user.reset(token)

        return response
