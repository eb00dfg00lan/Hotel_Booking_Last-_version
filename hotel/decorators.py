from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def require_roles(*allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.is_superuser and 'admin' in allowed_roles:
                return view_func(request, *args, **kwargs)
            role = request.session.get('role', None)
            if request.user.is_authenticated and role is None:
                role = 'guest'
            if role in allowed_roles:
                return view_func(request, *args, **kwargs)
            if not request.user.is_authenticated:
                return redirect('hotel:login')
            return HttpResponseForbidden('Forbidden: insufficient role')
        return _wrapped
    return decorator
