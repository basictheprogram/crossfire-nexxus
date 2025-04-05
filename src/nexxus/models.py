from django.db import models


class Blacklist(models.Model):
    """Represents a list of blacklisted hostnames."""

    entry: int = models.AutoField(primary_key=True)
    hostname: str | None = models.CharField(max_length=80, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        db_table = "blacklist"

    def __str__(self) -> str:
        return self.hostname or "(Unnamed)"


class Server(models.Model):
    """Represents a server with various metadata and statistics."""

    entry: int = models.AutoField(primary_key=True)
    hostname: str | None = models.CharField(max_length=80, blank=True, null=True)
    port: int | None = models.IntegerField(blank=True, null=True)
    html_comment: str | None = models.CharField(max_length=1024, blank=True, null=True)
    text_comment: str | None = models.CharField(max_length=256, blank=True, null=True)
    archbase: str | None = models.CharField(max_length=64, blank=True, null=True)
    mapbase: str | None = models.CharField(max_length=64, blank=True, null=True)
    codebase: str | None = models.CharField(max_length=64, blank=True, null=True)
    flags: str | None = models.CharField(max_length=20, blank=True, null=True)
    num_players: int | None = models.IntegerField(blank=True, null=True)
    in_bytes: int | None = models.IntegerField(blank=True, null=True)
    out_bytes: int | None = models.IntegerField(blank=True, null=True)
    uptime: int | None = models.IntegerField(blank=True, null=True)
    version: str | None = models.CharField(max_length=64, blank=True, null=True)
    sc_version: str | None = models.CharField(max_length=20, blank=True, null=True)
    cs_version: str | None = models.CharField(max_length=20, blank=True, null=True)
    last_update: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "servers"

    def __str__(self) -> str:
        return f"{self.hostname}:{self.port}" if self.hostname and self.port else "(Unnamed Server)"
