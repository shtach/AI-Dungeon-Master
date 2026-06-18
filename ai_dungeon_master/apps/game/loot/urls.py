from django.urls import path

from . import views

app_name = "loot"

urlpatterns = [
    path("take/", views.TakeLootView.as_view(), name="take"),
    path("leave/", views.LeaveLootView.as_view(), name="leave"),
]
