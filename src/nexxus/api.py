from django.http import HttpRequest
from django.utils import timezone
from ninja_extra import NinjaExtraAPI, api_controller, route, throttle

from nexxus.models import Blacklist, Server
from nexxus.schemas import Error, ServerSchema

app = NinjaExtraAPI()

# @api_controller('/', permissions=[])
# class NexxusController:

#     @route.get("", response={200: str}, permissions=[])
#     def index(self):
#         return "Nexxus API"


@api_controller("/meta_update.php", tags=["servers"], permissions=[])
class LegacyMetaUpdateController:
    def is_blacklisted(self, request: HttpRequest, server: ServerSchema):
        if server.hostname:
            blacklist = Blacklist.objects.filter(hostname=server.hostname)
            return blacklist.exists()

    @route.get("", response={405: Error}, permissions=[])
    @throttle
    def get_servers(self) -> tuple[int, dict[str, str]]:
        return 405, {"message": "Method Not Allowed"}

    @route.post("", response={200: ServerSchema, 404: Error}, permissions=[])
    @throttle
    def update_or_create_server(self, request: HttpRequest, server: ServerSchema) -> tuple[int, dict[str, str]]:
        # blacklist = self.is_blacklisted(request, server)
        # if blacklist:
        #     return 404, {"message": "Blacklisted hostname"}

        server.last_update = timezone.now()

        instance, created = Server.objects.update_or_create(
            hostname=server.hostname,
            port=server.port,
            defaults=server.dict(),
        )
        return 200, {"message": "OK"}


app.register_controllers(
    # NexxusController,
    LegacyMetaUpdateController,
)
