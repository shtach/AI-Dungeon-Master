from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ai_dungeon_master.apps.core.urls")),
    path("accounts/", include("ai_dungeon_master.apps.accounts.urls")),
    path("", include("ai_dungeon_master.apps.game.urls")),
    path("characters/", include("ai_dungeon_master.apps.characters.urls")),
    path("legacy/", include("ai_dungeon_master.apps.legacy.urls")),
    path("ai/", include("ai_dungeon_master.apps.ai.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
