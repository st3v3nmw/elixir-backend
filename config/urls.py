"""Elixir project URLs."""

from django.urls import include, path

from common.utils import error404

handler404 = error404

urlpatterns = [
    path(
        "api/",
        include(
            [
                path("auth/", include("authentication.urls")),
                path("facility/", include("facility.urls")),
                path("index/", include("index.urls")),
            ]
        ),
    ),
]
