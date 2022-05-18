"""This module houses models for the facility app."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.dispatch import receiver
from django.utils import timezone

from authentication.models import User
from common.constants import (CONSENT_REQUEST_STATUSES, COUNTIES,
                              PRACTITIONER_TYPES, REGIONS, VISIT_TYPES,
                              counties_to_regions_map)
from common.models import BaseModel, Entity

# Health Facility


class Facility(Entity):
    """Facility model."""

    REGIONS = BaseModel.preprocess_choices(REGIONS)
    COUNTIES = BaseModel.preprocess_choices(COUNTIES)
    # http://www.hl7.org/fhir/v3/ServiceDeliveryLocationRoleType/vs.html
    FACILITY_TYPES = [
        ("HOSP", "Hospital"),
        ("PSY", "Psychiatry Clinic"),
        ("RH", "Rehabilitation Hospital"),
        ("MBL", "Medical Laboratory"),
        ("PHARM", "Pharmacy"),
        ("PEDC", "Pediatrics Clinic"),
        ("OPTC", "Optometry Clinic"),
        ("DENT", "Dental Clinic"),
    ]

    name = models.CharField(max_length=128)
    county = models.CharField(choices=COUNTIES, max_length=32)
    location = models.TextField()  # Detailed Location
    type = models.CharField(choices=FACILITY_TYPES, max_length=32)
    api_base_url = models.URLField("API Base URL")

    SERIALIZATION_FIELDS = [
        "uuid",
        "name",
        "region",
        "county",
        "location",
        "type",
        "email",
        "phone_number",
        "address",
        "api_base_url",
        "date_joined",
        "is_active",
    ]

    @property
    def region(self):
        """Return the region the facility's county belongs to."""
        return counties_to_regions_map[self.county]

    def __str__(self):
        """Return the string representation of the Facility."""
        return f"{self.name} ({self.uuid})"


# Practitioner


class Practitioner(BaseModel):
    """Practitioner model."""

    PRACTITIONER_TYPES = BaseModel.preprocess_choices(PRACTITIONER_TYPES)

    user = models.OneToOneField(User, on_delete=models.RESTRICT)
    type = models.CharField(choices=PRACTITIONER_TYPES, max_length=32)

    VALIDATION_FIELDS = ["user_id", "type"]
    SERIALIZATION_FIELDS = ["uuid", "user"] + VALIDATION_FIELDS + ["created"]

    def __str__(self):
        """Return the string representation of the Practitioner."""
        return f"{self.user.first_name} {self.user.last_name} ({self.uuid})"


class Tenure(BaseModel):
    """Tenure model."""

    practitioner = models.ForeignKey(
        Practitioner, related_name="employment_history", on_delete=models.RESTRICT
    )
    facility = models.ForeignKey(Facility, on_delete=models.RESTRICT)
    start = models.DateField(default=timezone.now)
    end = models.DateField(null=True)

    VALIDATION_FIELDS = ["practitioner_id", "facility_id", "start"]
    SERIALIZATION_FIELDS = ["uuid", "facility", "start", "end", "practitioner"]

    class Meta:  # noqa
        unique_together = ("practitioner", "facility", "start")
        ordering = ["-start"]


# Records


