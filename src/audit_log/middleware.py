from contextvars import ContextVar

current_user = ContextVar("current_user", default=None)
current_request = ContextVar("current_request", default=None)


class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        token = current_user.set(user)
        current_request.set(request)

        try:
            response = self.get_response(request)
        finally:
            current_user.reset(token)

        return response
