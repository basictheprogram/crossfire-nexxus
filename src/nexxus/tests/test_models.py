import pytest
from django.db.utils import DataError

from nexxus.models import Blacklist, Server
from nexxus.tests.factories import BlacklistFactory, ServerFactory


@pytest.mark.django_db
def test_blacklist_creation() -> None:
    """Test that a Blacklist entry can be created and retrieved."""
    entry = BlacklistFactory()
    assert Blacklist.objects.count() == 1
    assert Blacklist.objects.get(entry=entry.entry).hostname == entry.hostname


@pytest.mark.django_db
def test_blacklist_null_hostname() -> None:
    """Test that Blacklist allows NULL hostname values."""
    entry = BlacklistFactory(hostname=None)
    assert entry.hostname is None
    assert str(entry) == "(Unnamed)"


@pytest.mark.django_db
def test_blacklist_str_hostname() -> None:
    """Test __str__ returns the hostname if set."""
    entry = BlacklistFactory(hostname="example.com", ip_address="192.168.1.1")
    assert str(entry) == "example.com"


@pytest.mark.django_db
def test_blacklist_str_representation() -> None:
    """Test the string representation of Blacklist entries."""
    entry = BlacklistFactory(hostname="example.com")
    assert str(entry) == "example.com"


@pytest.mark.django_db
def test_blacklist_auto_increment() -> None:
    """Test that Blacklist entries auto-increment properly."""
    entry1 = BlacklistFactory()
    entry2 = BlacklistFactory()
    assert entry2.entry == entry1.entry + 1


@pytest.mark.django_db
def test_blacklist_unique_constraint() -> None:
    """Ensure that duplicate Blacklist entries with the same hostname are allowed."""
    hostname = "duplicate.example.com"
    BlacklistFactory(hostname=hostname)
    BlacklistFactory(hostname=hostname)
    assert Blacklist.objects.filter(hostname=hostname).count() == 2


@pytest.mark.django_db
def test_server_creation() -> None:
    """Test that a Server entry can be created and retrieved."""
    server = ServerFactory()
    assert Server.objects.count() == 1
    retrieved = Server.objects.get(entry=server.entry)
    assert retrieved.hostname == server.hostname
    assert retrieved.port == server.port


@pytest.mark.django_db
def test_server_null_fields() -> None:
    """Test that optional Server fields can be NULL without errors."""
    server = ServerFactory(hostname=None, port=None)
    assert server.hostname is None
    assert server.port is None
    assert str(server) == "(Unnamed Server)"


@pytest.mark.django_db
def test_server_auto_increment() -> None:
    """Test that Server entries auto-increment properly."""
    server1 = ServerFactory()
    server2 = ServerFactory()
    assert server2.entry == server1.entry + 1


@pytest.mark.django_db
def test_server_str_representation() -> None:
    """Test the string representation of Server entries."""
    hostname = "example.com"
    port = 8080
    server = ServerFactory(hostname=hostname, port=port)
    assert str(server) == f"{hostname}:{port}"


@pytest.mark.django_db
def test_server_large_uptime() -> None:
    """Test that Server uptime handles large values properly."""
    uptime_value = 10**9  # Large uptime value
    server = ServerFactory(uptime=uptime_value)
    assert server.uptime == uptime_value


@pytest.mark.django_db
def test_server_invalid_port() -> None:
    """Test that setting an invalid port raises an error."""
    with pytest.raises(DataError):
        Server.objects.create(port=-1)
