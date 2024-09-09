from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from users.models import User


class UserAdmin(BaseUserAdmin):
    model = User
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ("username", "phone_number", "email", "first_name",
                    "last_name", "is_staff", "is_superuser")
    ordering = ("-id",)
    list_filter = ("is_staff", "is_superuser", "is_active")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {
         "fields": ("first_name", "last_name", "telegram_username", "phone_number", "telegram_id")}),
        (_("Permissions"), {
         "fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "phone_number", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email", "first_name", "last_name")


admin.site.register(User, UserAdmin)
