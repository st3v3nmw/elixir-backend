import csv

from facility.models import HCPCS

# Data obtained from
# https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets/Alpha-Numeric-HCPCS-Items/2020-Alpha-Numeric-HCPCS-File
SOURCE_CSV = "data/HCPC2020_ANWEB_w_disclaimer.csv"


def populate_table():
    with open(SOURCE_CSV, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            code, _ = HCPCS.get_or_create(
                code=row["HCPC"].strip(),
                description=row["LONG DESCRIPTION"].strip(),
            )
            print(f"Processed HCPCS Code {code}.")


if __name__ == "__main__":
    populate_table()
