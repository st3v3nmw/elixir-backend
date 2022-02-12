"""This module houses API endpoints for the facility app."""

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    ChargeItem,
    Encounter,
    HCPCS,
    ICD10,
    LOINC,
    Observation,
    Prescription,
    RxTerm,
    Visit,
)
from common.middleware import require_roles, require_service
from common.payload import create_success_payload
from common.utils import create, search_table


# Coding - Search


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_icd10(request):
    """Search for an ICD10 code."""
    return search_table(ICD10, ["code", "description", "category__title"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_loinc(request):
    """Search for a LOINC code."""
    return search_table(LOINC, ["code", "component", "long_common_name"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_hcpcs(request):
    """Search for a HCPCS code."""
    return search_table(HCPCS, ["code", "description"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_rxterm(request):
    """Search for a RxTerm code."""
    return search_table(RxTerm, ["code", "name"], request)


# Visits


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_visit(request):
    """Create a visit."""
    return create(Visit, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_visit(request, visit_id):
    """GET a visit."""
    visit = get_object_or_404(Visit, uuid=visit_id)
    return create_success_payload(visit.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_visits(request, practitioner_id):
    """List all visits a practitioner has been involved in."""
    visits = Visit.objects.filter(encounters__author_id=practitioner_id)
    return create_success_payload([visit.serialize() for visit in visits])


# Encounters


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_encounter(request):
    """Create an encounter."""
    return create(Encounter, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_encounter(request, encounter_id):
    """GET an encounter."""
    encounter = get_object_or_404(Encounter, uuid=encounter_id)
    return create_success_payload(encounter.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_encounters(request, practitioner_id):
    """List all encounters a practitioner has authored."""
    encounters = Encounter.objects.filter(author_id=practitioner_id)
    return create_success_payload([encounter.serialize() for encounter in encounters])


# Observations


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_observation(request):
    """Create an observation."""
    return create(Observation, request)


# Charge Items


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_charge_item(request):
    """Create a charge item."""
    return create(ChargeItem, request)


# Prescriptions


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_prescription(request):
    """Create a prescription."""
    return create(Prescription, request)
