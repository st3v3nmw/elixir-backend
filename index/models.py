"""This module houses models for the facility app."""

from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from authentication.models import User
from common.models import BaseModel, Entity
from common.constants import (
    CONSENT_REQUEST_STATUSES,
    counties_to_regions_map,
    COUNTIES,
    PRACTITIONER_TYPES,
    REGIONS,
    VISIT_TYPES,
)
from common.utils import ci_lower_bound

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
        "date_joined",
    ]

    @property
    def region(self):
        """Return the region the facility's county belongs to."""
        return counties_to_regions_map[self.county]


# Practitioner


class Practitioner(BaseModel):
    """Practitioner model."""

    PRACTITIONER_TYPES = BaseModel.preprocess_choices(PRACTITIONER_TYPES)

    user = models.OneToOneField(User, on_delete=models.RESTRICT)
    type = models.CharField(choices=PRACTITIONER_TYPES, max_length=32)

    VALIDATION_FIELDS = ["user_id", "type"]
    SERIALIZATION_FIELDS = ["uuid", "user"] + VALIDATION_FIELDS + ["created"]

    def fhir_serialize(self):
        """Serialize self as a Practitioner FHIR resource."""
        return {
            "resourceType": "Practitioner",
            "identifier": [self.uuid, self.user.uuid],
            "active": self.user.is_active,
            "name": [
                {
                    "use": "official",
                    "text": self.user.full_name,
                    "family": self.user.last_name,
                    "given": self.user.first_name,
                }
            ],
            "telecom": [{"system": "phone", "value": self.user.phone_number}],
            "gender": self.user.gender.lower(),
            "birthDate": self.user.date_of_birth,
            "address": {"text": self.user.address},
            "qualification": [{"code": self.type}],
            "communication": [{"language": "en", "preferred": True}],
        }


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
        return (
            self.ratings.aggregate(models.Avg("accuracy"))["accuracy__avg"]
            + self.ratings.aggregate(models.Avg("completeness"))["completeness__avg"]
        ) / 2


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

    records = models.ManyToManyField(to=Record, related_name="consent_requests")
    visit_types = ArrayField(
        models.CharField(
            choices=[
                ("OUTPATIENT", "Outpatient"),
                ("INPATIENT", "Inpatient"),
                ("OPTICAL", "Optical"),
                ("DENTAL", "Dental"),
            ],
            max_length=16,
        )
    )
    requestor = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    request_note = models.TextField()
    status = models.CharField(
        choices=CONSENT_REQUEST_STATUSES, max_length=16, default="PENDING"
    )

    POST_REQUIRED_FIELDS = [
        "records",
        "visit_types",
        "requestor",
        "request_note",
        "status",
    ]
    SERIALIZATION_FIELDS = [
        "visit_types",
        "requestor",
        "request_note",
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
        "consent_request_id",
        "from_state",
        "to_state",
        "transition_time",
    ]


class AccessLog(BaseModel):
    """AccessLog model."""

    record = models.ForeignKey(
        Record, related_name="access_logs", on_delete=models.RESTRICT
    )
    practitioner = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    access_time = models.DateTimeField(auto_now_add=True)

    POST_REQUESTED_FIELDS = ["record_id", "practitioner"]
    SERIALIZATION_FIELDS = POST_REQUESTED_FIELDS + ["access_time"]
