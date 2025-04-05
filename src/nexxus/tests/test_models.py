import factory
import pytest
from django.db.utils import IntegrityError
from faker import Faker

from nexxus.models import Blacklist, Server

fake = Faker()


class BlacklistFactory(factory.django.DjangoModelFactory):
    """Factory for creating Blacklist model instances."""

    class Meta:
        model = Blacklist

    hostname = factory.Faker("domain_name")


class ServerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Server model instances."""

    class Meta:
        model = Server

    hostname = factory.Faker("domain_name")
    port = factory.Faker("random_int", min=1024, max=65535)
    html_comment = factory.Faker("text", max_nb_chars=100)
    text_comment = factory.Faker("text", max_nb_chars=50)
    archbase = factory.Faker("word")
    mapbase = factory.Faker("word")
    codebase = factory.Faker("word")
    flags = factory.Faker("bothify", text="??????")
    num_players = factory.Faker("random_int", min=0, max=100)
    in_bytes = factory.Faker("random_int", min=0, max=1000000)
    out_bytes = factory.Faker("random_int", min=0, max=1000000)
    uptime = factory.Faker("random_int", min=0, max=1000000)
    version = factory.Faker("word")
    sc_version = factory.Faker("word")
    cs_version = factory.Faker("word")
    last_update = factory.Faker("date_time_this_decade")


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
def test_blacklist_auto_increment() -> None:
    """Test that Blacklist entries auto-increment properly."""
    entry1 = BlacklistFactory()
    entry2 = BlacklistFactory()
    assert entry2.entry == entry1.entry + 1


@pytest.mark.django_db
def test_server_auto_increment() -> None:
    """Test that Server entries auto-increment properly."""
    server1 = ServerFactory()
    server2 = ServerFactory()
    assert server2.entry == server1.entry + 1


@pytest.mark.django_db
def test_blacklist_str_representation() -> None:
    """Test the string representation of Blacklist entries."""
    hostname = fake.domain_name()
    entry = BlacklistFactory(hostname=hostname)
    assert str(entry) == hostname


@pytest.mark.django_db
def test_server_str_representation() -> None:
    """Test the string representation of Server entries."""
    hostname = fake.domain_name()
    port = fake.random_int(min=1024, max=65535)
    server = ServerFactory(hostname=hostname, port=port)
    assert str(server) == f"{hostname}:{port}"


@pytest.mark.django_db
def test_server_large_uptime() -> None:
    """Test that Server uptime handles large values properly."""
    uptime_value = 10**9  # Large uptime value
    server = ServerFactory(uptime=uptime_value)
    assert server.uptime == uptime_value


@pytest.mark.django_db
def test_blacklist_unique_constraint() -> None:
    """Ensure that duplicate Blacklist entries with the same hostname are allowed."""
    hostname = "duplicate.example.com"
    BlacklistFactory(hostname=hostname)
    BlacklistFactory(hostname=hostname)
    assert Blacklist.objects.filter(hostname=hostname).count() == 2


@pytest.mark.django_db
def test_server_invalid_port() -> None:
    """Test that setting an invalid port raises an error."""
    with pytest.raises(IntegrityError):
        Server.objects.create(port=-1)
