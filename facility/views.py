from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    HCPCS,
    ICD10,
    LOINC,
    ChargeItem,
    Encounter,
    Observation,
    Prescription,
    RxTerm,
    Visit,
)
from common.middleware import require_roles
from common.payload import create_error_payload, create_success_payload
from common.search import search_table
from common.utils import require_service
from common.validation import validate_post_data
from common.views import create


# Coding - Search


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_icd10(request):
    return search_table(ICD10, ["code", "description", "category__title"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_loinc(request):
    return search_table(LOINC, ["code", "component", "long_common_name"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_hcpcs(request):
    return search_table(HCPCS, ["code", "description"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_rxterm(request):
    return search_table(RxTerm, ["code", "name"], request)


# Visits


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_visit(request):
    return create(Visit, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_visit(request, visit_id):
    visit = get_object_or_404(Visit, uuid=visit_id)
    return create_success_payload(visit.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_visits(request, practitioner_id):
    visits = Visit.objects.filter(encounters__author_id=practitioner_id)
    return create_success_payload([visit.serialize() for visit in visits])


# Encounters


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_encounter(request):
    return create(Encounter, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_encounter(request, encounter_id):
    encounter = get_object_or_404(Encounter, uuid=encounter_id)
    return create_success_payload(encounter.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_encounters(request, practitioner_id):
    encounters = Encounter.objects.filter(author_id=practitioner_id)
    return create_success_payload([encounter.serialize() for encounter in encounters])


# Observations


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_observation(request):
    return create(Observation, request)


# Charge Items


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_charge_item(request):
    return create(ChargeItem, request)


# Prescriptions


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def create_prescription(request):
    return create(Prescription, request)
