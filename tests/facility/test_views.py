"""Tests for facility app views."""

import json

from django.test import Client
import pytest

from facility.models import ICD10, ICD10Category


@pytest.mark.django_db
def test_search_icd10(practitioner_fixture, doctor_auth_token_fixture):
    """Test searching for ICD10s."""
    unknown_fever_cat = ICD10Category.objects.create(
        code="R50", title="Fever of other and unknown origin"
    )
    drug_induced_fever = ICD10.objects.create(
        code="R502", description="Drug induced fever", category=unknown_fever_cat
    )

    cholera_cat = ICD10Category.objects.create(code="A00", title="Cholera")
    cholera_unspecified = ICD10.objects.create(
        code="A009", description="Cholera, unspecified", category=cholera_cat
    )

    typhoid_cat = ICD10Category.objects.create(code="A010", title="Typhoid fever")
    typhoid_pneumonia = ICD10.objects.create(
        code="A0103", description="Typhoid pneumonia", category=typhoid_cat
    )

    # Search with code description
    client = Client()
    response = client.post(
        "/api/facility/icd10/search/",
        {
            "query": "fever",
        },
        HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        content_type="application/json",
    )
    codes = json.loads(response.content)["data"]

    assert len(codes) == 2
    assert drug_induced_fever.serialize() in codes
    assert typhoid_pneumonia.serialize() in codes

    # Search with code
    client = Client()
    response = client.post(
        "/api/facility/icd10/search/",
        {
            "query": "A009",
        },
        HTTP_AUTHORIZATION=f"Bearer {doctor_auth_token_fixture}",
        content_type="application/json",
    )
    codes = json.loads(response.content)["data"]

    assert codes == [cholera_unspecified.serialize()]
