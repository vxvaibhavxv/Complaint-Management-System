from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("managers/", include("managers.urls")),
    path("", include("core.urls")),
]
