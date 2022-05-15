"""Script to populate the index using some sample objects."""

from index.models import Facility

facilities = [
    {
        "uuid": "025bd7e8-bb12-4a11-af80-1bb5d11180cc",
        "name": "Riverside Eye Clinic",
        "region": "Coast",
        "county": "LAMU",
        "location": "Room 73, Azania Center",
        "type": "OPTC",
        "email": "riverside@example.com",
        "phone_number": "+254755555555",
        "address": "P.O. BOX 123 Lamu",
        "api_base_url": "http://localhost:8081/",
        "date_joined": "2022-02-06 13:20:21.136591+00:00",
        "is_active": True,
    },
    {
        "uuid": "82fd642e-6f07-4e2a-9867-8d7f45e18b9a",
        "name": "Le Bébé Clinic",
        "region": "Central",
        "county": "NYERI",
        "location": "Hochelaga Towers, Off Gakere Road",
        "type": "PEDC",
        "email": "le.bebe@example.com",
        "phone_number": "+254788888888",
        "address": "P.O. BOX 12-10100 Nyeri",
        "api_base_url": "http://localhost:8989",
        "date_joined": "2022-02-06 13:32:19.104632+00:00",
        "is_active": True,
    },
    {
        "uuid": "07b19c55-4fd4-4e76-88a7-1647e0cf9746",
        "name": "Rx Pharmacy",
        "region": "Nyanza",
        "county": "KISUMU",
        "location": "Doctors Plaza, Room 314",
        "type": "PHARM",
        "email": "rx.pharm@example.com",
        "phone_number": "+254744444444",
        "address": "P.O. BOX 314 Kisumu",
        "api_base_url": "http://0.0.0.0:8080/",
        "date_joined": "2022-02-06 13:36:33.997420+00:00",
        "is_active": True,
    },
    {
        "uuid": "6b7b1aff-191f-417e-a3ad-99bb10e25bd8",
        "name": "Smiles Dental",
        "region": "Rift Valley",
        "county": "NAKURU",
        "location": "Happiness Center, 8th Floor, CBD",
        "type": "DENT",
        "email": "smiles.dental@example.com",
        "phone_number": "+254712346578",
        "address": "P.O. BOX 123 Nakuru",
        "api_base_url": "http://localhost:8080/",
        "date_joined": "2022-02-06 13:09:39.134844+00:00",
        "is_active": True,
    },
    {
        "uuid": "d4766983-fcd2-436c-8be8-5b1c1ffa3e75",
        "name": "Felicity Clinic",
        "region": "Nairobi",
        "county": "NAIROBI",
        "location": "1 Rossyln Close, Westlands",
        "type": "HOSP",
        "email": "felicity.clinic@example.com",
        "phone_number": "+254700000000",
        "address": "P.O. BOX 44-00100 Nairobi",
        "api_base_url": "http://134.122.87.44:8000/api/",
        "date_joined": "2022-02-05 22:59:01.851628+00:00",
        "is_active": True,
    },
    {
        "uuid": "5dff619a-7e45-4569-8ef5-e427037c78e1",
        "name": "Med Labs",
        "region": "Rift Valley",
        "county": "UASIN_GISHU",
        "location": "16 Forest Drive, Mau Estate",
        "type": "MBL",
        "email": "med.labs@example.com",
        "phone_number": "+254722222222",
        "address": "P.O. BOX 98 Eldoret",
        "api_base_url": "http://127.0.0.1:8998",
        "date_joined": "2022-02-06 15:53:41.577877+00:00",
        "is_active": True,
    },
]


def run():
    """Run the populate_index script."""
    for facility in facilities:
        facility.pop("region")
        Facility.objects.update_or_create(**facility)
