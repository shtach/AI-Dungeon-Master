from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.game.models import GameSession, Message
from ai_dungeon_master.apps.game.quests.models import Quest
from ai_dungeon_master.apps.world.models import Scenario, WorldSetting


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "game/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        characters = Character.objects.filter(user=self.request.user)

        active_sessions = (
            GameSession.objects.filter(
                user=self.request.user,
                status=GameSession.StatusChoices.ACTIVE,
            )
            .select_related("character", "world", "scenario")
        )

        active_map = {s.character_id: s for s in active_sessions}

        def hp_pct(char):
            if char.max_hp == 0:
                return 0
            return int(char.current_hp / char.max_hp * 100)

        characters_with_sessions = [
            (char, active_map.get(char.id), hp_pct(char))
            for char in characters
        ]

        context["characters_with_sessions"] = characters_with_sessions
        context["active_sessions"] = active_sessions
        return context


class GameSessionView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(GameSession, id=session_id, user=request.user)
        messages = Message.objects.filter(session=session).order_by('created_at')

        return render(request, "game/session.html", {
            "session": session,
            "messages": messages,
            "cards": session.current_cards,
        })


class QuestLogView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(GameSession, id=session_id, user=request.user)
        offered_quests = Quest.objects.filter(session=session, status=Quest.Status.OFFERED)
        active_quests = Quest.objects.filter(session=session, status=Quest.Status.ACTIVE)
        completed_quests = Quest.objects.filter(session=session, status=Quest.Status.COMPLETED)

        return render(request, "game/quests.html", {
            "session": session,
            "offered_quests": offered_quests,
            "active_quests": active_quests,
            "completed_quests": completed_quests,
        })


class CodexView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        session = get_object_or_404(GameSession, id=session_id, user=request.user)
        return render(request, "game/codex.html", {"session": session})


class CreateSessionView(LoginRequiredMixin, View):

    def get(self, request):
        character_id = request.GET.get("character_id")
        character = get_object_or_404(Character, id=character_id, user=request.user)

        worlds = WorldSetting.objects.prefetch_related("scenarios").all()
        worlds_json = [
            {
                "id": w.id,
                "name": w.name,
                "scenarios": [
                    {"id": s.id, "title": s.title}
                    for s in w.scenarios.all()
                ],
            }
            for w in worlds
        ]

        return render(request, "game/new_session.html", {
            "character": character,
            "worlds": worlds,
            "worlds_json": worlds_json,
        })

    def post(self, request):
        character_id = request.POST.get("character_id")
        world_id = request.POST.get("world_id")
        scenario_id = request.POST.get("scenario_id")

        character = get_object_or_404(Character, id=character_id, user=request.user)
        world = get_object_or_404(WorldSetting, id=world_id)
        scenario = get_object_or_404(Scenario, id=scenario_id, world=world)

        session = GameSession.objects.create(
            user=request.user,
            character=character,
            world=world,
            scenario=scenario,
        )

        Message.objects.create(
            session=session,
            role=Message.RoleChoices.ASSISTANT,
            content=scenario.intro_text,
        )

        return redirect(reverse("game:session", kwargs={"session_id": session.id}))
