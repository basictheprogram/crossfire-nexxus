from django.urls import path

from nexxus.views import ServerListlView

app_name = "nexxus"

urlpatterns = [
    path("", ServerListlView.as_view(), name="index"),
]
