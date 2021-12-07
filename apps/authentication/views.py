import json

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import User
from utils.validation import validate_post_data
from utils.payload import ResponseType, create_response_payload, serialize_object


@csrf_exempt
@require_POST
def register_user(request):
    request_data = json.loads(request.body)
    valid_data, missing_fields = validate_post_data(request_data, model=User)
    if not valid_data:
        return create_response_payload(ResponseType.FAIL, data=missing_fields)

    user = User.objects.create_user(**request_data)
    return create_response_payload(
        ResponseType.SUCCESS, data=serialize_object(user, User)
    )


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
