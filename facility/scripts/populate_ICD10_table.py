import csv

from facility.models import ICD10Category, ICD10

# Data obtained from
# https://github.com/k4m1113/ICD-10-CSV
SOURCE_CSV = "data/icd10_codes.csv"


def populate_table():
    with open(SOURCE_CSV, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            category, _ = ICD10Category.get_or_create(
                code=row["Category Code"].strip(), title=row["Category Title"].strip()
            )
            print(f"Processed ICD10 Category {category}")

            code, _ = ICD10.get_or_create(
                category=category,
                code=row["Full Code"].strip(),
                description=row["Full Description"].strip(),
            )
            print(f"Processed ICD10 Code {code}.", end="\n\n")


if __name__ == "__main__":
    populate_table()
