import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from ai_dungeon_master.apps.characters.models import InventoryItem
from ai_dungeon_master.apps.game.models import GameSession

logger = logging.getLogger("ai_dungeon_master.apps.game.loot")

BONUS_LIMITS = {"hit_bonus": (-5, 10), "ac_bonus": (-5, 10)}


def _clamp_bonus(value, field):
    lo, hi = BONUS_LIMITS.get(field, (-5, 10))
    return max(lo, min(hi, int(value or 0)))


class TakeLootView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id,
            user=request.user,
        )

        loot = session.pending_loot
        if not loot:
            return JsonResponse({"error": "No pending loot"}, status=400)

        item = InventoryItem.objects.create(
            character=session.character,
            name=loot["name"],
            item_type=loot.get("item_type", "MISC"),
            slot=loot.get("slot", "MISC"),
            damage_die=loot.get("damage_die"),
            attack_stat=loot.get("attack_stat"),
            hit_bonus=_clamp_bonus(loot.get("hit_bonus"), "hit_bonus"),
            ac_bonus=_clamp_bonus(loot.get("ac_bonus"), "ac_bonus"),
            stat_bonuses=loot.get("stat_bonuses", {}),
        )

        session.pending_loot = None
        session.save(update_fields=["pending_loot"])

        return JsonResponse({"taken": True, "item_id": item.id, "name": item.name})


class LeaveLootView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id,
            user=request.user,
        )

        if not session.pending_loot:
            return JsonResponse({"error": "No pending loot"}, status=400)

        session.pending_loot = None
        session.save(update_fields=["pending_loot"])

        return JsonResponse({"discarded": True})
