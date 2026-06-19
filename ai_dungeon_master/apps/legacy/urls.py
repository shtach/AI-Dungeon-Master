from django.urls import path

from . import views

app_name = "legacy"

urlpatterns = [
    path("perk/<str:perk_key>/buy/", views.BuyPerkView.as_view(), name="buy_perk"),
    path("relic/<int:relic_id>/choose/", views.ChooseRelicView.as_view(), name="choose_relic"),
    path("session/<int:session_id>/summary/", views.SessionSummaryView.as_view(), name="session_summary"),
]
