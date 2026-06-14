from django.urls import path
from . import views

app_name = "dice"

urlpatterns = [
    path("session/<int:session_id>/roll/", views.RollView.as_view(), name="roll"),
]
