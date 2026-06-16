from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = (
        "username",
        "first_name",
        "last_name",
        "email",
        "sciper",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    )

    readonly_fields = ["last_login", "date_joined"]

    search_fields = ["username", "first_name", "last_name", "email", "sciper"]

    list_display = [
        "username",
        "first_name",
        "last_name",
        "email",
        "sciper",
        "is_active",
        "is_staff",
        "is_superuser",
    ]

    list_filter = ["is_active", "is_staff", "is_superuser"]

    ordering = ["-date_joined"]
