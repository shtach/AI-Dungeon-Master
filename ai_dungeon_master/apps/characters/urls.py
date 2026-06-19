from django.urls import path
from . import views

app_name = "characters"

urlpatterns = [
    path("create/step1/", views.CharacterCreateStep1View.as_view(), name="create_step1"),
    path("create/step2/", views.CharacterCreateStep2View.as_view(), name="create_step2"),
    path("create/step3/", views.CharacterCreateStep3View.as_view(), name="create_step3"),
    path("create/step4/", views.CharacterCreateStep4View.as_view(), name="create_step4"),
    path("create/legacy/", views.CharacterCreateLegacyView.as_view(), name="create_legacy"),
]