class Record(BaseModel):
    """Record model."""

    VISIT_TYPES = BaseModel.preprocess_choices(VISIT_TYPES)

    facility = models.ForeignKey(
        Facility, related_name="records", on_delete=models.RESTRICT
    )
    patient = models.ForeignKey(User, related_name="records", on_delete=models.RESTRICT)
    creation_time = models.DateTimeField()  # Creation time at facility
    visit_type = models.CharField(choices=VISIT_TYPES, max_length=16)
    # doctrine of professional discretion
    is_released = models.BooleanField(default=True)

    POST_REQUIRED_FIELDS = [
        "uuid",
        "facility_id",
        "patient_id",
        "creation_time",
        "visit_type",
        "is_released",
    ]
    SERIALIZATION_FIELDS = [
        "uuid",
        "facility",
        "patient_id",
        "is_released",
        "creation_time",
        "visit_type",
        "ratings",
        "consent_requests",
        "rating",
        "access_logs",
    ]

    @property
    def rating(self):
        """Calculate the average rating for this record."""
        avg_accuracy = (
            self.ratings.aggregate(models.Avg("accuracy"))["accuracy__avg"] or 0
        )
        avg_completeness = (
            self.ratings.aggregate(models.Avg("completeness"))["completeness__avg"] or 0
        )
        return f"{avg_accuracy},{avg_completeness}"


class RecordRating(BaseModel):
    """RecordRating model."""

    record = models.ForeignKey(
        Record, related_name="ratings", on_delete=models.RESTRICT
    )
    rater = models.ForeignKey(User, related_name="ratings", on_delete=models.RESTRICT)
    accuracy = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    completeness = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review = models.TextField()

    POST_REQUIRED_FIELDS = [
        "record_id",
        "rater_id",
        "accuracy",
        "completeness",
        "review",
    ]
    SERIALIZATION_FIELDS = [
        "uuid",
        "record_id",
        "accuracy",
        "completeness",
        "review",
        "rater",
        "created",
    ]


class ConsentRequest(BaseModel):
    """ConsentRequest model."""

    CONSENT_REQUEST_STATUSES = BaseModel.preprocess_choices(CONSENT_REQUEST_STATUSES)

    record = models.ForeignKey(
        Record, on_delete=models.RESTRICT, related_name="consent_requests"
    )
    requestor = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    request_note = models.TextField()
    status = models.CharField(
        choices=CONSENT_REQUEST_STATUSES, max_length=16, default="PENDING"
    )

    POST_REQUIRED_FIELDS = [
        "record_id",
        "requestor_id",
        "request_note",
        "status",
    ]
    SERIALIZATION_FIELDS = [
        "uuid",
        "requestor",
        "request_note",
        "record_id",
        "status",
        "created",
        "transition_logs",
    ]


class ConsentRequestTransition(BaseModel):
    """ConsentRequestTransition model."""

    consent_request = models.ForeignKey(
        ConsentRequest, related_name="transition_logs", on_delete=models.RESTRICT
    )
    from_state = models.TextField(
        choices=[("DRAFT", "Draft"), ("PENDING", "Pending"), ("APPROVED", "Approved")],
        max_length=16,
    )
    to_state = models.TextField(
        choices=[
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("WITHDRAWN", "Withdrawn"),
        ],
        max_length=16,
    )
    transition_time = models.DateTimeField(auto_now_add=True)

    SERIALIZATION_FIELDS = [
        "uuid",
        "consent_request_id",
        "from_state",
        "to_state",
        "transition_time",
    ]


@receiver(
    models.signals.post_save,
    sender=ConsentRequest,
    dispatch_uid="update_status",
)
def update_consent_request_status(sender, instance, **kwargs):
    """Create a ConsentRequestTransition log when the ConsentRequest state changes."""
    existing_logs = ConsentRequestTransition.objects.filter(consent_request=instance)
    if existing_logs.exists():
        from_state = existing_logs.latest("created").to_state
    else:
        from_state = "PENDING"
    ConsentRequestTransition.objects.create(
        consent_request=instance,
        from_state=from_state,
        to_state=instance.status,
    )


class AccessLog(BaseModel):
    """AccessLog model."""

    record = models.ForeignKey(
        Record, related_name="access_logs", on_delete=models.RESTRICT
    )
    practitioner = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    access_time = models.DateTimeField(auto_now_add=True)

    POST_REQUESTED_FIELDS = ["record_id", "practitioner_id"]
    SERIALIZATION_FIELDS = ["uuid", "record_id", "practitioner", "access_time"]
