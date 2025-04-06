import factory
from faker import Faker

from nexxus.models import Blacklist, Server

fake = Faker()


class BlacklistFactory(factory.django.DjangoModelFactory):
    """Factory for creating Blacklist model instances."""

    hostname = factory.LazyAttribute(lambda x: fake.domain_name())
    ip_address = factory.LazyAttribute(lambda x: fake.ipv4())

    class Meta:
        model = Blacklist


class ServerFactory(factory.django.DjangoModelFactory):
    """Factory for creating Server model instances."""

    hostname = factory.LazyAttribute(lambda x: fake.domain_name())
    port = factory.LazyAttribute(lambda x: fake.random_int(min=1024, max=65535))
    html_comment = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=1024))
    text_comment = factory.LazyAttribute(lambda x: fake.text(max_nb_chars=256))
    archbase = factory.LazyAttribute(lambda x: fake.word())
    mapbase = factory.LazyAttribute(lambda x: fake.word())
    codebase = factory.LazyAttribute(lambda x: fake.word())
    flags = factory.LazyAttribute(lambda x: fake.bothify(text="??????"))
    num_players = factory.LazyAttribute(lambda x: fake.random_int(min=0, max=100))
    in_bytes = factory.LazyAttribute(lambda x: fake.random_int(min=0, max=1000000))
    out_bytes = factory.LazyAttribute(lambda x: fake.random_int(min=0, max=1000000))
    uptime = factory.LazyAttribute(lambda x: fake.random_int(min=0, max=1000000))
    version = factory.LazyAttribute(lambda x: fake.word())
    sc_version = factory.LazyAttribute(lambda x: fake.word())
    cs_version = factory.LazyAttribute(lambda x: fake.word())
    last_update = factory.LazyAttribute(lambda x: fake.date_this_decade())

    class Meta:
        model = Server
