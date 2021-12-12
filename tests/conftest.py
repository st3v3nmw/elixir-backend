import json

import pytest
from django.test import Client

from authentication.models import User
from registry.models import HealthFacility, HealthWorker, Tenure


# authentication app


@pytest.fixture
def patient_default_fields_fixture():
    return {
        "uuid": "c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        "first_name": "John",
        "surname": "Doe",
        "phone_number": "+254712345678",
        "national_id": "12345",
        "gender": "MALE",
        "date_of_birth": "2000-12-07",
    }


@pytest.fixture
def patient_fixture(patient_default_fields_fixture) -> User:
    return User.objects.create_user(
        "john@example.com", "some-password", **patient_default_fields_fixture
    )


@pytest.fixture
def patient_auth_token_fixture(patient_fixture) -> str:
    client = Client()
    response = client.post(
        "/api/auth/login/",
        {
            "email": patient_fixture.email,
            "password": "some-password",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    return response_json["data"]["token"]


# registry app


@pytest.fixture
def clinic_default_fields_fixture():
    return {
        "uuid": "35d7d0c0-5126-4823-85bc-607e1ef3bfda",
        "name": "Felicity Clinic",
        "region": "NAIROBI",
        "county": "NAIROBI",
        "location": "1 Rosslyn Close",
        "email": "felicity@example",
        "phone_number": "+254712345678",
        "address": "P.O. BOX 1 - 10100",
        "api_base_url": "http://localhost/api/",
    }


@pytest.fixture
def clinic_fixture(clinic_default_fields_fixture) -> HealthFacility:
    return HealthFacility.objects.create(**clinic_default_fields_fixture)


@pytest.fixture
def doctor_fixture() -> User:
    doctor_default_fields = {
        "uuid": "601e357c-91e5-4d28-b830-5462590adb3c",
        "first_name": "Jane",
        "surname": "Doe",
        "phone_number": "+254712345678",
        "national_id": "67890",
        "gender": "FEMALE",
        "date_of_birth": "1990-12-12",
    }
    return User.objects.create_user(
        "jane@example.com", "some-password", **doctor_default_fields
    )


@pytest.fixture
def doctor_auth_token_fixture(doctor_fixture) -> str:
    client = Client()
    response = client.post(
        "/api/auth/login/",
        {
            "email": doctor_fixture.email,
            "password": "some-password",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    return response_json["data"]["token"]


@pytest.fixture
def health_worker_fixture(doctor_fixture) -> HealthWorker:
    return HealthWorker.objects.create(user=doctor_fixture, type="DOCTOR")


@pytest.fixture
def tenure_fixture(health_worker_fixture, clinic_fixture) -> Tenure:
    return Tenure.objects.create(
        health_worker=health_worker_fixture,
        facility=clinic_fixture,
        start="2011-01-01",
        end="2013-11-05",
    )
