"""Facility app URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path("icd10/search/", views.search_icd10),
    path("loinc/search/", views.search_loinc),
    path("loinc/arrival-measurements/", views.get_arrival_measurements),
    path("hcpcs/search/", views.search_hcpcs),
    path("rxterm/search/", views.search_rxterm),
    path("visits/new/", views.create_visit),
    path("visits/<uuid:visit_id>/", views.get_visit),
    path("visits/practitioners/<uuid:practitioner_id>/", views.list_visits),
    path("encounters/new/", views.create_encounter),
    path("encounters/<uuid:encounter_id>/", views.get_encounter),
    path("encounters/practitioners/<uuid:practitioner_id>/", views.list_encounters),
    path("observations/new/", views.create_observation),
    path("charge-items/new/", views.create_charge_item),
    path("prescriptions/new/", views.create_prescription),
]
