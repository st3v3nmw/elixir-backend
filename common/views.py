from common.payload import create_success_payload, create_error_payload, ErrorCode
from common.validation import validate_post_data


def create(request, model):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, model.POST_REQUIRED_FIELDS
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    success, result = model.save_wrapper(request_data)
    if success:
        return create_success_payload(
            result.serialize(), message="Created successfully."
        )
    else:
        return create_error_payload(result)


def error404(request, exception):
    return create_error_payload({}, ErrorCode.DOES_NOT_EXIST, status=404)
