"""Index app URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path("facilities/", views.list_facilities),
    path("facilities/<uuid:pk>/", views.get_facility),
    path("facilities/search/", views.search_facilities),
    path("practitioners/", views.list_practitioners),
    path("practitioners/new/", views.register_practitioner),
    path("practitioners/<uuid:user_id>/", views.get_practitioner),
    path("practitioners/tenures/new/", views.register_tenure),
    path("practitioners/search/", views.search_practitioners),
    path("patients/<uuid:patient_id>/", views.get_patient),
    path("patients/search/", views.search_patients),
    path("records/new/", views.create_record),
    path("records/ratings/new/", views.create_rating),
    path("records/<uuid:doc_id>/", views.get_record),
    path("records/users/<uuid:user_id>/", views.list_records),
    path("records/consent/new/", views.create_consent_request),
    path("records/consent/<uuid:request_id>/", views.get_consent_request),
    path("records/consent/<uuid:request_id>/update/", views.update_consent_request),
    path("records/<uuid:record_id>/consent/", views.list_consent_requests),
    path("records/users/<uuid:user_id>/consent/", views.list_user_consent_requests),
    path("records/logs/new/", views.create_access_log),
    path("records/logs/<uuid:log_id>/", views.get_access_log),
    path("records/<uuid:record_id>/logs/", views.list_access_logs),
]
