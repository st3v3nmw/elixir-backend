"""Authentication app URLs."""

from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login),
    path("register/", views.register_user),
    path("public-key/", views.get_public_key),
    path("next-of-kin/", views.register_next_of_kin),
]
