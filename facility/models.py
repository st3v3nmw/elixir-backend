from django.db import models
from common.constants import ENCOUNTER_STATUS, VISIT_TYPES

from common.models import BaseModel

# Coding


class LOINC(BaseModel):
    """
    Logical Observation Identifiers Names and Codes
    LOINC is a common language (set of identifiers, names, and codes)
    for identifying health measurements, observations, and documents.
    https://loinc.org/get-started/what-loinc-is/
    """

    LOINC_STATUS = BaseModel.preprocess_choices(
        ["Active", "Deprecated", "Discouraged", "Trial"]
    )

    code = models.CharField("LOINC Code", max_length=16, unique=True)
    # The substance or entity being measured or observed.
    component = models.CharField("Component", max_length=256)
    # The characteristic or attribute of the analyte.
    attribute = models.CharField("Attribute/Property", max_length=32)
    # The interval of time over which an observation was made.
    timing = models.CharField("Timing", max_length=32)
    # The specimen or thing upon which the observation was made.
    system = models.CharField("System", max_length=256)
    # How the observation value is quantified or expressed: quantitative, ordinal, nominal.
    scale = models.CharField("Scale", max_length=8)
    # OPTIONAL A high-level classification of how the observation was made.
    # Only needed when the technique affects the clinical interpretation of the results.
    method = models.CharField("Method", max_length=256)
    # Human friendly version of code
    long_common_name = models.TextField("Long Common Name")
    status = models.CharField("Status", choices=LOINC_STATUS, max_length=16)

    SERIALIZATION_FIELDS = [
        "code",
        "component",
        "attribute",
        "timing",
        "system",
        "scale",
        "method",
        "long_common_name",
        "status",
    ]

    @property
    def fully_specified_name(self) -> str:
        return (
            f"{self.component}:{self.property}:{self.timing}:{self.system}:{self.scale}:"
            f"{self.method}"
        )

    def __str__(self) -> str:
        return f"{self.fully_specified_name} ({self.uuid})"


class ICD10Category(BaseModel):
    code = models.CharField("ICD10 Category", max_length=16, unique=True)
    title = models.TextField("Category Title")

    def __str__(self) -> str:
        return f"{self.code} {self.title} ({self.uuid})"


class ICD10(BaseModel):
    """
    International Classification of Diseases (ICD)
    The global standard for diagnostic health information.
    https://icd.who.int/en
    """

    category = models.ForeignKey(to=ICD10Category, on_delete=models.RESTRICT)
    code = models.CharField("Diagnosis Code", max_length=16, unique=True)
    description = models.TextField("Diagnosis Description")

    SERIALIZATION_FIELDS = ["code", "description", "category"]

    def __str__(self) -> str:
        return f"{self.category.code} {self.code} {self.description} ({self.uuid})"


class HCPCS(BaseModel):
    """
    Healthcare Common Procedure Coding System (HCPCS)
    The Healthcare Common Procedure Coding System (HCPCS) is a collection of codes that represent
    procedures, supplies, products and services which may be provided to patients.
    Useful for billing.
    """

    code = models.CharField("HCPCS Code", max_length=16)
    seq_num = models.CharField("Sequence Number", max_length=8, default="0010")
    description = models.TextField("Description")

    SERIALIZATION_FIELDS = ["code", "description"]

    class Meta:
        unique_together = ("code", "seq_num")

    def __str__(self) -> str:
        return f"{self.code}:{self.seq_num} {self.description} ({self.uuid})"


class RxTerm(BaseModel):
    """
    RxTerms
    RxTerms is a drug interface terminology derived from RxNorm for prescription writing
    or medication history recording (e.g. in e-prescribing systems, PHRs).
    https://lhncbc.nlm.nih.gov/MOR/RxTerms/
    """

    code = models.CharField("RXCUI", max_length=16, unique=True)
    name = models.TextField("Display Name")
    route = models.CharField("Route", max_length=64)
    strength = models.CharField("Strength", max_length=256)
    form = models.CharField("Form", max_length=64)

    SERIALIZATION_FIELDS = ["code", "name", "route", "strength", "form"]

    def __str__(self):
        return f"{self.name} {self.strength} {self.form} ({self.uuid})"


# Records


