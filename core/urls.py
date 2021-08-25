from django.urls import path
from .views import index, loginView, logoutView, register, viewComplaint, editComplaint, deleteComplaint, resolved, complaints, unresolved

app_name = "core"
urlpatterns = [
    path("", index, name = "index"),
    path("login/", loginView, name = "login"),
    path("register/", register, name = "register"),
    path("logout/", logoutView, name = "logout"),
    path("complaints/", complaints, name = "complaints"),
    path("complaint/<slug:slug>/", viewComplaint, name = "viewComplaint"),
    path("resolved/<slug:slug>/", resolved, name = "resolved"),
    path("unresolved/<slug:slug>/", unresolved, name = "unresolved"),
    path("edit-complaint/<slug:slug>/", editComplaint, name = "editComplaint"),
    path("delete-complaint/<slug:slug>/", deleteComplaint, name = "deleteComplaint"),
]