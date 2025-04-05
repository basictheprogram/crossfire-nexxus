from ninja import ModelSchema, Schema

from nexxus.models import Server


class ServerSchema(ModelSchema):
    class Meta:
        model = Server
        fields = "__all__"


class ServerCreateSchema(Schema):
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


class Error(Schema):
    message: str
