from common.payload import create_error_payload, ErrorCode


def error404(request, exception):
    return create_error_payload({}, ErrorCode.DOES_NOT_EXIST, status=404)
