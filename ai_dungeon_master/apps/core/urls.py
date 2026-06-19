from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing_view, name="landing"),
    path("healthz/", views.healthz, name="healthz"),
]
