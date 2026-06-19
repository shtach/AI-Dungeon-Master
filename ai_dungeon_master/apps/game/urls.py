from django.urls import include, path
from . import session_views
from . import turn_views

app_name = "game"

urlpatterns = [
    path("dashboard/", session_views.DashboardView.as_view(), name="dashboard"),
    path("session/new/", session_views.CreateSessionView.as_view(), name="create_session"),
    path("session/<int:session_id>/", session_views.GameSessionView.as_view(), name="session"),
    path("session/<int:session_id>/quests/", session_views.QuestLogView.as_view(), name="quest_log"),
    path("session/<int:session_id>/codex/", session_views.CodexView.as_view(), name="codex"),
    path("session/<int:session_id>/message/", turn_views.CardClickView.as_view(), name="card_click"),
    path("session/<int:session_id>/resolve/", turn_views.ResolveView.as_view(), name="resolve"),
    path("session/<int:session_id>/loot/", include("ai_dungeon_master.apps.game.loot.urls")),
    path("session/<int:session_id>/quest/", include("ai_dungeon_master.apps.game.quests.urls")),
    path("dice/", include("ai_dungeon_master.apps.game.dice.urls")),
    path("combat/", include("ai_dungeon_master.apps.game.combat.urls")),
]
