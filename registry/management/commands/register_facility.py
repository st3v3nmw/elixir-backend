from django.core.management.base import BaseCommand

from registry.models import Facility
from common.utils import require_service


class Command(BaseCommand):
    help = "Adds a health facility to the registry"

    def add_arguments(self, parser) -> None:
        parser.add_argument("name", type=str)
        parser.add_argument(
            "county", choices=[county[0] for county in Facility.COUNTIES]
        )
        parser.add_argument("location", type=str)
        parser.add_argument(
            "type", choices=[type[0] for type in Facility.FACILITY_TYPES]
        )
        parser.add_argument("email", type=str)
        parser.add_argument("phone_number", type=str)
        parser.add_argument("address", type=str)
        parser.add_argument("api_base_url", type=str)

    @require_service("REGISTRY")
    def handle(self, *args, **kwargs):
        fields = {
            "name": kwargs["name"],
            "county": kwargs["county"],
            "location": kwargs["location"],
            "type": kwargs["type"],
            "email": kwargs["email"],
            "phone_number": kwargs["phone_number"],
            "address": kwargs["address"],
            "api_base_url": kwargs["api_base_url"],
        }
        try:
            facility = Facility.objects.create(**fields)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Health Facility registered (UUID: {facility.uuid})."
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(str(e)))
            self.stdout.write(self.style.ERROR("Error adding facility."))
