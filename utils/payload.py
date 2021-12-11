from enum import Enum
from functools import partial

from django.http import JsonResponse


class ResponseType(str, Enum):
    SUCCESS = "success"
    ERROR = "error"


class ErrorCode(str, Enum):
    FIELD_REQUIRED = "field_required"
    UNIQUE_KEY_VIOLATION = "unique_key_violation"


def __create_response_payload(response_type: ResponseType, data, message=""):
    return JsonResponse({"status": response_type, "data": data, "message": message})


create_success_payload = partial(__create_response_payload, ResponseType.SUCCESS)
create_error_payload = partial(__create_response_payload, ResponseType.ERROR)
