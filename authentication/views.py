import json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import User
from utils.payload import (
    create_success_payload,
    create_error_payload,
)


@csrf_exempt
@require_POST
def register_user(request):
    request_data = json.loads(request.body)
    valid_data, missing_fields = User.validate_post_data(request_data)
    if not valid_data:
        return create_error_payload(missing_fields)

    success, result = User.save_wrapper(request_data)
    if success:
        return create_success_payload(
            result.serialize(), message="User created successfully."
        )
    else:
        return create_error_payload(result)


# @csrf_exempt
# @require_POST
# def login(request):
#     pass


# @csrf_exempt
# @require_POST
# def reset_password(request):
#     pass


# @csrf_exempt
# @require_POST
# def change_password(request):
#     pass
