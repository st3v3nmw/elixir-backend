"""Tests for common utils."""

from common.utils import validate_post_data


def test_validation_malformed_json():
    """Test validation of malformed POST JSON."""
    is_valid, request_data, debug_data = validate_post_data(
        "{first_name: 'Jane' }}", ["first_name", "last_name"]
    )
    assert is_valid is False
    assert request_data == {}
    assert debug_data == {
        "data": {},
        "message": "Please provide valid JSON.",
    }
