"""Tests for authentication views."""

import json
import os

from django.test import Client
import jwt
import pytest


def test_user_registration_endpoint_missing_fields() -> None:
    """Test user registration using missng fields."""
    client = Client()

    response = client.post(
        "/api/auth/register/",
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
            "national_id": "field_required",
            "gender": "field_required",
            "date_of_birth": "field_required",
            "phone_number": "field_required",
        },
        "message": "",
    }


@pytest.mark.django_db
def test_user_registration_endpoint_proper_data(patient_default_fields_fixture) -> None:
    """Test user registration using a properly populated payload."""
    client = Client()

    patient_default_fields_fixture["email"] = "john@example.com"
    patient_default_fields_fixture["password"] = "some-password"
    response = client.post(
        "/api/auth/register/",
        patient_default_fields_fixture,
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    patient_default_fields_fixture["date_joined"] = response_json["data"]["date_joined"]
    patient_default_fields_fixture["is_active"] = True
    patient_default_fields_fixture.pop("password")
    patient_default_fields_fixture["records"] = []
    patient_default_fields_fixture["relatives"] = []
    assert response_json == {
        "status": "success",
        "data": patient_default_fields_fixture,
        "message": "Created successfully.",
    }

    # attempt to register user with the same data
    patient_default_fields_fixture["password"] = "some-password"
    patient_default_fields_fixture.pop("records")
    patient_default_fields_fixture.pop("relatives")
    response = client.post(
        "/api/auth/register/",
        patient_default_fields_fixture,
        content_type="application/json",
    )
    patient_default_fields_fixture["records"] = []
    patient_default_fields_fixture["relatives"] = []
    response_json = json.loads(response.content)
    assert response_json == {
        "status": "error",
        "data": {},
        "message": (
            'duplicate key value violates unique constraint "authentication_user_pkey"\n'
            "DETAIL:  Key (uuid)=(c8db9bda-c4cb-4c8e-a343-d19ea17f4875) already exists.\n"
        ),
    }


@pytest.mark.django_db
def test_patient_login(patient_fixture):
    """Test patient login."""
    client = Client()

    # login failure
    response = client.post(
        "/api/auth/login/",
        {
            "email": "john@example.com",
            "password": "wrong-password",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    assert response_json == {
        "status": "error",
        "data": {"message": "login_failed"},
        "message": "",
    }

    # login success
    response = client.post(
        "/api/auth/login/",
        {
            "email": "john@example.com",
            "password": "some-password",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    assert response_json["status"] == "success"
    decoded_token = jwt.decode(
        response_json["data"]["token"],
        os.environ["JWT_PUBLIC_KEY"],
        algorithms=["RS384"],
    )
    assert decoded_token["sub"] == patient_fixture.uuid
    assert decoded_token["roles"] == "PATIENT"
    assert response_json["data"]["user"] == patient_fixture.serialize()


@pytest.mark.django_db
def test_physician_login_roles(doctor_fixture, practitioner_fixture):
    """Test physician login & verify token roles."""
    client = Client()
    response = client.post(
        "/api/auth/login/",
        {
            "email": "jane@example.com",
            "password": "some-password",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    assert response_json["status"] == "success"
    decoded_token = jwt.decode(
        response_json["data"]["token"],
        os.environ["JWT_PUBLIC_KEY"],
        algorithms=["RS384"],
    )
    assert decoded_token["sub"] == doctor_fixture.uuid
    assert decoded_token["roles"] == "PATIENT PRACTITIONER PHYSICIAN"


def test_get_public_key():
    """Test fetching the AUTH server's public key."""
    client = Client()
    response_json = json.loads(client.get("/api/auth/public-key/").content)
    assert response_json["data"]["algorithm"] == "RS384"
    assert response_json["data"]["public_key"] == os.environ["JWT_PUBLIC_KEY"]
