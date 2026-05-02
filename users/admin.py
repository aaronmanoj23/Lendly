from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Campus, User


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("name", "email_domain", "city", "state")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "email_domain")


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = ("email", "full_name", "campus", "is_staff", "is_email_verified")
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("full_name", "bio", "phone", "avatar", "campus")}),
        ("Stripe", {"fields": ("stripe_account_id",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
