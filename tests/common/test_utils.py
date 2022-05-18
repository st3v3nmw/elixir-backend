"""Tests for common utils."""

import json

from django.test import Client


def test_validation_malformed_json():
    """Test validation of malformed POST JSON."""
    client = Client()
    response = client.post(
        "/api/auth/register/",
        "{first_name: 'Jane' }}",
        content_type="application/json",
    )
    assert json.loads(response.content) == {
        "data": {},
        "message": "Please provide valid JSON.",
        "status": "error",
    }
