from django.urls import path

from . import views

app_name = "quests"

urlpatterns = [
    path("<int:quest_id>/accept/", views.QuestAcceptView.as_view(), name="accept"),
    path("<int:quest_id>/decline/", views.QuestDeclineView.as_view(), name="decline"),
    path("<int:quest_id>/complete/", views.QuestCompleteView.as_view(), name="complete"),
]
