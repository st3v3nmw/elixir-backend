from django.urls import path, include

from common.views import error404

handler404 = error404

urlpatterns = [
    path(
        "api/",
        include(
            [
                path("auth/", include("authentication.urls")),
                path("facility", include("facility.urls")),
                path("index/", include("index.urls")),
            ]
        ),
    ),
]
