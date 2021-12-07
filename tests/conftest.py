import pytest

from authentication.models import User

# authentication app


@pytest.fixture
def user_default_fields_fixture():
    defaults = {
        "uuid": "c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "country": "KE",
        "national_id": "12345",
        "gender": "FEMALE",
        "date_of_birth": "2000-12-07",
        "date_joined": "2021-12-07 20:27:21.693131+00:00",
    }
    return defaults


@pytest.fixture
def normal_user_fixture(user_default_fields_fixture) -> User:
    return User.objects.create_user(
        "user@example.com", "some-password", **user_default_fields_fixture
    )


@pytest.fixture
def admin_fixture(user_default_fields_fixture) -> User:
    return User.objects.create_superuser(
        "user@example.com", "some-password", **user_default_fields_fixture
    )
