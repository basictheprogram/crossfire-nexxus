from django.db import models


class Blacklist(models.Model):
    """Represents a list of blacklisted hostnames."""

    entry = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=80, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        """Meta options for the Blacklist model."""

        db_table = "blacklist"

    def __str__(self) -> str:
        """Return the string representation of the Blacklist entry."""
        return self.hostname or "(Unnamed)"


class Server(models.Model):
    """Represents a server with various metadata and statistics."""

    entry = models.AutoField(primary_key=True)
    hostname = models.CharField(max_length=80, blank=True)
    port = models.PositiveIntegerField(blank=True, null=True)
    html_comment = models.CharField(max_length=1024, blank=True)
    text_comment = models.CharField(max_length=256, blank=True)
    archbase = models.CharField(max_length=64, blank=True)
    mapbase = models.CharField(max_length=64, blank=True)
    codebase = models.CharField(max_length=64, blank=True)
    flags = models.CharField(max_length=20, blank=True)
    num_players = models.IntegerField(blank=True, null=True)
    in_bytes = models.IntegerField(blank=True, null=True)
    out_bytes = models.IntegerField(blank=True, null=True)
    uptime = models.IntegerField(blank=True, null=True)
    version = models.CharField(max_length=64, blank=True)
    sc_version = models.CharField(max_length=20, blank=True)
    cs_version = models.CharField(max_length=20, blank=True)
    last_update: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Server model."""

        db_table = "servers"

    def __str__(self) -> str:
        """Return the string representation of the Server entry."""
        return f"{self.hostname}:{self.port}" if self.hostname and self.port else "(Unnamed Server)"
