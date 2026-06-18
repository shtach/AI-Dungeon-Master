from django.urls import path

from . import views

app_name = "combat"

urlpatterns = [
    path("session/<int:session_id>/start/", views.StartCombatView.as_view(), name="start_combat"),
    path("session/<int:session_id>/attack/", views.AttackView.as_view(), name="attack"),
    path("session/<int:session_id>/enemy-turn/", views.EnemyTurnView.as_view(), name="enemy_turn"),
    path("session/<int:session_id>/flee/", views.FleeView.as_view(), name="flee"),
    path("session/<int:session_id>/outwit/", views.OutwitView.as_view(), name="outwit"),
    path("session/<int:session_id>/persuade/", views.PersuadeView.as_view(), name="persuade"),
]
