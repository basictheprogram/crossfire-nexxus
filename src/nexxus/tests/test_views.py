from datetime import timedelta
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from nexxus.models import Server
from nexxus.tests.factories import ServerFactory

pytestmark = pytest.mark.django_db


class TestLegacyClientView:
    """Unit tests for the LegacyClientView."""

    def test_legacy_client_view_returns_active_servers(self) -> None:
        """Test that only servers updated within LAST_UPDATE_TIMEOUT are returned."""
        now = timezone.now()

        with patch("django.utils.timezone.now", return_value=now):
            active_server = ServerFactory()

        stale_time = now - timedelta(seconds=settings.LAST_UPDATE_TIMEOUT + 100)
        with patch("django.utils.timezone.now", return_value=stale_time):
            stale_server = ServerFactory()

        client = Client()
        response = client.get(reverse("legacy_client"))

        content = response.content.decode("utf-8")
        assert response.status_code == HTTPStatus.OK
        assert active_server.hostname in content
        assert stale_server.hostname not in content


class TestLegacyHtmlView:
    """Unit tests for the LegacyHtmlView."""

    def test_legacy_html_view_lists_all_servers(self) -> None:
        """Test that all servers are listed in the view context."""
        servers = ServerFactory.create_batch(3)
        client = Client()

        response = client.get(reverse("legacy_html"))

        assert response.status_code == HTTPStatus.OK
        for server in servers:
            assert server.hostname in str(response.content)


class TestLegacyUpdateView:
    """Unit tests for the LegacyUpdateView."""

    def test_post_missing_hostname_or_port_returns_400(self) -> None:
        """Test that missing required POST fields returns 400."""
        client = Client()
        response = client.post(reverse("legacy_update"), data={"hostname": "hostonly"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b"Missing required fields" in response.content

    def test_post_invalid_port_returns_400(self) -> None:
        """Test that non-numeric port returns a 400 error."""
        client = Client()
        response = client.post(reverse("legacy_update"), data={"hostname": "test", "port": "abc"})
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b"Invalid port value" in response.content

    def test_post_creates_server(self) -> None:
        """Test that a valid POST request creates a new server."""
        client = Client()
        data = {
            "hostname": "newhost",
            "port": "1234",
            "num_players": "10",
            "in_bytes": "100",
            "out_bytes": "200",
            "uptime": "3600",
        }

        response = client.post(reverse("legacy_update"), data=data)

        assert response.status_code == HTTPStatus.CREATED
        assert Server.objects.filter(hostname="newhost", port=1234).exists()
        assert b"Server created" in response.content

    def test_post_updates_existing_server(self) -> None:
        """Test that a valid POST request updates an existing server."""
        server = ServerFactory(hostname="existing", port=1234, num_players=0)
        client = Client()

        data = {
            "hostname": "existing",
            "port": "1234",
            "num_players": "99",
            "in_bytes": "100",
            "out_bytes": "200",
            "uptime": "3600",
        }

        response = client.post(reverse("legacy_update"), data=data)

        assert response.status_code == HTTPStatus.OK
        server.refresh_from_db()
        assert server.num_players == 99
        assert b"Server updated" in response.content


class TestServerListView:
    """Unit tests for the ServerListView."""

    def test_get_request_returns_server_list(self) -> None:
        """Test GET request renders server list."""
        servers = ServerFactory.create_batch(2)
        client = Client()

        response = client.get(reverse("v3:index"))

        assert response.status_code == HTTPStatus.OK
        for server in servers:
            assert server.hostname in str(response.content)

    def test_post_valid_form_creates_server(self) -> None:
        """Test valid POST request creates a new server using ServerForm."""
        client = Client()
        data = {
            "hostname": "posthost",
            "port": 8000,
            "num_players": 4,
            "in_bytes": 1000,
            "out_bytes": 2000,
            "uptime": 600,
        }

        response = client.post(reverse("v3:index"), data=data)

        assert response.status_code == HTTPStatus.CREATED
        assert Server.objects.filter(hostname="posthost", port=8000).exists()
        assert b"Server created" in response.content

    def test_post_invalid_form_returns_400(self) -> None:
        """Test invalid POST data returns 400 with form error details."""
        client = Client()
        data = {
            "hostname": "",  # Invalid
            "port": "notaport",
        }

        response = client.post(reverse("v3:index"), data=data)

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert b"Invalid data" in response.content
