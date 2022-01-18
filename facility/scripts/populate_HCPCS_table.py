import csv

from tqdm import tqdm

from facility.models import HCPCS

# Data obtained from
# https://www.cms.gov/Medicare/Coding/HCPCSReleaseCodeSets/Alpha-Numeric-HCPCS-Items/2020-Alpha-Numeric-HCPCS-File
SOURCE_CSV = "facility/scripts/data/HCPC2020_ANWEB_w_disclaimer.csv"


def run():
    print(f"Populating HCPCS table from {SOURCE_CSV}...")
    with open(SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f))
        for row in tqdm(rows):
            HCPCS.objects.get_or_create(
                code=row["HCPC"].strip(),
                seq_num=row["SEQNUM"].strip(),
                description=row["LONG DESCRIPTION"].strip(),
            )
