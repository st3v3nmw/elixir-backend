from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import Facility, Practitioner, Tenure, Record, RecordRating
from common.payload import create_success_payload
from common.utils import require_service
from common.views import create
from common.middlewares import require_roles


# Health Facilities


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def list_facilities(request):
    facilities = Facility.objects.all()
    data = [facility.serialize() for facility in facilities]
    return create_success_payload(data)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def get_facility(request, pk):
    facility = get_object_or_404(Facility, uuid=pk)
    return create_success_payload(facility.serialize())


# Practitioner


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("REGISTRY")
def register_practitioner(request):
    return create(request, Practitioner)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("REGISTRY")
def register_tenure(request):
    return create(request, Tenure)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def get_practitioner(request, pk):
    practitioner = get_object_or_404(Practitioner, pk=pk)
    return create_success_payload(practitioner.serialize())


# Records


@require_roles(["FACILITY"])
@csrf_exempt
@require_POST
@require_service("REGISTRY")
def create_record(request):
    return create(request, Record)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("REGISTRY")
def create_rating(request):
    return create(request, RecordRating)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("REGISTRY")
def get_record(request, pk):
    record = get_object_or_404(Record, pk=pk)
    return create_success_payload(record.serialize())
