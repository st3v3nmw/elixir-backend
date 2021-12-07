from enum import Enum

from django.http import JsonResponse


class ResponseType(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"
    ERROR = "error"


def create_response_payload(response_type: ResponseType, data={}, message=""):
    payload = {"status": response_type}
    if response_type == ResponseType.SUCCESS or response_type == ResponseType.FAIL:
        payload["data"] = data
    else:
        payload["message"] = message
    print(payload)
    return JsonResponse(payload)


def serialize_object(object, model):
    object = object.__dict__
    result = {}
    for field in model.SERIALIZATION_FIELDS:
        result[field] = str(object[field])
    return result
