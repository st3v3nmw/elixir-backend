"""This module houses models for the facility app."""

from django.contrib.postgres.fields import ArrayField
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
    SERIALIZATION_FIELDS = ["uuid"] + VALIDATION_FIELDS + ["employment_history"]

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
                    "family": self.user.surname,
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
    SERIALIZATION_FIELDS = ["uuid", "facility_id", "start", "end"]

    class Meta:  # noqa
        unique_together = ("practitioner", "facility", "start")
        ordering = ["-start"]


# Records


class Record(BaseModel):
    """Record model."""

    facility = models.ForeignKey(
        Facility, related_name="records", on_delete=models.RESTRICT
    )
    patient = models.ForeignKey(User, related_name="records", on_delete=models.RESTRICT)
    creation_time = models.DateTimeField()  # Creation time at facility
    # doctrine of professional discretion
    is_released = models.BooleanField(default=True)

    POST_REQUIRED_FIELDS = [
        "uuid",
        "owner_id",
        "patient_id",
        "creation_time",
        "released",
    ]
    SERIALIZATION_FIELDS = [
        "uuid",
        "owner",
        "patient_id",
        "released",
        "creation_time",
        "ratings",
        "consent_requests",
    ]

    @property
    def rating(self):
        """Calculate the rating for this record using Wilson Score Intervals."""
        n_ratings = self.ratings.objects.all().count()
        n_positive_accurate = self.ratings.objects.filter(is_accurate=True).count()
        n_positive_complete = self.ratings.objects.filter(is_complete=True).count()
        return (
            ci_lower_bound(n_positive_accurate, n_ratings, 0.96)
            + ci_lower_bound(n_positive_complete, n_ratings, 0.96)
        ) / 2


class RecordRating(BaseModel):
    """RecordRating model."""

    record = models.ForeignKey(
        Record, related_name="ratings", on_delete=models.RESTRICT
    )
    encounter = models.UUIDField()
    rater = models.ForeignKey(User, related_name="ratings", on_delete=models.RESTRICT)
    is_accurate = models.BooleanField()
    is_complete = models.BooleanField()
    review = models.TextField()

    POST_REQUIRED_FIELDS = ["record_id", "rater_id", "rating", "review"]
    SERIALIZATION_FIELDS = ["record_id", "rating", "review", "rater"]


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
    status = models.TextField(choices=CONSENT_REQUEST_STATUSES, max_length=16)

    POST_REQUIRED_FIELDS = [
        "records",
        "visit_types",
        "requestor",
        "request_note",
        "status",
    ]
    SERIALIZATION_FIELDS = POST_REQUIRED_FIELDS + ["transition_logs"]


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
    access_time = models.DateTimeField()

    POST_REQUESTED_FIELDS = ["record_id", "practitioner_id", "access_time"]
    SERIALIZATION_FIELDS = POST_REQUESTED_FIELDS
