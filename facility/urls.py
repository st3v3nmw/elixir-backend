"""Facility app URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path("icd10/search/", views.search_icd10),
    path("loinc/search/", views.search_loinc),
    path("loinc/arrival-measurements/", views.get_arrival_measurements),
    path("hcpcs/search/", views.search_hcpcs),
    path("hcpcs/consultation-codes/", views.get_consultation_codes),
    path("rxterm/search/", views.search_rxterm),
    path("visits/new/", views.create_visit),
    path("visits/<uuid:visit_id>/", views.get_visit),
]
