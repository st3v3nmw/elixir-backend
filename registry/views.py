from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from authentication.models import User
from .models import Facility, Practitioner, Tenure, Record, RecordRating
from common.payload import create_success_payload
from common.utils import require_service
from common.views import create
from common.middlewares import require_roles


# Health Facilities


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def get_facility(request, pk):
    facility = get_object_or_404(Facility, uuid=pk)
    return create_success_payload(facility.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def list_facilities(request):
    facilities = Facility.objects.all()
    return create_success_payload([facility.serialize() for facility in facilities])


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
@require_GET
@require_service("REGISTRY")
def get_record(request, doc_id):
    record = get_object_or_404(Record, pk=doc_id)
    return create_success_payload(record.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("REGISTRY")
def list_records(request, user_id):
    records = Record.objects.filter(user_id=user_id)
    return create_success_payload([record.serialize() for record in records])
