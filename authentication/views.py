"""This module houses API endpoints for the authentication app."""

from datetime import timedelta
import os

import jwt
from django.contrib.auth import authenticate
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import NextOfKin, User
from common.middleware import require_roles, require_service
from common.payload import (
    create_error_payload,
    ErrorCode,
    create_success_payload,
)
from common.utils import create, validate_post_data
from index.models import Practitioner


@csrf_exempt
@require_POST
@require_service("AUTH")
def register_user(request):
    """Register a user."""
    return create(User, request)


@csrf_exempt
@require_POST
@require_service("AUTH")
def login(request):
    """Authenticate a user and return a JWT access token."""
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
        roles = ["PATIENT"]
        # check if user is a practitioner
        try:
            practitioner = Practitioner.objects.get(user=user)
            roles.append("PRACTITIONER")
            roles.append(practitioner.type)
        except Practitioner.DoesNotExist:
            pass

        claims = {
            "sub": str(user.uuid),
            "iat": now.timestamp(),
            "exp": (
                now + timedelta(seconds=31556926)  # one solar year lol
            ).timestamp(),
            "roles": " ".join(roles),
        }
        token = jwt.encode(claims, os.environ["JWT_PRIVATE_KEY"], algorithm="RS384")
        return create_success_payload(
            {"token": token, "user": user.serialize()},
            message="Login successful.",
        )
    else:
        return create_error_payload({"message": ErrorCode.LOGIN_FAILED})


@require_GET
@require_service("AUTH")
def get_public_key(request):
    """Return the Auth server's public key."""
    return create_success_payload(
        {"algorithm": "RS384", "public_key": os.environ["JWT_PUBLIC_KEY"]}
    )


# @csrf_exempt
# @require_POST
# @require_service("AUTH")
# def reset_password(request):
#     pass


# @require_roles(["PATIENT"])
# @csrf_exempt
# @require_POST
# @require_service("AUTH")
# def change_password(request):
#     pass


@require_roles(["PATIENT"])
@csrf_exempt
@require_POST
@require_service("AUTH")
def register_next_of_kin(request):
    """Save a next of kin relationship."""
    return create(NextOfKin, request)
