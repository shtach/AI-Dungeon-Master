from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, render
from django.views import View
from ai_dungeon_master.apps.game.models import GameSession, Message

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.world.models import WorldSetting
from ai_dungeon_master.apps.ai.client import get_ai_client
from ai_dungeon_master.apps.ai.context_builder import build_prompt


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "game/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = Character.objects.filter(user=self.request.user)
        context['worlds'] = WorldSetting.objects.all()

        return context


class SendMessageView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related('character', 'world', 'scenario'),
            id=session_id,
            user=request.user
        )
        user_text = request.POST.get("message", "").strip()
        if not user_text:
            return render(request, "game/_messages.html", {"new_messages": []})

        user_msg = Message.objects.create(
            session=session,
            role=Message.RoleChoices.USER,
            content=user_text
        )

        ai_client = get_ai_client()
        ai_response_text = ai_client.generate(user_text)
        ai_msg = Message.objects.create(
            session=session,
            role=Message.RoleChoices.ASSISTANT,
            content=ai_response_text
        )

        return render(request, "game/_messages.html", {
            "new_messages": [user_msg, ai_msg]
        })


class GameSessionView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(GameSession, id=session_id, user=request.user)
        messages = Message.objects.filter(session=session).order_by('created_at')

        return render(request, "game/session.html", {
            "session": session,
            "messages": messages,
        })