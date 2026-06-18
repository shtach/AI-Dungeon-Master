import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from ai_dungeon_master.apps.game.models import GameSession
from ai_dungeon_master.apps.game.quests.models import Quest

logger = logging.getLogger("ai_dungeon_master.apps.game.quests")


class QuestAcceptView(LoginRequiredMixin, View):
    def post(self, request, session_id, quest_id):
        session = get_object_or_404(
            GameSession, id=session_id, user=request.user
        )
        quest = get_object_or_404(
            Quest, id=quest_id, session=session, status=Quest.Status.OFFERED
        )

        quest.status = Quest.Status.ACTIVE
        quest.save(update_fields=["status"])

        return JsonResponse({"accepted": True, "quest_id": quest.id})


class QuestDeclineView(LoginRequiredMixin, View):
    def post(self, request, session_id, quest_id):
        session = get_object_or_404(
            GameSession, id=session_id, user=request.user
        )
        quest = get_object_or_404(
            Quest, id=quest_id, session=session, status=Quest.Status.OFFERED
        )

        quest.status = Quest.Status.FAILED
        quest.save(update_fields=["status"])

        return JsonResponse({"declined": True, "quest_id": quest.id})


class QuestCompleteView(LoginRequiredMixin, View):
    def post(self, request, session_id, quest_id):
        session = get_object_or_404(
            GameSession, id=session_id, user=request.user
        )
        quest = get_object_or_404(
            Quest, id=quest_id, session=session, status=Quest.Status.ACTIVE
        )

        quest.status = Quest.Status.COMPLETED
        quest.save(update_fields=["status"])

        return JsonResponse({"completed": True, "quest_id": quest.id})
