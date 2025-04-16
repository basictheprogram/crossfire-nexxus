from datetime import timedelta
from typing import Any, ClassVar, TypedDict

from django.conf import settings
from django.db.models import F
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, TemplateView

from nexxus.forms import ServerForm
from nexxus.models import Server
from nexxus.security import (
    # APIKeyCheck,
    # HMACSignatureCheck,
    HostnameBlacklistCheck,
    IPBlacklistCheck,
    # RateLimitCheck,
)


class PostRequestData(TypedDict, total=False):
    """Structure for processing a POST request."""

    html_comment: str
    text_comment: str
    archbase: str
    mapbase: str
    codebase: str
    flags: str
    num_players: int
    in_bytes: int
    out_bytes: int
    uptime: int
    version: str
    sc_version: str
    cs_version: str


class LegacyClientView(TemplateView):
    """Django view that serves the legacy client using a template."""

    model: type[Server] = Server
    template_name: str = "legacy_client.html"

    def get_queryset(self) -> QuerySet[Server]:
        """Return Server objects as documented in the legacy meta_client.php."""
        # Get the current time and subtract the timeout period (you can adjust the timeout)
        last_update_timeout = timezone.now() - timedelta(seconds=settings.LAST_UPDATE_TIMEOUT)

        # Query the Server model with the necessary filters and field selection
        queryset = (
            Server.objects.filter(last_update__gt=last_update_timeout)
            .values(
                "hostname",
                "port",
                "html_comment",
                "text_comment",
                "archbase",
                "mapbase",
                "codebase",
                "flags",
                "num_players",
                "in_bytes",
                "out_bytes",
                "uptime",
                "version",
                "sc_version",
                "cs_version",
                last_update_timestamp=F("last_update"),
            )
            .order_by("hostname")
        )

        return queryset

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict:
        """Return the context data for rendering the template."""
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        # Add the queryset to the context
        context["server_data"] = queryset
        return context


class LegacyHtmlView(ListView):
    """A view that displays a list of Server objects, ordered by hostname."""

    model: type[Server] = Server
    template_name: str = "legacy_html.html"
    context_object_name: str = "server_list"

    def get_queryset(self) -> QuerySet[Server]:
        """Return all Server objects ordered by hostname."""
        queryset: QuerySet[Server] = Server.objects.order_by("hostname")
        return queryset


@method_decorator(csrf_exempt, name="dispatch")
class LegacyUpdateView(View):
    """Django view that applies multiple security checks before processing a request."""

    security_checks: ClassVar[list] = [
        IPBlacklistCheck(),
        HostnameBlacklistCheck(),
        # APIKeyCheck(),
        # HMACSignatureCheck(),
        # RateLimitCheck(),
    ]

    def post(self, request: HttpRequest, *args, **kwargs: PostRequestData) -> HttpResponse:
        """Handle the POST request to update or create a server."""
        for check in self.security_checks:
            response = check.validate(request)
            if response:
                return response

        hostname = request.POST.get("hostname", "").strip()
        port = request.POST.get("port", "").strip()

        if not hostname or not port:
            return HttpResponse("Missing required fields hostname and/or port", status=400, content_type="text/plain")

        # Convert port safely
        port = int(port) if port.isdigit() else None
        if port is None:
            return HttpResponse("Invalid port value", status=400, content_type="text/plain")

        server, created = Server.objects.update_or_create(
            hostname=hostname,
            port=port,
            defaults={
                "html_comment": request.POST.get("html_comment", "").strip(),
                "text_comment": request.POST.get("text_comment", "").strip(),
                "archbase": request.POST.get("archbase", "").strip(),
                "mapbase": request.POST.get("mapbase", "").strip(),
                "codebase": request.POST.get("codebase", "").strip(),
                "flags": request.POST.get("flags", "").strip(),
                "num_players": int(request.POST.get("num_players", 0) or 0),
                "in_bytes": int(request.POST.get("in_bytes", 0) or 0),
                "out_bytes": int(request.POST.get("out_bytes", 0) or 0),
                "uptime": int(request.POST.get("uptime", 0) or 0),
                "version": request.POST.get("version", "").strip(),
                "sc_version": request.POST.get("sc_version", "").strip(),
                "cs_version": request.POST.get("cs_version", "").strip(),
            },
        )

        return HttpResponse(
            f"Nexxus created {hostname}" if created else f"Nexxus updated {hostname}",
            status=201 if created else 200,
            content_type="text/plain",
        )


@method_decorator(csrf_exempt, name="dispatch")
class ServerListlView(ListView):
    """A view that displays a list of Server objects, ordered by hostname."""

    model = Server
    template_name: str = "server_list.html"
    context_object_name = "server_list"

    def get_queryset(self) -> QuerySet[Server]:
        """Return all Server objects ordered by hostname."""
        queryset: QuerySet[Server] = Server.objects.order_by("hostname")
        return queryset

    def get(self, request: HttpRequest) -> HttpResponse:
        """Handle GET requests."""
        return super().get(request)

    def post(self, request: HttpRequest) -> HttpResponse:
        """Handle POST requests."""
        form = ServerForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            hostname = cleaned_data.get("hostname")
            port = cleaned_data.get("port")

            server, created = Server.objects.update_or_create(
                hostname=hostname,
                port=port,
                defaults=cleaned_data,
            )

            return HttpResponse(
                f"Nexxus created {hostname}" if created else f"Nexxus updated {hostname}",
                status=201 if created else 200,
                content_type="text/plain",
            )

        errors = form.errors.as_text()
        return HttpResponse(
            f"Invalid data: {errors}",
            status=400,
            content_type="text/plain",
        )
