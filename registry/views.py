from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import HealthFacility, HealthWorker, Tenure
from common.payload import create_success_payload
from common.utils import require_server
from common.views import create
from common.middlewares import require_roles


# Health Facilities


@require_roles(["PATIENT", "HEALTH_WORKER"])
@require_GET
@require_server("CORE")
def list_facilities(request):
    facilities = HealthFacility.objects.all()
    data = [facility.serialize() for facility in facilities]
    return create_success_payload(data)


@require_roles(["PATIENT", "HEALTH_WORKER"])
@require_GET
@require_server("CORE")
def get_facility(request, pk):
    facility = get_object_or_404(HealthFacility, uuid=pk)
    return create_success_payload(facility.serialize())


# Health Worker


@require_roles(["HEALTH_WORKER"])
@csrf_exempt
@require_POST
@require_server("CORE")
def register_health_worker(request):
    return create(request, HealthWorker)


@require_roles(["HEALTH_WORKER"])
@csrf_exempt
@require_POST
@require_server("CORE")
def register_tenure(request):
    return create(request, Tenure)


@require_roles(["PATIENT", "HEALTH_WORKER"])
@require_GET
@require_server("CORE")
def get_health_worker(request, pk):
    health_worker = get_object_or_404(HealthWorker, pk=pk)
    return create_success_payload(health_worker.serialize())
