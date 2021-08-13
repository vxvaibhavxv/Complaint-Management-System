from django.urls import path
from .views import index, loginView, logoutView, register

app_name = "core"
urlpatterns = [
    path("", index, name = "index"),
    path("login/", loginView, name = "login"),
    path("register/", register, name = "register"),
    path("logout/", logoutView, name = "logout"),
]