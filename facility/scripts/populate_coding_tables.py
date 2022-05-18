"""Script to populate the coding tables."""

import csv

from tqdm import tqdm

from facility.models import HCPCS, ICD10, LOINC, ICD10Category, RxTerm

# Data obtained from
# https://www.cms.gov/medicaremedicare-fee-service-paymentphysicianfeeschedpfs-relative-value-files/rvu22b
# CPT codes and descriptions only are copyright 2021 American Medical Association.  All Rights Reserved.  # noqa
# Dental codes (D codes) are copyright 2022/23 American Dental Association.  All Rights Reserved.
HCPCS_SOURCE_CSV = "facility/scripts/data/PPRRVU22_APR.csv"

# Data obtained from https://github.com/k4m1113/ICD-10-CSV
ICD10_SOURCE_CSV = "facility/scripts/data/icd10_codes.csv"

# Data obtained from https://loinc.org/downloads/loinc-table/
LOINC_SOURCE_CSV = "facility/scripts/data/LoincTableCore.csv"

# Data obtained from https://lhncbc.nlm.nih.gov/MOR/RxTerms/
RXTERMS_SOURCE_CSV = "facility/scripts/data/RxTerms202201.csv"


def run():
    """Run populate_coding_tables script."""
    print(f"Populating HCPCS table from {HCPCS_SOURCE_CSV}...")
    with open(HCPCS_SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        for row in tqdm(rows):
            code = row["HCPCS"].strip()
            mod = row["MOD"].strip()
            if mod:
                code += f"-{mod}"
            HCPCS.objects.get_or_create(
                code=code,
                description=row["DESCRIPTION"].strip(),
                status_code=row["STATUS CODE"].strip(),
            )

    print(f"Populating ICD10 tables from {ICD10_SOURCE_CSV}...")
    with open(ICD10_SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        for row in tqdm(rows):
            category, _ = ICD10Category.objects.get_or_create(
                code=row["Category Code"].strip(), title=row["Category Title"].strip()
            )

            ICD10.objects.get_or_create(
                category=category,
                code=row["Full Code"].strip(),
                description=row["Full Description"].strip(),
            )

    print(f"Populating LOINC table from {LOINC_SOURCE_CSV}...")
    with open(LOINC_SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        for row in tqdm(rows):
            LOINC.objects.get_or_create(
                code=row["LOINC_NUM"].strip(),
                component=row["COMPONENT"].strip(),
                attribute=row["PROPERTY"].strip(),
                timing=row["TIME_ASPCT"].strip(),
                system=row["SYSTEM"].strip(),
                scale=row["SCALE_TYP"].strip(),
                method=row["METHOD_TYP"].strip(),
                long_common_name=row["LONG_COMMON_NAME"].strip(),
                status=row["STATUS"].strip(),
            )

    print(f"Populating RxTerms table from {RXTERMS_SOURCE_CSV}...")
    with open(RXTERMS_SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        for row in tqdm(rows):
            RxTerm.objects.get_or_create(
                code=row["RXCUI"].strip(),
                name=row["DISPLAY_NAME"].strip(),
                route=row["ROUTE"].strip(),
                strength=row["STRENGTH"].strip(),
                form=row["RXN_DOSE_FORM"].strip(),
            )
