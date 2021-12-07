import pytest

from unittest.mock import patch

from authentication.models import User
from utils.payload import ResponseType, create_response_payload, serialize_object

PATCH_PATH = "utils.payload."


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
def test_serialize_object(normal_user_fixture, user_default_fields_fixture):
    expected = user_default_fields_fixture
    expected["date_joined"] = str(normal_user_fixture.date_joined)
    expected["email"] = "user@example.com"
    expected["is_active"] = "True"

    result = serialize_object(normal_user_fixture, User)
    assert expected == result
