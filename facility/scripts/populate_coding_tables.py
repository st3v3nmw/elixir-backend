import csv

from tqdm import tqdm

from facility.models import HCPCS, ICD10, ICD10Category, LOINC, RxTerm

# Data obtained from
# https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets/Alpha-Numeric-HCPCS-Items/2020-Alpha-Numeric-HCPCS-File
HCPCS_SOURCE_CSV = "facility/scripts/data/HCPC2020_ANWEB_w_disclaimer.csv"

# Data obtained from https://github.com/k4m1113/ICD-10-CSV
ICD10_SOURCE_CSV = "facility/scripts/data/icd10_codes.csv"

# Data obtained from https://loinc.org/downloads/loinc-table/
LOINC_SOURCE_CSV = "facility/scripts/data/LoincTableCore.csv"

# Data obtained from https://lhncbc.nlm.nih.gov/MOR/RxTerms/
RXTERMS_SOURCE_CSV = "facility/scripts/data/RxTerms202201.csv"


def run():
    print(f"Populating HCPCS table from {HCPCS_SOURCE_CSV}...")
    with open(HCPCS_SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        for row in tqdm(rows):
            HCPCS.objects.get_or_create(
                code=row["HCPC"].strip(),
                seq_num=row["SEQNUM"].strip(),
                description=row["LONG DESCRIPTION"].strip(),
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