class Visit(BaseModel):
    VISIT_TYPES = BaseModel.preprocess_choices(VISIT_TYPES)

    patient_id = models.UUIDField("Patient UUID")
    facility_id = models.UUIDField("Health Facility UUID")
    type = models.CharField("Visit Type", choices=VISIT_TYPES, max_length=16)
    start = models.DateTimeField("Visit Start", auto_now_add=True)
    end = models.DateTimeField("Visit End", null=True)
    primary_diagnosis = models.ForeignKey(to=ICD10, on_delete=models.RESTRICT)
    secondary_diagnoses = models.ManyToManyField(
        to=ICD10, related_name="secondary_diagnoses"
    )
    invoice_number = models.CharField("Invoice Number", max_length=32)
    invoice_attachment = models.FileField(upload_to="attachments/")

    synced = models.BooleanField("Synced with record registry?", default=False)

    POST_REQUIRED_FIELDS = [
        "patient_id",
        "facility_id",
        "type",
        "start",
        "end",
        "primary_diagnosis",
        "secondary_diagnoses",
        "invoice_number",
        "invoice_attachment",
    ]

    @property
    def invoice_amount(self):
        return sum(encounter.total for encounter in self.encounters)


class Encounter(BaseModel):
    ENCOUNTER_STATUS = BaseModel.preprocess_choices(ENCOUNTER_STATUS)
    # http://www.hl7.org/fhir/v3/ActEncounterCode/vs.html
    ENCOUNTER_CLASSES = [
        ("AMB", "Ambulatory"),
        ("EMER", "Emergency"),
        ("FLD", "Field"),
        ("HH", "Home Health"),
        ("IMP", "Inpatient Encounter"),
        ("ACUTE", "Inpatient Acute"),
        ("NONAC", "Inpatient Non-Acute"),
        ("OBSENC", "Observation Encounter"),
        ("PRENC", "Pre-Admission"),
        ("SS", "Short Stay"),
        ("VR", "Virtual"),
    ]

    author_id = models.UUIDField("Author's Tenure UUID")
    visit = models.ForeignKey(
        to=Visit, related_name="encounters", on_delete=models.RESTRICT
    )
    status = models.CharField("Status", choices=ENCOUNTER_STATUS, max_length=16)
    type = models.CharField("Type", choices=ENCOUNTER_CLASSES, max_length=8)
    start = models.DateTimeField("Visit Start", auto_now_add=True)
    end = models.DateTimeField("Visit End", null=True)
    clinical_notes = models.TextField("Clinical Notes")
    attachment = models.FileField(upload_to="attachments/")

    POST_REQUIRED_FIELDS = [
        "author_id",
        "visit_id",
        "status",
        "type",
        "start",
        "end",
        "clinical_notes",
        "attachment",
    ]

    @property
    def total_amount(self):
        return sum(line.total for line in self.charge_items) + sum(
            line.total for line in self.prescriptions
        )


class Observation(BaseModel):
    loinc = models.ForeignKey(to=LOINC, on_delete=models.RESTRICT)
    encounter = models.ForeignKey(
        to=Encounter, related_name="observations", on_delete=models.RESTRICT
    )
    result = models.CharField(max_length=256, null=True)

    POST_REQUIRED_FIELDS = ["loinc_id", "encounter_id", "result"]


class AbstractChargeItem(BaseModel):
    unit_price = models.DecimalField("Unit Price", decimal_places=2, max_digits=10)
    quantity = models.IntegerField("Quantity")
    paid = models.BooleanField("Paid?", default=False)

    @property
    def total(self):
        return self.unit_price * self.quantity

    class Meta:
        abstract = True


class ChargeItem(AbstractChargeItem):
    encounter = models.ForeignKey(
        to=Encounter, related_name="charge_items", on_delete=models.RESTRICT
    )
    item = models.ForeignKey(to=HCPCS, on_delete=models.RESTRICT)

    POST_REQUIRED_FIELDS = ["encounter_id", "item_id", "unit_price", "quantity", "paid"]


class Prescription(AbstractChargeItem):
    encounter = models.ForeignKey(
        to=Encounter, related_name="prescriptions", on_delete=models.RESTRICT
    )
    drug = models.ForeignKey(to=RxTerm, on_delete=models.RESTRICT)
    description = models.TextField("Description")
    frequency = models.IntegerField("Frequency")
    duration = models.CharField(
        "Duration",
        choices=[
            ("HOUR", "Hour"),
            ("DAY", "Day"),
            ("WEEK", "Week"),
            ("MONTH", "Month"),
            ("YEAR", "Year"),
        ],
        max_length=8,
    )

    POST_REQUIRED_FIELDS = [
        "encounter_id",
        "drug_id",
        "description",
        "frequency",
        "duration",
        "paid",
    ]
