import unittest
from io import StringIO

import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_registry_facility(clinic_default_fields_fixture):
    out = StringIO()
    fields = clinic_default_fields_fixture
    call_command(
        "register_facility",
        fields["name"],
        fields["region"],
        fields["county"],
        fields["location"],
        fields["email"],
        fields["phone_number"],
        fields["address"],
        fields["api_base_url"],
        stdout=out,
    )

    tc = unittest.TestCase()
    tc.assertIn("Health Facility registered (UUID: ", out.getvalue())

    # attempt to re-register
    call_command(
        "register_facility",
        fields["name"],
        fields["region"],
        fields["county"],
        fields["location"],
        fields["email"],
        fields["phone_number"],
        fields["address"],
        fields["api_base_url"],
        stdout=out,
    )
    tc.assertIn(
        f"DETAIL:  Key (email)=({fields['email']}) already exists.", out.getvalue()
    )
