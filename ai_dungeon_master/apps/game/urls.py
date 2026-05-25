from django.urls import path
from . import views

app_name = "game"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("session/new/", views.CreateSessionView.as_view(), name="create_session"),
    path("session/<int:session_id>/", views.GameSessionView.as_view(), name="session"),
    path("session/<int:session_id>/message/", views.SendMessageView.as_view(), name="send_message"),
]