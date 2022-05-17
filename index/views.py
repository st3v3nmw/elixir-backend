"""This module houses API endpoints for the index app."""

import uuid
from datetime import timedelta

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import (
    AccessLog,
    ConsentRequest,
    Facility,
    Practitioner,
    Record,
    RecordRating,
    Tenure,
)
from authentication.models import User
from common.middleware import require_roles, require_service
from common.payload import create_error_payload, create_success_payload
from common.utils import create, search_table, validate_post_data


# Health Facilities


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_facility(request, pk):
    """GET a facility."""
    facility = get_object_or_404(Facility, uuid=pk)
    return create_success_payload(facility.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_facilities(request):
    """List all registered facilities."""
    facilities = Facility.objects.all().order_by("name")
    return create_success_payload([facility.serialize() for facility in facilities])


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_facilities(request):
    """Search practitioners."""
    return search_table(Facility, ["name", "location", "county"], request)


# Practitioner


@require_roles(["PATIENT"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def register_practitioner(request):
    """Register a practitioner."""
    return create(Practitioner, request)


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def register_tenure(request):
    """Register a practitioner's tenure at a specific facility."""
    return create(Tenure, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_practitioner(request, user_id):
    """GET a practitioner."""
    practitioner = get_object_or_404(Practitioner, user__uuid=user_id)
    latest_tenure = practitioner.employment_history.latest("start")
    extra = practitioner.serialize()
    latest_tenure.SERIALIZATION_FIELDS = ["uuid", "facility", "start", "end"]
    extra["latest_tenure"] = latest_tenure.serialize()
    return create_success_payload(
        {
            "fhir": practitioner.fhir_serialize(),
            "extra": extra,
        }
    )


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_practitioners(request):
    """List all registered practitioners."""
    practitioners = Practitioner.objects.all()
    return create_success_payload(
        [
            {"fhir": practitioner.fhir_serialize(), "extra": practitioner.serialize()}
            for practitioner in practitioners
        ]
    )


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_practitioners(request):
    """Search for practitioners."""
    return search_table(Practitioner, ["user__first_name", "user__last_name"], request)


# Records


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_record(request):
    """Create a record."""
    return create(Record, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_rating(request):
    """Create a rating."""
    return create(RecordRating, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_record(request, doc_id):
    """GET a record."""
    record = get_object_or_404(Record, uuid=doc_id)
    return create_success_payload(record.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def list_records(request, user_id):
    """List all records belonging to a particular user."""
    records = list(map(lambda x: x.serialize(), Record.objects.filter(patient=user_id)))

    if "PRACTITIONER" in request.token["roles"]:
        tenure = Tenure.objects.get(practitioner__user=request.token["sub"])
        for record in records:
            cnr_q = ConsentRequest.objects.filter(
                record=record["uuid"],
                requestor=tenure,
            )
            if cnr_q.filter(status="APPROVED").exists():
                record["access_status"] = "APPROVED"
            elif cnr_q.filter(status="PENDING").exists():
                record["access_status"] = "PENDING"
            else:
                record["access_status"] = "NONE"
    else:
        for record in records:
            record["access_status"] = "APPROVED"
    return create_success_payload(records)


# Consent


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_consent_request(request):
    """Create a consent request."""
    return create(ConsentRequest, request)


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_consent_request(request, request_id):
    """GET a consent request."""
    consent_request = get_object_or_404(ConsentRequest, uuid=request_id)
    return create_success_payload(consent_request.serialize())


@require_roles(["PATIENT", "PRACTITINER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def update_consent_request(request, request_id):
    """UPDATE the status of a consent request."""
    consent_request = get_object_or_404(ConsentRequest, uuid=request_id)
    is_valid, request_data, debug_data = validate_post_data(request, ["to_state"])
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    consent_request.status = request_data["to_state"]
    consent_request.save()
    consent_request.refresh_from_db()
    return create_success_payload(consent_request.serialize())


@require_roles(["PATIENT", "PRACTITIONER"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_consent_requests(request, record_id):
    """List all consent requests for a particular record."""
    requests = ConsentRequest.objects.filter(record__in=record_id)
    return create_success_payload([request.serialize() for request in requests])


@require_roles(["PATIENT"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_user_consent_requests(request, user_id):
    requests = ConsentRequest.objects.filter(record__patient=user_id).order_by(
        "-created"
    )
    return create_success_payload([request.serialize() for request in requests])


# Access Logs


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def create_access_log(request):
    """Create an access log entry."""
    is_valid, request_data, debug_data = validate_post_data(
        request, AccessLog.POST_REQUIRED_FIELDS
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])
    latest_log_entry = AccessLog.objects.filter(
        record_id=request_data["record_id"],
        practitioner=request_data["practitioner_id"],
    )
    if len(latest_log_entry) == 0 or timezone.now() - latest_log_entry.latest(
        "created"
    ).created > timedelta(hours=1):
        request_data["uuid"] = uuid.uuid4()
        success, result = AccessLog.create(request_data)
        if success:
            return create_success_payload(
                result.serialize(), message="Created successfully."
            )
        else:
            return create_error_payload(message=result)
    else:
        return create_success_payload(latest_log_entry.latest("created").serialize())


@require_roles(["PATIENT"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def get_access_log(request, log_id):
    """GET an access log entry."""
    log = get_object_or_404(AccessLog, uuid=log_id)
    return create_success_payload(log.serialize())


@require_roles(["PATIENT"])
@csrf_exempt
@require_GET
@require_service("INDEX")
def list_access_logs(request, record_id):
    """List all access logs for a particular record."""
    logs = AccessLog.objects.filter(record=record_id)
    return create_success_payload([log.serialize() for log in logs])


# Patient


@require_roles(["PATIENT", "PRACTITIONER"])
@require_GET
@require_service("INDEX")
def get_patient(request, patient_id):
    """GET a patient in FHIR format."""
    patient = get_object_or_404(User, uuid=patient_id)
    return create_success_payload(patient.fhir_serialize())


@require_roles(["PRACTITIONER"])
@csrf_exempt
@require_POST
@require_service("INDEX")
def search_patients(request):
    """Search patients."""
    return search_table(
        User,
        ["first_name", "last_name", "national_id", "email", "phone_number"],
        request,
    )
