import csv

from tqdm import tqdm

from facility.models import ICD10Category, ICD10

# Data obtained from
# https://github.com/k4m1113/ICD-10-CSV
SOURCE_CSV = "facility/scripts/data/icd10_codes.csv"


def run():
    print(f"Populating ICD10 tables from {SOURCE_CSV}...")
    with open(SOURCE_CSV, "r") as f:
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
