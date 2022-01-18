import csv

from tqdm import tqdm

from facility.models import LOINC

# Data obtained from
# https://loinc.org/downloads/loinc-table/
SOURCE_CSV = "facility/scripts/data/LoincTableCore.csv"


def run():
    print(f"Populating LOINC table from {SOURCE_CSV}...")
    with open(SOURCE_CSV, "r") as f:
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
