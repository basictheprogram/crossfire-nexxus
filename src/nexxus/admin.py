from django.contrib import admin

from nexxus.models import Blacklist, Server

admin.site.register(Blacklist)
admin.site.register(Server)
