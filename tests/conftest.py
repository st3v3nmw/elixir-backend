import pytest

from authentication.models import User


# authentication app


@pytest.fixture
def patient_default_fields_fixture():
    defaults = {
        "uuid": "c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "country": "KE",
        "national_id": "12345",
        "gender": "MALE",
        "date_of_birth": "2000-12-07",
        "date_joined": "2021-12-07 20:27:21.693131+00:00",
    }
    return defaults


@pytest.fixture
def patient_fixture(patient_default_fields_fixture) -> User:
    return User.objects.create_user(
        "john@example.com", "some-password", **patient_default_fields_fixture
    )
