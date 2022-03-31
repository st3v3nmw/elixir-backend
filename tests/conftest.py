"""Test fixtures."""

import json

from django.test import Client
import pytest

from authentication.models import User
from index.models import Facility, Practitioner, Tenure


# authentication app


@pytest.fixture
def patient_default_fields_fixture():
    """Return default fields for a patient fixture."""
    return {
        "uuid": "c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "national_id": "12345",
        "gender": "MALE",
        "date_of_birth": "2000-12-07",
        "address": "1-10100 Nyeri",
    }


@pytest.fixture
def patient_fixture(patient_default_fields_fixture) -> User:
    """Return an instantiated patient fixture."""
    return User.objects.create_user(
        "john@example.com", "some-password", **patient_default_fields_fixture
    )


@pytest.fixture
def patient_auth_token_fixture(patient_fixture) -> str:
    """Return an auth token fixture for a patient."""
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


# index app


@pytest.fixture
def clinic_default_fields_fixture():
    """Return default fields for a Facility fixture."""
    return {
        "uuid": "35d7d0c0-5126-4823-85bc-607e1ef3bfda",
        "name": "Felicity Clinic",
        "county": "NAIROBI",
        "location": "1 Rosslyn Close",
        "type": "HOSP",
        "email": "felicity@example",
        "phone_number": "+254712345678",
        "address": "P.O. BOX 1 - 10100",
        "api_base_url": "http://localhost/api/",
    }


@pytest.fixture
def clinic_fixture(clinic_default_fields_fixture) -> Facility:
    """Return an instantiated Facility fixture."""
    return Facility.objects.create(**clinic_default_fields_fixture)


@pytest.fixture
def doctor_fixture() -> User:
    """Return an instantiated practitioner/User fixture."""
    doctor_default_fields = {
        "uuid": "601e357c-91e5-4d28-b830-5462590adb3c",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "national_id": "67890",
        "gender": "FEMALE",
        "date_of_birth": "1990-12-12",
        "address": "1 Rosslyn Close, Westlands",
    }
    return User.objects.create_user(
        "jane@example.com", "some-password", **doctor_default_fields
    )


@pytest.fixture
def doctor_auth_token_fixture(doctor_fixture) -> str:
    """Return an auth token fixture for a practitioner."""
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
def practitioner_fixture(doctor_fixture) -> Practitioner:
    """Return an instantiated Practitioner fixture."""
    return Practitioner.objects.create(user=doctor_fixture, type="PHYSICIAN")


@pytest.fixture
def tenure_fixture(practitioner_fixture, clinic_fixture) -> Tenure:
    """Return an instantiated Tenure fixture."""
    return Tenure.objects.create(
        practitioner=practitioner_fixture,
        facility=clinic_fixture,
        start="2011-01-01",
        end="2013-11-05",
    )
