from django.urls import path
from .views import loginView, logoutView, dashboard, newAdmin, removeAdmin, editAdmin

app_name = "managers"
urlpatterns = [
    path("login/", loginView, name = "managerLogin"),
    path("logout/", logoutView, name = "managerLogout"),
    path("new-admin/", newAdmin, name = "newAdmin"),
    path("edit-admin/<slug:slug>/", editAdmin, name = "editAdmin"),
    path("remove-user/<slug:slug>/", removeAdmin, name = "removeAdmin"),
    path("dashboard/", dashboard, name = "managerDashboard"),
]