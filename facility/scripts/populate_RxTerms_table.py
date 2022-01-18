import csv

from tqdm import tqdm

from facility.models import RxTerm

# Data obtained from
# https://lhncbc.nlm.nih.gov/MOR/RxTerms/
SOURCE_CSV = "facility/scripts/data/RxTerms202201.csv"


def run():
    print(f"Populating RxTerms table from {SOURCE_CSV}...")
    with open(SOURCE_CSV, "r") as f:
        rows = list(csv.DictReader(f, delimiter="|"))
        for row in tqdm(rows):
            RxTerm.objects.get_or_create(
                code=row["RXCUI"].strip(),
                name=row["DISPLAY_NAME"].strip(),
                route=row["ROUTE"].strip(),
                strength=row["STRENGTH"].strip(),
                form=row["RXN_DOSE_FORM"].strip(),
            )
