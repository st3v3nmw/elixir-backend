from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from common.views import create

from .models import HealthFacility, HealthWorker, Tenure
from common.payload import create_success_payload


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
    return create(request, HealthWorker)


@require_GET
def get_health_worker(request, pk):
    health_worker = get_object_or_404(HealthWorker, pk=pk)
    return create_success_payload(health_worker.serialize())


@csrf_exempt
@require_POST
def register_tenure(request):
    return create(request, Tenure)
