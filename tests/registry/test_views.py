import json

import pytest
from django.test import Client
from model_bakery import baker

from authentication.models import User
from registry.models import Facility


@pytest.mark.django_db
def test_list_facilities(patient_auth_token_fixture):
    for _ in range(4):
        baker.make(Facility)

    client = Client()
    response_json = json.loads(
        client.get(
            "/api/registry/facilities/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json["status"] == "success"
    assert len(response_json["data"]) == 4


@pytest.mark.django_db
def test_get_facility(clinic_fixture, patient_auth_token_fixture):
    client = Client()
    response_json = json.loads(
        client.get(
            f"/api/registry/facilities/{clinic_fixture.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json == {
        "status": "success",
        "data": {
            "uuid": "35d7d0c0-5126-4823-85bc-607e1ef3bfda",
            "name": "Felicity Clinic",
            "county": "NAIROBI",
            "region": "Nairobi",
            "type": "HOSP",
            "location": "1 Rosslyn Close",
            "email": "felicity@example",
            "phone_number": "+254712345678",
            "address": "P.O. BOX 1 - 10100",
            "api_base_url": "http://localhost/api/",
            "date_joined": response_json["data"]["date_joined"],
            "is_active": True,
        },
        "message": "",
    }


@pytest.mark.django_db
def test_get_facility_error404(patient_auth_token_fixture):
    client = Client()
    response_json = json.loads(
        client.get(
            "/api/registry/facilities/c8db9bda-c4cb-4c8e-a343-d19ea17f4875/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json == {
        "status": "error",
        "data": {},
        "message": "does_not_exist",
    }


@pytest.mark.django_db
def test_register_practitioner(practitioner_fixture, doctor_auth_token_fixture):
    client = Client()

    doc2 = baker.make(User)

    response = client.post(
        "/api/registry/practitioners/new/",
        {
            "user_id": str(doc2.uuid),
            "type": "PHYSICIAN",
        },
        HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        content_type="application/json",
    )
    response_json = json.loads(response.content)

    assert response_json == {
        "status": "success",
        "data": {
            "uuid": response_json["data"]["uuid"],
            "user_id": str(doc2.uuid),
            "type": "PHYSICIAN",
            "employment_history": [],
        },
        "message": "Created successfully.",
    }


@pytest.mark.django_db
def test_register_tenure(
    practitioner_fixture, clinic_fixture, doctor_auth_token_fixture
):
    client = Client()

    response = client.post(
        "/api/registry/practitioners/tenures/new/",
        {
            "practitioner_id": practitioner_fixture.uuid,
            "facility_id": clinic_fixture.uuid,
            "start": "2011-01-01",
        },
        HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        content_type="application/json",
    )
    response_json = json.loads(response.content)

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
def test_get_practitioner(
    practitioner_fixture, tenure_fixture, patient_auth_token_fixture
):
    client = Client()

    response_json = json.loads(
        client.get(
            f"/api/registry/practitioners/{practitioner_fixture.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json == {
        "status": "success",
        "data": {
            "uuid": response_json["data"]["uuid"],
            "user_id": practitioner_fixture.user_id,
            "type": "PHYSICIAN",
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
