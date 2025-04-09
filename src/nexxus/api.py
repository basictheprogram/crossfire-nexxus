from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja_extra import NinjaExtraAPI, api_controller, route

from nexxus.models import Server
from nexxus.schemas import ServerCreateSchema, ServerSchema

api = NinjaExtraAPI()


@api_controller("/servers", permissions=[])
class NexxusController:
    """Controller for managing Nexxus servers."""

    @route.get("", response={200: list[ServerSchema]}, permissions=[])
    def get_servers(self, request: HttpRequest) -> QuerySet[Server]:
        """Get a list of all servers."""
        return Server.objects.all()

    @route.get("/{entry}", response={200: ServerSchema}, permissions=[])
    def get_server(self, request: HttpRequest, entry: int) -> Server:
        """Get a server by entry ID."""
        server = get_object_or_404(Server, entry=entry)
        return server

    @route.patch("", response={201: ServerSchema}, permissions=[])
    def create_server(self, request: HttpRequest, server: ServerCreateSchema) -> tuple[int, Any]:
        """Create or update a server."""
        if not server.hostname or not server.port:
            return 400, {"message": "Hostname and port are required."}

        instance, created = Server.objects.update_or_create(
            hostname=server.hostname,
            port=server.port,
            defaults=server.dict(),
        )
        return 201, instance


# @api_controller("/meta_update.php", tags=["servers"], permissions=[])
# class LegacyMetaUpdateController:
#     def is_blacklisted(self, request: HttpRequest, server: ServerSchema):
#         if server.hostname:
#             blacklist = Blacklist.objects.filter(hostname=server.hostname)
#             return blacklist.exists()

#     @route.get("", response={405: Error}, permissions=[])
#     @throttle
#     def get_servers(self) -> tuple[int, dict[str, str]]:
#         return 405, {"message": "Method Not Allowed"}

#     @route.post("", response={200: ServerSchema, 404: Error}, permissions=[])
#     @throttle
#     def update_or_create_server(self, request: HttpRequest, server: ServerSchema) -> tuple[int, dict[str, str]]:
#         # blacklist = self.is_blacklisted(request, server)
#         # if blacklist:
#         #     return 404, {"message": "Blacklisted hostname"}

#         server.last_update = timezone.now()

#         instance, created = Server.objects.update_or_create(
#             hostname=server.hostname,
#             port=server.port,
#             defaults=server.dict(),
#         )
#         return 200, {"message": "OK"}


api.register_controllers(
    NexxusController,
    # LegacyMetaUpdateController,
)
