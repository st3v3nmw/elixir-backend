"""Index app URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path("facilities/", views.list_facilities),
    path("facilities/search/", views.search_facilities),
    path("practitioners/", views.list_practitioners),
    path("practitioners/new/", views.register_practitioner),
    path("practitioners/<uuid:user_id>/", views.get_practitioner),
    path("practitioners/search/", views.search_practitioners),
    path("patients/search/", views.search_patients),
    path("records/new/", views.create_record),
    path("records/ratings/new/", views.create_rating),
    path("records/<uuid:doc_id>/", views.get_record),
    path("records/users/<uuid:user_id>/", views.list_records),
    path("records/consent/new/", views.create_consent_request),
    path("records/consent/<uuid:request_id>/update/", views.update_consent_request),
    path("records/users/<uuid:user_id>/consent/", views.list_user_consent_requests),
    path("records/logs/new/", views.create_access_log),
]
