"""Tests for index app views."""

import json

from django.test import Client
from model_bakery import baker
import pytest

from authentication.models import NextOfKin, User
from index.models import Facility


@pytest.mark.django_db
def test_list_facilities(patient_auth_token_fixture):
    """Test listing of all facilities."""
    for _ in range(4):
        baker.make(Facility)

    client = Client()
    response_json = json.loads(
        client.get(
            "/api/index/facilities/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json["status"] == "success"
    assert len(response_json["data"]) == 4


@pytest.mark.django_db
def test_get_facility(clinic_fixture, patient_auth_token_fixture):
    """Test fetching a particular facility."""
    client = Client()
    response_json = json.loads(
        client.get(
            f"/api/index/facilities/{clinic_fixture.uuid}/",
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
    """Test fetching a non-existent facility."""
    client = Client()
    response_json = json.loads(
        client.get(
            "/api/index/facilities/c8db9bda-c4cb-4c8e-a343-d19ea17f4875/",
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
    """Test registration of a practitioner."""
    client = Client()

    doc2 = baker.make(User)

    response = client.post(
        "/api/index/practitioners/new/",
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
    """Test registration of a practitioner's tenure."""
    client = Client()

    response = client.post(
        "/api/index/practitioners/tenures/new/",
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
    """Test fetching a practitioner."""
    client = Client()

    response_json = json.loads(
        client.get(
            f"/api/index/practitioners/{practitioner_fixture.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {patient_auth_token_fixture}",
        ).content
    )

    assert response_json == {
        "status": "success",
        "data": {
            "fhir": {
                "resourceType": "Practitioner",
                "active": True,
                "address": {"text": "1 Rosslyn Close, Westlands"},
                "birthDate": "1990-12-12",
                "communication": [{"language": "en", "preferred": True}],
                "gender": "female",
                "identifier": [
                    response_json["data"]["extra"]["uuid"],
                    practitioner_fixture.user_id,
                ],
                "name": [
                    {
                        "family": "Doe",
                        "given": "Jane",
                        "text": "Jane Doe",
                        "use": "official",
                    }
                ],
                "qualification": [{"code": "PHYSICIAN"}],
                "telecom": [{"system": "phone", "value": "+254712345678"}],
            },
            "extra": {
                "uuid": response_json["data"]["extra"]["uuid"],
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
        },
        "message": "",
    }


@pytest.mark.django_db
def test_get_patient(
    practitioner_fixture, doctor_fixture, doctor_auth_token_fixture, patient_fixture
):
    """Test the get patient as FHIR function."""
    NextOfKin.objects.create(
        user=patient_fixture, next_of_kin=doctor_fixture, relationship="PARENT"
    )

    client = Client()
    response_json = json.loads(
        client.get(
            f"/api/index/patients/{patient_fixture.uuid}/",
            HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        ).content
    )

    assert response_json == {
        "status": "success",
        "data": {
            "resourceType": "Patient",
            "identifier": ["c8db9bda-c4cb-4c8e-a343-d19ea17f4875"],
            "name": [
                {
                    "use": "official",
                    "text": "John Doe",
                    "family": "Doe",
                    "given": "John",
                }
            ],
            "telecom": [{"system": "phone", "value": "+254712345678"}],
            "gender": "male",
            "birthDate": "2000-12-07",
            "address": {"text": "1-10100 Nyeri"},
            "contact": [
                {
                    "gender": "female",
                    "name": "Jane Doe",
                    "relationship": "PARENT",
                    "telecom": {"system": "phone", "value": "+254712345678"},
                }
            ],
            "communication": [{"language": "en", "preferred": True}],
            "active": True,
        },
        "message": "",
    }
