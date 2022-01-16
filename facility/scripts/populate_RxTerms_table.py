import csv

from facility.models import RxTerm

# Data obtained from
# https://lhncbc.nlm.nih.gov/MOR/RxTerms/
SOURCE_CSV = "data/RxTerms202201.csv"


def populate_table():
    with open(SOURCE_CSV, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            code, _ = RxTerm.get_or_create(
                code=row["RXCUI"].strip(),
                name=row["DISPLAY_NAME"].strip(),
                route=row["ROUTE"].strip(),
                strength=row["STRENGTH"].strip(),
                form=row["RXN_DOSE_FORM"].strip(),
            )
            print(f"Processed RxTerms Code {code}.")


if __name__ == "__main__":
    populate_table()
