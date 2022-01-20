from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login),
    path("register/", views.register_user),
    path("public-key/", views.get_public_key),
]
