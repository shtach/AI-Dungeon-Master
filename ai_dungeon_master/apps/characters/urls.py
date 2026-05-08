from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "characters"

urlpatterns = [
    #path("create/", views.CharacterCreateView.as_view(), name="create"),
    path("create/step1/", TemplateView.as_view(template_name="characters/create_step1.html"), name="create_step1"),
    path("create/step2/", TemplateView.as_view(template_name="characters/create_step2.html"), name="create_step2"),
    path("create/step3/", TemplateView.as_view(template_name="characters/create_step3.html"), name="create_step3"),
    path("create/step4/", TemplateView.as_view(template_name="characters/create_step4.html"), name="create_step4"),
]