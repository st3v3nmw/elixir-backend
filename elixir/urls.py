from django.urls import path, include

urlpatterns = [
    path(
        "api/",
        include(
            [
                path("auth/", include("authentication.urls")),
                path("registry/", include("registry.urls")),
            ]
        ),
    ),
]
