import pytest
from faker import Faker

from nexxus.forms import ServerForm
from nexxus.models import Server
from nexxus.tests.factories import ServerFactory

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

    def test_valid_form_optional_fields(self) -> None:
        """Ensure the form accepts valid data."""
        server_data = ServerFactory.as_dict()
        form = ServerForm(data=server_data)

        assert form.is_valid()
        instance = form.save()
        assert isinstance(instance, Server)
        assert instance.hostname == server_data["hostname"]
        assert instance.port == server_data["port"]
        assert instance.html_comment == server_data["html_comment"]
        assert instance.text_comment == server_data["text_comment"]
        assert instance.archbase == server_data["archbase"]
        assert instance.mapbase == server_data["mapbase"]
        assert instance.codebase == server_data["codebase"]
        assert instance.flags == server_data["flags"]
        assert instance.num_players == server_data["num_players"]
        assert instance.in_bytes == server_data["in_bytes"]
        assert instance.out_bytes == server_data["out_bytes"]
        assert instance.uptime == server_data["uptime"]
        assert instance.version == server_data["version"]
        assert instance.sc_version == server_data["sc_version"]
        assert instance.cs_version == server_data["cs_version"]
        assert "invalid_field" not in form.cleaned_data

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
