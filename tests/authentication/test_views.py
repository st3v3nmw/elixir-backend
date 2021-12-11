import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


def test_login_endpoint_missing_fields() -> None:
    client = Client()

    # missing fields
    response = client.post(
        "/api/auth/register",
        {
            "email": "adelaide@example.com",
            "first_name": "Adelaide",
            "last_name": "Doe",
        },
        content_type="application/json",
    )
    assert json.loads(response.content) == {
        "status": "error",
        "data": {
            "password": "field_required",
            "country": "field_required",
            "national_id": "field_required",
            "gender": "field_required",
            "date_of_birth": "field_required",
            "phone_number": "field_required",
        },
        "message": "",
    }


def test_login_endpoint_proper_data(user_default_fields_fixture) -> None:
    client = Client()

    user_default_fields_fixture["email"] = "jane@example.com"
    user_default_fields_fixture["password"] = "some-password"
    response = client.post(
        "/api/auth/register",
        user_default_fields_fixture,
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    user_default_fields_fixture["date_joined"] = response_json["data"]["date_joined"]
    user_default_fields_fixture["is_active"] = "True"
    user_default_fields_fixture.pop("password")
    assert response_json == {
        "status": "success",
        "data": user_default_fields_fixture,
        "message": "User created successfully.",
    }

    # attempt to register user with the same data
    user_default_fields_fixture["password"] = "some-password"
    response = client.post(
        "/api/auth/register",
        user_default_fields_fixture,
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    assert response_json == {
        "status": "error",
        "data": {"email": "unique_key_violation"},
        "message": "",
    }
