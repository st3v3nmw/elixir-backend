import pytest

from authentication.models import User
from registry.models import HealthFacility


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
        "api_base_url": "http://localhost/api",
    }


@pytest.fixture
def clinic_fixture(clinic_default_fields_fixture) -> HealthFacility:
    return HealthFacility.objects.create(**clinic_default_fields_fixture)
