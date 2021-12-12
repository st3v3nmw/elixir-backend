import os
import jwt
from functools import wraps

from common.payload import create_error_payload, ErrorCode
from common.utils import parametrized


@parametrized
def require_roles(fn, roles):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    wrapper.required_roles = roles
    return wraps(fn)(wrapper)


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        required_roles = getattr(view_func, "required_roles", [])
        if len(required_roles) == 0:
            return None

        token = request.META.get("HTTP_AUTHORIZATION")

        print(token)

        if token is None:
            return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)

        try:
            decoded_token = jwt.decode(
                token[7:], os.environ["JWT_PUBLIC_KEY"], algorithms=["RS384"]
            )
        except jwt.exceptions.DecodeError:
            return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)

        print(decoded_token)

        tokens_roles = decoded_token["roles"].split(" ")
        for required_role in required_roles:
            if required_role in tokens_roles:
                request.token = decoded_token
                return None

        print("yey")

        return create_error_payload({}, message=ErrorCode.UNAUTHORIZED, status=401)
