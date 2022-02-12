"""Config for index app."""

from django.apps import AppConfig


class IndexConfig(AppConfig):  # noqa
    default_auto_field = "django.db.models.BigAutoField"
    name = "index"
