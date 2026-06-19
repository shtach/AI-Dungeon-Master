from django.urls import path

from ai_dungeon_master.apps.ai import views

app_name = "ai"

urlpatterns = [
    path("usage/", views.usage_stats, name="usage-stats"),
]
