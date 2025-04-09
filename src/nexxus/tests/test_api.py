from http import HTTPStatus

import factory
import pytest
from django.test import Client
from faker import Faker

from nexxus.models import Server
from nexxus.tests.factories import ServerFactory

fake = Faker()


@pytest.mark.django_db
class TestNexxusController:
    """Functional tests for NexxusController endpoints."""

    client = Client()

    @pytest.fixture(autouse=True)
    def setup_method(self, db: pytest.django.db) -> None:
        """Run before every test."""
        self.client = Client()
        self.list_url = "/v3/api/servers"
        self.detail_url = lambda entry: f"/v3/api/servers/{entry}"
        self.patch_url = "/v3/api/servers"

    def test_get_servers_empty(self) -> None:
        """Should return an empty list when no servers exist."""
        response = self.client.get(self.list_url)
        assert response.status_code == HTTPStatus.OK
        assert response.json() == []

    def test_get_servers_populated(self) -> None:
        """Should return a list of existing servers."""
        server1 = ServerFactory()
        server2 = ServerFactory()
        response = self.client.get(self.list_url)
        assert response.status_code == HTTPStatus.OK
        assert len(response.json()) == 2
        entries = [server["entry"] for server in response.json()]
        assert server1.entry in entries
        assert server2.entry in entries

    def test_get_server_valid_entry(self) -> None:
        """Should return a single server with valid entry."""
        server = ServerFactory()
        response = self.client.get(self.detail_url(server.entry))
        assert response.status_code == HTTPStatus.OK
        assert response.json()["entry"] == server.entry

    def test_get_server_invalid_entry(self) -> None:
        """Should return 404 when server entry does not exist."""
        response = self.client.get(self.detail_url(99999))
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create_server_valid_payload(self) -> None:
        """Should create or update a server with valid payload."""
        payload = factory.build(dict, FACTORY_CLASS=ServerFactory)

        response = self.client.patch(self.patch_url, data=payload, content_type="application/json")

        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["hostname"] == payload["hostname"]
        assert data["port"] == payload["port"]
        assert data["text_comment"] == payload["text_comment"]
        assert Server.objects.filter(hostname=payload["hostname"]).exists()

    def test_create_server_missing_hostname_or_port(self) -> None:
        """Should return 422 if hostname or port is missing."""
        payload = {"hostname": "", "port": None}
        response = self.client.patch(self.patch_url, data=payload, content_type="application/json")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_server_updates_existing(self) -> None:
        """Should update existing server with same hostname and port."""
        # Create an instance of the server and save it to the database
        server = ServerFactory.create(hostname="example.com", port=8080)

        # Use factory.build to generate a dictionary with the default values
        payload = factory.build(dict, FACTORY_CLASS=ServerFactory)

        # Modify the payload to update only the fields you want to change
        payload.update(
            {
                "hostname": server.hostname,
                "port": server.port,
                "flags": "ZZZ",
                "platform": "windows",
                "version": "2.0.0",
            }
        )

        response = self.client.patch(
            self.patch_url,
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == HTTPStatus.CREATED

        server.refresh_from_db()
        assert server.hostname == payload["hostname"]
        assert server.port == payload["port"]
        assert server.flags == payload["flags"]
        assert server.version == payload["version"]
