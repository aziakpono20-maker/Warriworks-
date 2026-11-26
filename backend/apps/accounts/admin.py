
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import WarriWorksAdminUserCreationForm
from .models import User


@admin.register(User)
class WarriWorksUserAdmin(UserAdmin):
    add_form = WarriWorksAdminUserCreationForm

    list_display = (
        "email",
        "username",
        "role",
        "phone",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = ("email", "username", "phone")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined")},
        ),
        (
            "WarriWorks",
            {"fields": ("role", "phone", "legacy_password_hash")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
