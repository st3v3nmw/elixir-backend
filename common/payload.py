"""This module houses common methods associated with API payloads."""

from enum import Enum
from functools import partial

from django.http import JsonResponse


class ResponseType(str, Enum):
    """Enumeration for API response types."""

    SUCCESS = "success"
    ERROR = "error"


class ErrorCode(str, Enum):
    """Enumeration for API error codes."""

    FIELD_REQUIRED = "field_required"
    LOGIN_FAILED = "login_failed"
    DOES_NOT_EXIST = "does_not_exist"
    UNAUTHORIZED = "unauthorized"


def __create_response_payload(
    response_type: ResponseType, data={}, message="", status=200
):
    """Create an API response (both Success & Error response types)."""
    return JsonResponse(
        {"status": response_type, "data": data, "message": message}, status=status
    )


create_success_payload = partial(__create_response_payload, ResponseType.SUCCESS)
create_error_payload = partial(__create_response_payload, ResponseType.ERROR)
