from django.contrib import admin
from .forms import UserCreationForm, UserEditForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ManagerAdmin, User, Complaint, Tag, ComplaintTag, Reply, ManagerAdmin

class UserAdmin(BaseUserAdmin):
    form = UserEditForm
    add_form = UserCreationForm
    list_display = ["email", "getName", "isAdmin", "isManager", "active", "isSuperuser"]
    list_filter = ["isAdmin", "isManager", "active", "isSuperuser"]

    @admin.display(description = "Name")
    def getName(self, instance):
        return " ".join([instance.firstName, instance.lastName])

    fieldsets = (
        ("General", {"fields": ("email", "password")}),
        ("Personal", {"fields": ("firstName", "lastName")}),
        ("Permissions", {"fields": ("isAdmin", "isManager", "active", "isSuperuser")}),
    )
    add_fieldsets = (
        ("General", {"fields": ("email", "password", "password_2")}),
        ("Personal", {"fields": ("firstName", "lastName")}),
        ("Permissions", {"fields": ("isAdmin", "isManager", "active", "isSuperuser")}),
    )
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = ()

admin.site.register(User, UserAdmin)
admin.site.register(Complaint)
admin.site.register(Tag)
admin.site.register(ComplaintTag)
admin.site.register(Reply)
admin.site.register(ManagerAdmin)