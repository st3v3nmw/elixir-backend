import pytest
from model_bakery import baker
from unittest.mock import patch

from apps.authentication.models import User
from utils.payload import ResponseType, create_response_payload, serialize_object

PATCH_PATH = "utils.payload."


@pytest.fixture
def user():
    user = baker.make(
        User,
        uuid="c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        email="user@example.com",
        first_name="Jane",
        last_name="Doe",
        phone_number="+254712345678",
        country="KE",
        national_id="12345",
        gender="FEMALE",
        date_of_birth="2000-12-07",
    )
    user.date_joined = "2021-12-07 20:27:21.693131+00:00"
    return user


@patch(PATCH_PATH + "JsonResponse")
def test_create_success_payload(mock_json_response):
    create_response_payload(ResponseType.SUCCESS, data={})
    mock_json_response.assert_called_with({"status": ResponseType.SUCCESS, "data": {}})


@patch(PATCH_PATH + "JsonResponse")
def test_create_error_payload(mock_json_response):
    msg: str = "Unable to communicate with the database"
    create_response_payload(ResponseType.ERROR, message=msg)
    mock_json_response.assert_called_once_with(
        {"status": ResponseType.ERROR, "message": msg}
    )


@pytest.mark.django_db
def test_serialize_object(user):
    expected = {
        "uuid": "c8db9bda-c4cb-4c8e-a343-d19ea17f4875",
        "email": "user@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+254712345678",
        "country": "KE",
        "national_id": "12345",
        "gender": "FEMALE",
        "date_of_birth": "2000-12-07",
        "date_joined": "2021-12-07 20:27:21.693131+00:00",
        "is_active": "True",
    }
    result = serialize_object(user, User)
    assert expected == result
