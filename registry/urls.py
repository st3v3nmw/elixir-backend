from django.urls import path

from . import views

urlpatterns = [
    path("facilities/", views.list_facilities),
    path("facilities/<uuid:pk>/", views.get_facility),
    path("workers/new/", views.register_health_worker),
    path("workers/<uuid:pk>/", views.get_health_worker),
    path("workers/tenures/new/", views.register_tenure),
]
