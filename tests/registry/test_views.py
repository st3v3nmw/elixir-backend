import json

import pytest
from django.test import Client
from model_bakery import baker

from registry.models import HealthFacility


@pytest.mark.django_db
def test_list_facilities():
    for _ in range(4):
        baker.make(HealthFacility)

    client = Client()
    json_response = json.loads(client.get("/api/registry/facilities/").content)

    assert json_response["status"] == "success"
    assert len(json_response["data"]) == 4


@pytest.mark.django_db
def test_get_facility(clinic_fixture):
    client = Client()
    json_response = json.loads(
        client.get(f"/api/registry/facilities/{clinic_fixture.uuid}/").content
    )

    assert json_response == {
        "status": "success",
        "data": {
            "uuid": "35d7d0c0-5126-4823-85bc-607e1ef3bfda",
            "name": "Felicity Clinic",
            "region": "NAIROBI",
            "county": "NAIROBI",
            "location": "1 Rosslyn Close",
            "email": "felicity@example",
            "phone_number": "+254712345678",
            "address": "P.O. BOX 1 - 10100",
            "api_base_url": "http://localhost/api",
            "date_joined": json_response["data"]["date_joined"],
            "is_active": True,
        },
        "message": "",
    }
