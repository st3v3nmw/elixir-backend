import os
from datetime import timedelta

import jwt
from django.utils import timezone
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET

from .models import User
from common.payload import (
    ErrorCode,
    create_success_payload,
    create_error_payload,
)
from common.validation import validate_post_data


@csrf_exempt
@require_POST
def register_user(request):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, User.VALIDATION_FIELDS
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    success, result = User.save_wrapper(request_data)
    if success:
        return create_success_payload(
            result.serialize(), message="User created successfully."
        )
    else:
        return create_error_payload(result)


@csrf_exempt
@require_POST
def login(request):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, ["email", "password"]
    )
    if not is_valid:
        return create_error_payload(
            debug_data["data"], message=debug_data["message"]
        )  # pragma: no cover

    user = authenticate(email=request_data["email"], password=request_data["password"])
    if user is not None:
        now = timezone.now()
        claims = {
            "sub": str(user.uuid),
            "iat": now.timestamp(),
            "exp": (
                now + timedelta(seconds=31556926)  # one solar year lol
            ).timestamp(),
            "roles": "Patient",  # space separated list of roles
        }
        token = jwt.encode(claims, os.environ["JWT_PRIVATE_KEY"], algorithm="RS384")
        return create_success_payload(
            {
                "token": token,
                "algorithm": "RS384",
                "public_key": os.environ["JWT_PUBLIC_KEY"],
            },
            message="Login successful.",
        )
    else:
        return create_error_payload({"message": ErrorCode.LOGIN_FAILED})


@require_GET
def public_key(request):
    return create_success_payload(
        {"algorithm": "RS384", "public_key": os.environ["JWT_PUBLIC_KEY"]}
    )


# @csrf_exempt
# @require_POST
# def reset_password(request):
#     pass


# @csrf_exempt
# @require_POST
# def change_password(request):
#     pass
