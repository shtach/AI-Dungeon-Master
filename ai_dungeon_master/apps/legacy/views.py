from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from ai_dungeon_master.apps.game.models import GameSession

from .models import SessionSummary


class SessionSummaryView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character", "world", "scenario"),
            id=session_id, user=request.user,
        )
        summary = get_object_or_404(
            SessionSummary.objects.select_related("profile"),
            session=session,
        )
        return render(request, "legacy/summary.html", {
            "session": session,
            "summary": summary,
        })
