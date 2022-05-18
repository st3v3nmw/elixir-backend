"""This module houses API endpoints for the facility app."""

import os

from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from common.middleware import require_roles, require_service
from common.payload import create_success_payload
from common.utils import create, search_table

from .models import HCPCS, ICD10, LOINC, RxTerm, Visit

index_base_url = (
    "http://"
    + os.environ["REGISTRY_SERVER_IP"]
    + ":"
    + os.environ["REGISTRY_SERVER_PORT"]
    + "/api/index/"
)


# Coding - Search


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def search_icd10(request):
    """Search for an ICD10 code."""
    return search_table(ICD10, ["code", "description", "category__title"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def search_loinc(request):
    """Search for a LOINC code."""
    return search_table(LOINC, ["code", "component", "long_common_name"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("FACILITY")
def get_arrival_measurements(request):
    """Get LOINC codes for vital signs measurements."""
    codes = LOINC.objects.filter(
        code__in=["3141-9", "3137-7", "8310-5", "8480-6", "8462-4", "8867-4", "9279-1"]
    ).order_by("long_common_name")
    return create_success_payload([code.serialize() for code in codes])


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("FACILITY")
def get_consultation_codes(request):
    """Get HCPCS codes for OP & IP consultation."""
    codes = [HCPCS.objects.get(code="99241"), HCPCS.objects.get(code="99251")]  # OP, IP
    return create_success_payload([code.serialize() for code in codes])


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
def search_hcpcs(request):
    """Search for a HCPCS code."""
    return search_table(HCPCS, ["code", "description"], request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("FACILITY")
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
@require_service("FACILITY")
def get_visit(request, visit_id):
    """GET a visit."""
    visit = get_object_or_404(Visit, uuid=visit_id)
    return create_success_payload(visit.serialize())
