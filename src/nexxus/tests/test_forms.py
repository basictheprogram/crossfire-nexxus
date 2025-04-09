import pytest
from faker import Faker

from nexxus.forms import ServerForm
from nexxus.models import Server

fake = Faker()


@pytest.mark.django_db
class TestServerForm:
    """Unit tests for the ServerForm form."""

    def test_valid_form(self) -> None:
        """Ensure the form accepts valid data."""
        form = ServerForm(data={"hostname": "example-server.local", "port": 8080})
        assert form.is_valid()
        instance = form.save()
        assert isinstance(instance, Server)
        assert instance.hostname == "example-server.local"
        assert instance.port == 8080

    def test_hostname_whitespace_and_case(self) -> None:
        """Test that leading/trailing whitespace and case are cleaned."""
        form = ServerForm(data={"hostname": "  ExaMple-SerVer.LOCAL ", "port": 1234})
        assert form.is_valid()
        instance = form.save()
        assert instance.hostname == "example-server.local"

    def test_invalid_hostname_characters(self) -> None:
        """Reject hostnames with invalid characters."""
        form = ServerForm(data={"hostname": "bad_host!@#", "port": 1234})
        assert not form.is_valid()
        assert "hostname" in form.errors
        assert "Invalid hostname format." in form.errors["hostname"]

    def test_missing_hostname(self) -> None:
        """Reject missing hostname."""
        form = ServerForm(data={"hostname": "", "port": 1234})
        assert not form.is_valid()
        assert "hostname" in form.errors

    def test_missing_port(self) -> None:
        """Reject if port is not provided."""
        form = ServerForm(data={"hostname": "validhost"})
        assert not form.is_valid()
        assert "port" in form.errors
        assert "Port is required." in form.errors["port"]

    def test_port_out_of_range_low(self) -> None:
        """Reject port number less than 1."""
        form = ServerForm(data={"hostname": "host", "port": 0})
        assert not form.is_valid()
        assert "port" in form.errors
        assert "Port must be between 1 and 65535." in form.errors["port"]

    def test_port_out_of_range_high(self) -> None:
        """Reject port number greater than 65535."""
        form = ServerForm(data={"hostname": "host", "port": 70000})
        assert not form.is_valid()
        assert "port" in form.errors
        assert "Port must be between 1 and 65535." in form.errors["port"]

    def test_save_does_not_commit(self) -> None:
        """Ensure commit=False works as expected."""
        form = ServerForm(data={"hostname": "testserver", "port": 8888})
        assert form.is_valid()
        instance = form.save(commit=False)
        assert isinstance(instance, Server)
        assert instance.pk is None  # Not saved yet

    def test_error_message_text(self) -> None:
        """Check error messages formatting."""
        form = ServerForm(data={"hostname": "!!", "port": 999999})
        assert not form.is_valid()
        assert form.errors["hostname"] == ["Invalid hostname format."]
        assert form.errors["port"] == ["Port must be between 1 and 65535."]
