"""Config for authentication app."""

from django.apps import AppConfig


class AuthConfig(AppConfig):  # noqa
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
