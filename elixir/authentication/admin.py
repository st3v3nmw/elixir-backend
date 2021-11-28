from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import ugettext_lazy as _

from authentication.models import User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class UserAdminConfig(UserAdmin):
    form = CustomUserChangeForm

    search_fields = ("email", "first_name", "last_name", "phone_number")
    list_filter = (
        "gender",
        "is_active",
        "date_joined",
        "country",
    )
    ordering = ("-email",)
    list_display = (
        "id",
        "uuid",
        "email",
        "first_name",
        "last_name",
        "gender",
        "date_of_birth",
        "phone_number",
        "country",
        "national_id",
        "date_joined",
        "is_active",
    )
    fieldsets = (
        (
            _("Biographical Information"),
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "gender",
                    "date_of_birth",
                    "phone_number",
                    "country",
                    "national_id",
                )
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Other Information"), {"fields": ("id", "uuid", "date_joined")}),
    )
    readonly_fields = ["id", "uuid", "date_joined"]


admin.site.register(User, UserAdminConfig)
