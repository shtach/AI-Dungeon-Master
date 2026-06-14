import json
import random

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from ai_dungeon_master.apps.characters.stats import ability_mod
from ai_dungeon_master.apps.game.models import DiceRoll, GameSession, Message

DICE_SIDES = {
    "d4": 4, "d6": 6, "d8": 8, "d10": 10,
    "d12": 12, "d20": 20, "d100": 100,
}


class RollView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id,
            user=request.user,
        )

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        dice_type = body.get("dice_type", "d20").lower()
        stat = body.get("stat")
        dc = body.get("dc")

        sides = DICE_SIDES.get(dice_type)
        if sides is None:
            return JsonResponse({"error": f"Unknown dice type: {dice_type}"}, status=400)

        roll = random.randint(1, sides)

        modifier = 0
        if stat:
            modifier = ability_mod(session.character, stat)

        total = roll + modifier

        success = None
        if dc is not None:
            try:
                dc = int(dc)
            except (ValueError, TypeError):
                return JsonResponse({"error": "DC must be an integer"}, status=400)
            success = total >= dc

        msg = Message.objects.create(
            session=session,
            role=Message.RoleChoices.SYSTEM,
            content=f"Rolled {dice_type}: {roll} + {modifier} = {total}" +
                    (f" (DC {dc}: {'Success' if success else 'Failure'})" if dc is not None else ""),
        )

        DiceRoll.objects.create(
            message=msg,
            dice_type=dice_type,
            result=roll,
        )

        return JsonResponse({
            "roll": roll,
            "modifier": modifier,
            "total": total,
            "dc": dc,
            "success": success,
        })
