from django.urls import path

from . import views

urlpatterns = [
    path("visits/new/", views.create_visit),
]
