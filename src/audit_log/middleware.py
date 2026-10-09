from contextvars import ContextVar

current_user = ContextVar("current_user", default=None)
current_request = ContextVar("current_request", default=None)


class AuditUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        user_token = current_user.set(user)
        request_token = current_request.set(request)

        try:
            response = self.get_response(request)
        finally:
            current_user.reset(user_token)
            current_request.reset(request_token)

        return response
