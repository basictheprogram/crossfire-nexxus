from django.contrib import admin
from django.urls import include, path

from nexxus.views import LegacyClientView, LegacyHtmlView, LegacyUpdateView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Default, handles v1 and v2 metaserver
    path("", LegacyHtmlView.as_view(), name="index"),
    path("meta_client.php", LegacyClientView.as_view(), name="legacy_client"),
    path("meta_html.php", LegacyHtmlView.as_view(), name="legacy_html"),
    path("meta_update.php", LegacyUpdateView.as_view(), name="legacy_update"),
    # v3 metaserver
    path("v3/", include(("nexxus.urls", "nexxus"), namespace="v3")),
]
