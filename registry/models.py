from django.db import models
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

from authentication.models import User
from common.models import BaseModel, Entity
from common.constants import (
    REGIONS,
    COUNTIES,
    PRACTITIONER_TYPES,
    CONSENT_REQUEST_STATUSES,
    counties_to_regions_map,
)
from django.contrib.postgres.fields import ArrayField

# Health Facility


class Facility(Entity):
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

    name = models.CharField("Name", max_length=128)
    region = models.CharField("Region", choices=REGIONS, max_length=32)
    county = models.CharField("County", choices=COUNTIES, max_length=32)
    location = models.TextField("Detailed Location")
    type = models.CharField("Type", choices=FACILITY_TYPES, max_length=32)
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
        return counties_to_regions_map[self.county]


# Practitioner


class Practitioner(BaseModel):
    PRACTITIONER_TYPES = BaseModel.preprocess_choices(PRACTITIONER_TYPES)

    user = models.OneToOneField(User, on_delete=models.RESTRICT)
    type = models.CharField(
        "Practitioner Type", choices=PRACTITIONER_TYPES, max_length=32
    )

    VALIDATION_FIELDS = ["user_id", "type"]
    SERIALIZATION_FIELDS = ["uuid"] + VALIDATION_FIELDS + ["employment_history"]


class Tenure(BaseModel):
    practitioner = models.ForeignKey(
        Practitioner, related_name="employment_history", on_delete=models.RESTRICT
    )
    facility = models.ForeignKey(Facility, on_delete=models.RESTRICT)
    start = models.DateField("Tenure Start", default=timezone.now)
    end = models.DateField("Tenure End", null=True)

    VALIDATION_FIELDS = ["practitioner_id", "facility_id", "start"]
    SERIALIZATION_FIELDS = ["uuid", "facility_id", "start", "end"]

    class Meta:
        unique_together = ("practitioner", "facility", "start")
        ordering = ["-start"]


# Records


class Record(BaseModel):
    owner = models.ForeignKey(Tenure, related_name="records", on_delete=models.RESTRICT)
    patient = models.ForeignKey(User, related_name="records", on_delete=models.RESTRICT)
    creation_time = models.DateTimeField("Creation time at facility")
    # doctrine of professional discretion
    released = models.BooleanField("Released?", default=True)

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


class RecordRating(BaseModel):
    record = models.ForeignKey(
        Record, related_name="ratings", on_delete=models.RESTRICT
    )
    rater = models.ForeignKey(User, related_name="ratings", on_delete=models.RESTRICT)
    rating = models.FloatField(
        "Rating", validators=[MinValueValidator(1.0), MaxValueValidator(10.0)]
    )
    review = models.TextField("Record Review")

    POST_REQUIRED_FIELDS = ["record_id", "rater_id", "rating", "review"]
    SERIALIZATION_FIELDS = ["record_id", "rating", "review", "rater"]


class ConsentRequest(BaseModel):
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
    practitioner = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    request_note = models.TextField("Request Note")
    status = models.TextField(
        "Consent Request Status", choices=CONSENT_REQUEST_STATUSES, max_length=16
    )

    POST_REQUIRED_FIELDS = [
        "records",
        "visit_types",
        "practitioner",
        "request_note",
        "status",
    ]
    SERIALIZATION_FIELDS = POST_REQUIRED_FIELDS + ["transition_logs"]


class ConsentRequestTransition(BaseModel):
    consent_request = models.ForeignKey(
        ConsentRequest, related_name="transition_logs", on_delete=models.RESTRICT
    )
    from_state = models.TextField(
        "From State",
        choices=[("DRAFT", "Draft"), ("PENDING", "Pending"), ("APPROVED", "Approved")],
        max_length=16,
    )
    to_state = models.TextField(
        "To State",
        choices=[
            ("APPROVED", "Approved"),
            ("REJECTED", "Rejected"),
            ("WITHDRAWN", "Withdrawn"),
        ],
        max_length=16,
    )
    transition_time = models.DateTimeField("Transition Time", auto_now_add=True)

    SERIALIZATION_FIELDS = [
        "consent_request_id",
        "from_state",
        "to_state",
        "transition_time",
    ]


class AccessLog(BaseModel):
    record = models.ForeignKey(
        Record, related_name="access_logs", on_delete=models.RESTRICT
    )
    practitioner = models.ForeignKey(Tenure, on_delete=models.RESTRICT)
    access_time = models.DateTimeField("Access Time")

    POST_REQUESTED_FIELDS = ["record_id", "practitioner_id", "access_time"]
    SERIALIZATION_FIELDS = POST_REQUESTED_FIELDS
