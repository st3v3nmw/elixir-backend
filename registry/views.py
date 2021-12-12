from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import HealthFacility, HealthWorker, Tenure
from common.payload import create_success_payload, create_error_payload
from common.validation import validate_post_data


# Health Facilities


@require_GET
def list_facilities(request):
    facilities = HealthFacility.objects.all()
    data = [facility.serialize() for facility in facilities]
    return create_success_payload(data)


@require_GET
def get_facility(request, pk):
    facility = get_object_or_404(HealthFacility, uuid=pk)
    return create_success_payload(facility.serialize())


# Health Worker


@csrf_exempt
@require_POST
def register_health_worker(request):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, HealthWorker.VALIDATION_FIELDS
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    success, result = HealthWorker.save_wrapper(request_data)
    if success:
        return create_success_payload(
            result.serialize(), message="Health worker created successfully."
        )
    else:
        return create_error_payload(result)


@require_GET
def get_health_worker(request, pk):
    health_worker = get_object_or_404(HealthWorker, pk=pk)
    response_data = health_worker.serialize()
    return create_success_payload(response_data)


@csrf_exempt
@require_POST
def register_tenure(request):
    is_valid, request_data, debug_data = validate_post_data(
        request.body, Tenure.VALIDATION_FIELDS
    )
    if not is_valid:
        return create_error_payload(debug_data["data"], message=debug_data["message"])

    success, result = Tenure.save_wrapper(request_data)
    if success:
        return create_success_payload(result.serialize())
    else:
        return create_error_payload(result)
