from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from ai_dungeon_master.apps.game.models import GameSession

from .models import LegacyPerk, OwnedPerk, PlayerProfile, Relic, SessionSummary


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


class BuyPerkView(LoginRequiredMixin, View):
    def post(self, request, perk_key):
        perk = get_object_or_404(LegacyPerk, key=perk_key)
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)

        if OwnedPerk.objects.filter(profile=profile, perk=perk).exists():
            return JsonResponse({"error": "Already owned"}, status=400)

        if profile.legacy_points < perk.cost:
            return JsonResponse({"error": "Not enough points"}, status=400)

        try:
            profile.legacy_points -= perk.cost
            profile.save(update_fields=["legacy_points"])
            OwnedPerk.objects.create(profile=profile, perk=perk)
        except Exception:
            return JsonResponse({"error": "Purchase failed"}, status=400)

        return JsonResponse({"ok": True, "points_remaining": profile.legacy_points})


class ChooseRelicView(LoginRequiredMixin, View):
    def post(self, request, relic_id):
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
        relic = get_object_or_404(Relic, id=relic_id, profile=profile)
        request.session["chosen_relic_id"] = relic.id
        return JsonResponse({"ok": True, "relic": relic.name})
