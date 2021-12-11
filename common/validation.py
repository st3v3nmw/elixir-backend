import json

from common.payload import ErrorCode


def validate_post_data(request_data, required_fields):
    try:
        request_data = json.loads(request_data)
    except json.JSONDecodeError:
        return False, {}, {"data": {}, "message": "Please provide valid JSON."}

    missing_fields = {}
    for field in required_fields:
        if field not in request_data:
            missing_fields[field] = ErrorCode.FIELD_REQUIRED

    return (
        len(missing_fields) == 0,
        request_data,
        {"data": missing_fields, "message": ""},
    )
