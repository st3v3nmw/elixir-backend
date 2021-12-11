import pytest

from authentication.models import User

pytestmark = pytest.mark.django_db


def test_user(user_fixture: User) -> None:
    assert str(user_fixture) == "Jane Doe"
