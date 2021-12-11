from django.views.decorators.http import require_GET
from django.shortcuts import get_object_or_404

from .models import HealthFacility
from common.payload import create_success_payload


@require_GET
def list_facilities(_):
    facilities = HealthFacility.objects.all()
    data = [facility.serialize() for facility in facilities]
    return create_success_payload(data)


@require_GET
def get_facility(_, pk):
    facility = get_object_or_404(HealthFacility, uuid=pk)
    return create_success_payload(facility.serialize())
