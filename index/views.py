from django.contrib.postgres.search import SearchVector
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import (
    AccessLog,
    ConsentRequest,
    ConsentRequestTransition,
    Facility,
    Practitioner,
    Tenure,
    Record,
    RecordRating,
)
from authentication.models import User
from common.middleware import require_roles
from common.payload import create_error_payload, create_success_payload
from common.utils import require_service
from common.validation import validate_post_data
from common.views import create


# Health Facilities


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_facility(request, pk):
    facility = get_object_or_404(Facility, uuid=pk)
    return create_success_payload(facility.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_facilities(request):
    facilities = Facility.objects.all()
    return create_success_payload([facility.serialize() for facility in facilities])


# Practitioner


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def register_practitioner(request):
    return create(Practitioner, request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def register_tenure(request):
    return create(Tenure, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_practitioner(request, pk):
    practitioner = get_object_or_404(Practitioner, uuid=pk)
    return create_success_payload(
        {
            "fhir": practitioner.fhir_serialize(),
            "extra": practitioner.serialize(),
        }
    )


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_practitioners(request):
    practitioners = Practitioner.objects.all()
    return create_success_payload(
        [
            {"fhir": practitioner.fhir_serialize(), "extra": practitioner.serialize()}
            for practitioner in practitioners
        ]
    )


# Search Providers


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_providers(request):
    is_valid, request_data, debug_data = validate_post_data(request.body, ["query"])
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    facilities = Facility.objects.annotate(
        search=SearchVector("name", "location", "county")
    ).filter(search=request_data["query"])

    practitioners = Practitioner.objects.annotate(
        search=SearchVector("user__first_name", "user__surname")
    ).filter(search=request_data["query"])

    return create_success_payload(
        [
            *[facility.serialize() for facility in facilities],
            *[practitioner.serialize() for practitioner in practitioners],
        ]
    )


# Records


@require_roles(["FACILITY"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_record(request):
    return create(Record, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_rating(request):
    return create(RecordRating, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_record(request, doc_id):
    record = get_object_or_404(Record, uuid=doc_id)
    return create_success_payload(record.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_records(request, user_id):
    records = Record.objects.filter(user_id=user_id)
    return create_success_payload([record.serialize() for record in records])


# Consent


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_consent_request(request):
    return create(ConsentRequest, request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_consent_request(request, request_id):
    request = get_object_or_404(ConsentRequest, uuid=request_id)
    return create_success_payload(request.serialize())


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_consent_requests(request, record_id):
    requests = ConsentRequest.objects.filter(record__in=record_id)
    return create_success_payload([request.serialize() for request in requests])


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_consent_request_transition(request):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, ["request_id", "to_state"]
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    request = get_object_or_404(ConsentRequest, uuid=request_data["request_id"])
    transition = ConsentRequestTransition.create(
        consent_request=request,
        from_state=request.status,
        to_state=request_data["to_state"],
    )
    request.status = request_data["to_state"]
    return create_success_payload(transition.serialize(), message="Created.")


# Access Logs


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_access_log(request):
    return create(AccessLog, request)


@require_roles(["PATIENT"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_access_log(request, log_id):
    log = get_object_or_404(AccessLog, uuid=log_id)
    return create_success_payload(log.serialize())


@require_roles(["PATIENT"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_access_logs(request, record_id):
    logs = AccessLog.objects.filter(record=record_id)
    return create_success_payload([log.serialize() for log in logs])


# Patient


@require_GET
@require_service("INDEX")
def get_patient(request, patient_id):
    patient = get_object_or_404(User, uuid=patient_id)
    return create_success_payload(patient.fhir_serialize())
