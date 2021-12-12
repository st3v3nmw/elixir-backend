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
    response_json = json.loads(client.get("/api/registry/facilities/").content)

    assert response_json["status"] == "success"
    assert len(response_json["data"]) == 4


@pytest.mark.django_db
def test_get_facility(clinic_fixture):
    client = Client()
    response_json = json.loads(
        client.get(f"/api/registry/facilities/{clinic_fixture.uuid}/").content
    )

    assert response_json == {
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
            "date_joined": response_json["data"]["date_joined"],
            "is_active": True,
        },
        "message": "",
    }


@pytest.mark.django_db
def test_register_health_worker(doctor_fixture):
    client = Client()

    response = client.post(
        "/api/registry/workers/new/",
        {
            "user_id": doctor_fixture.uuid,
            "type": "DOCTOR",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)

    assert response_json == {
        "status": "success",
        "data": {
            "uuid": response_json["data"]["uuid"],
            "user_id": doctor_fixture.uuid,
            "type": "DOCTOR",
            "employment_history": [],
        },
        "message": "Created successfully.",
    }


@pytest.mark.django_db
def test_register_tenure(health_worker_fixture, clinic_fixture):
    client = Client()

    response = client.post(
        "/api/registry/workers/tenures/new/",
        {
            "health_worker_id": health_worker_fixture.uuid,
            "facility_id": clinic_fixture.uuid,
            "start": "2011-01-01",
        },
        content_type="application/json",
    )
    response_json = json.loads(response.content)
    print(response_json)

    assert response_json == {
        "status": "success",
        "data": {
            "uuid": response_json["data"]["uuid"],
            "facility_id": clinic_fixture.uuid,
            "start": "2011-01-01",
            "end": None,
        },
        "message": "Created successfully.",
    }


@pytest.mark.django_db
def test_get_health_worker(health_worker_fixture, tenure_fixture):
    client = Client()

    response_json = json.loads(
        client.get(f"/api/registry/workers/{health_worker_fixture.uuid}/").content
    )

    print(response_json)
    assert response_json == {
        "status": "success",
        "data": {
            "uuid": response_json["data"]["uuid"],
            "user_id": health_worker_fixture.user_id,
            "type": "DOCTOR",
            "employment_history": [
                {
                    "uuid": str(tenure_fixture.uuid),
                    "facility_id": tenure_fixture.facility_id,
                    "start": "2011-01-01",
                    "end": "2013-11-05",
                }
            ],
        },
        "message": "",
    }
