from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("ai_dungeon_master.apps.accounts.urls")),
    path("", include("ai_dungeon_master.apps.game.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
