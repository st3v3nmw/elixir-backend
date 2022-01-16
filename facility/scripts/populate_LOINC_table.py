import csv

from facility.models import LOINC

# Data obtained from
# https://loinc.org/downloads/loinc-table/
SOURCE_CSV = "data/LoincTableCore.csv"


def populate_table():
    with open(SOURCE_CSV, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            code, _ = LOINC.get_or_create(
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
            print(f"Processed LOINC Code {code}.")


if __name__ == "__main__":
    populate_table()
