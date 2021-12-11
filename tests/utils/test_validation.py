from utils.validation import validate_post_data


def test_validation_malformed_json():
    is_valid, request_data, debug_data = validate_post_data(
        "{first_name: 'Jane' }}", ["first_name", "last_name"]
    )
    assert is_valid is False
    assert request_data == {}
    assert debug_data == {
        "data": {},
        "message": "Please provide valid JSON.",
    }
