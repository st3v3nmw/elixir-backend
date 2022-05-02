"""This module houses access control decorators & middleware."""

from functools import wraps
import jwt
import os

from common.payload import create_error_payload, ErrorCode
from common.utils import parameterized


@parameterized
def require_roles(fn, roles):
    """Ensure that the client has the necessary roles to access an API view."""

    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    wrapper.required_roles = roles
    return wraps(fn)(wrapper)


@parameterized
def require_service(fn, service):
    """Ensure that the server serving a request provides a specific service."""

    def wrapper(*args, **kwargs):
        if service not in os.environ["SERVER_SERVICES"].split(" "):
            raise Exception(f"{service} not supported on this server.")
        return fn(*args, **kwargs)

    return wrapper


class LoginRequiredMiddleware:
    """Middleware to extract user token (& roles) from a request."""

    def __init__(self, get_response):  # noqa
        self.get_response = get_response

    def __call__(self, request):  # noqa
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Extract user token (& roles) from a request."""
        required_roles = getattr(view_func, "required_roles", [])
        if len(required_roles) == 0:
            return None

        token = request.META.get("HTTP_AUTHORIZATION")

        if token is None:
            return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)

        try:
            decoded_token = jwt.decode(
                token[7:], os.environ["JWT_PUBLIC_KEY"], algorithms=["RS384"]
            )
            decoded_token['raw'] = token[7:]
        except jwt.exceptions.DecodeError:
            return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)

        tokens_roles = decoded_token["roles"].split(" ")
        for required_role in required_roles:
            if required_role in tokens_roles:
                request.token = decoded_token
                return None

        return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)
