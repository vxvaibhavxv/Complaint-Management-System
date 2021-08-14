from django.urls import path
from .views import index, loginView, logoutView, register, viewComplaint, editComplaint, deleteComplaint

app_name = "core"
urlpatterns = [
    path("", index, name = "index"),
    path("login/", loginView, name = "login"),
    path("register/", register, name = "register"),
    path("logout/", logoutView, name = "logout"),
    path("complaint/<slug:slug>/", viewComplaint, name = "viewComplaint"),
    path("edit-complaint/<slug:slug>/", editComplaint, name = "editComplaint"),
    path("delete-complaint/<slug:slug>/", deleteComplaint, name = "deleteComplaint"),
]