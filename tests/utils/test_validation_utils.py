from authentication.models import User
from utils.validation import validate_post_data


def test_validation_success_using_required_fields_list():
    fields = ["email", "country"]
    request_data = {"email": "user@example.com", "country": "KE"}
    valid, debug_data = validate_post_data(request_data, required_fields=fields)
    assert valid is True
    assert debug_data == {}


def test_missing_fields_validation_using_model():
    request_data = {"email": "user@example.com", "country": "KE"}
    valid, debug_data = validate_post_data(request_data, model=User)
    assert valid is False
    assert debug_data == {
        "password": "password is required",
        "first_name": "first_name is required",
        "last_name": "last_name is required",
        "national_id": "national_id is required",
        "gender": "gender is required",
        "date_of_birth": "date_of_birth is required",
        "phone_number": "phone_number is required",
    }
