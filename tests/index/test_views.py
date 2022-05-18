"""Tests for index app views."""

import json

import pytest
from django.test import Client
from model_bakery import baker

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

    user = baker.make(User)

    response = client.post(
        "/api/index/practitioners/new/",
        {
            "user_id": str(user.uuid),
            "type": "PHYSICIAN",
        },
        HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        content_type="application/json",
    )
    response_json = json.loads(response.content)

    assert response_json == {
        "status": "success",
        "data": {
            "created": response_json["data"]["created"],
            "uuid": response_json["data"]["uuid"],
            "user_id": str(user.uuid),
            "user": user.serialize(),
            "type": "PHYSICIAN",
        },
        "message": "Created successfully.",
    }


@pytest.mark.django_db
def test_search_patient(
    practitioner_fixture, doctor_fixture, doctor_auth_token_fixture, patient_fixture
):
    """Test the get patient as FHIR function."""
    NextOfKin.objects.create(
        user=patient_fixture, next_of_kin=doctor_fixture, relationship="PARENT"
    )

    client = Client()
    response_json = json.loads(
        client.post(
            "/api/index/patients/search/",
            {"query": "John Doe"},
            HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
            content_type="application/json",
        ).content
    )

    assert response_json == {
        "status": "success",
        "data": [patient_fixture.serialize()],
        "message": "",
    }
