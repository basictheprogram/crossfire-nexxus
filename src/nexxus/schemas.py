from ninja import ModelSchema, Schema

from nexxus.models import Server


class ServerSchema(ModelSchema):
    """Schema for the Server model."""

    class Meta:
        """Meta options for the ServerSchema."""

        model = Server
        fields = "__all__"


class ServerCreateSchema(Schema):
    """Schema for creating a new server entry."""

    hostname: str
    port: int
    html_comment: str
    text_comment: str
    archbase: str
    mapbase: str
    codebase: str
    flags: str
    num_players: int
    in_bytes: int
    out_bytes: int
    uptime: int
    version: str
    sc_version: str
    cs_version: str


class ErrorSchema(Schema):
    """Schema for error responses."""

    message: str
