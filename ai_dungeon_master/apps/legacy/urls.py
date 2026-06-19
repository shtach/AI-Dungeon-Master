from django.urls import path

from . import views

app_name = "legacy"

urlpatterns = [
    path("session/<int:session_id>/summary/", views.SessionSummaryView.as_view(), name="session_summary"),
]
