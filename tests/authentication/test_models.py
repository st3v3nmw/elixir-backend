import pytest

from authentication.models import User

pytestmark = pytest.mark.django_db


def test_user_str_repr(patient_fixture: User) -> None:
    assert str(patient_fixture) == "John Doe (c8db9bda-c4cb-4c8e-a343-d19ea17f4875)"
