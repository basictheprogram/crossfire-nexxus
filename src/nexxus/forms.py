import re
from typing import ClassVar

from django import forms

from nexxus.models import Server

MIN_PORT: int = 1
MAX_PORT: int = 65535


class ServerForm(forms.ModelForm):
    """Form for creating and validating Server entries."""

    class Meta:
        """Meta class for ServerForm."""

        model = Server
        fields: ClassVar[list[str]] = [
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
        ]

    def clean_hostname(self) -> str:
        """Validate and clean the hostname field."""
        hostname = self.cleaned_data.get("hostname", "")

        if not hostname:
            error_msg = "Invalid hostname."
            raise forms.ValidationError(error_msg)

        hostname = hostname.strip().lower()

        if not re.match(r"^[a-z0-9.-]+$", hostname):
            error_msg = "Invalid hostname format."
            raise forms.ValidationError(error_msg)

        return hostname

    def clean_port(self) -> int:
        """Validate and clean the port field."""
        port = self.cleaned_data.get("port")

        if port is None:
            error_msg = "Port is required."
            raise forms.ValidationError(error_msg)
        if not (MIN_PORT <= port <= MAX_PORT):
            error_msg = f"Port must be between {MIN_PORT} and {MAX_PORT}."
            raise forms.ValidationError(error_msg)

        return port
