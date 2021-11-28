from django.contrib import admin
from authentication.models import User
from django.contrib.auth.admin import UserAdmin


class UserAdminConfig(UserAdmin):
    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "gender",
        "is_active",
    )
    ordering = ("-date_joined",)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "gender",
        "is_active",
    )
    fieldsets = (
        (
            "Biographical Information",
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "phone_number",
                )
            },
        ),
        ("Status", {"fields": ("is_active",)}),
        ("Other Information", {"fields": ("id", "uuid", "date_joined")}),
    )
    readonly_fields = ["id", "uuid", "date_joined"]


admin.site.register(User, UserAdminConfig)
