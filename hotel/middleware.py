from .utils import ensure_session_defaults
class SessionDefaultsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        ensure_session_defaults(request)
        response = self.get_response(request)
        return response
