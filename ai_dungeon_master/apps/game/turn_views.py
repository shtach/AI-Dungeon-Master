import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from ai_dungeon_master.apps.ai.client import get_ai_client
from ai_dungeon_master.apps.ai.context_builder import build_prompt
from ai_dungeon_master.apps.ai.exceptions import AIClientError, AIProviderError
from ai_dungeon_master.apps.ai.parser import parse_ai_response
from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.game.models import GameSession, Message
from ai_dungeon_master.apps.game.quests.models import Quest

logger = logging.getLogger("ai_dungeon_master.apps.game.turn_views")


def _error_payload(message: str, status: int = 500) -> JsonResponse:
    return JsonResponse({"error": message}, status=status)


def _filter_cards_by_inventory(cards: list, character: Character) -> list:
    inventory_names = set(
        character.inventory.values_list("name", flat=True).values_list("name", flat=True)
    )
    return [c for c in cards if not c.get("requires") or c["requires"] in inventory_names]


def _process_quests(session: GameSession, parsed: dict) -> None:
    quest_offer = parsed.get("quest_offer")
    if quest_offer and isinstance(quest_offer, dict):
        Quest.objects.create(
            session=session,
            title=quest_offer.get("title", "Untitled Quest"),
            description=quest_offer.get("description", ""),
            status=Quest.Status.OFFERED,
        )

    quest_complete = parsed.get("quest_complete")
    if quest_complete:
        try:
            quest = Quest.objects.get(
                id=int(quest_complete), session=session, status=Quest.Status.ACTIVE
            )
            quest.status = Quest.Status.COMPLETED
            quest.save(update_fields=["status"])
        except (Quest.DoesNotExist, ValueError):
            pass


def _apply_hp_change(session: GameSession, hp_change: int | None) -> dict:
    if hp_change is None:
        return {}

    character = session.character
    character.current_hp = max(0, min(character.max_hp, character.current_hp + hp_change))
    character.save(update_fields=["current_hp"])

    if character.current_hp == 0 and session.status == GameSession.StatusChoices.ACTIVE:
        session.status = GameSession.StatusChoices.DEAD
        session.save(update_fields=["status"])

    return {
        "hp_change": hp_change,
        "current_hp": character.current_hp,
        "max_hp": character.max_hp,
    }


def _build_response_payload(parsed: dict, dice_payload: dict | None = None, hp_payload: dict | None = None) -> dict:
    payload = {
        "narrative": parsed.get("narrative"),
        "cards": parsed.get("cards", []),
        "hp_change": parsed.get("hp_change"),
        "quest_offer": parsed.get("quest_offer"),
        "quest_complete": parsed.get("quest_complete"),
        "combat_start": parsed.get("combat_start"),
        "enemy_hp": parsed.get("enemy_hp"),
        "combat_end": parsed.get("combat_end"),
        "loot": parsed.get("loot"),
    }
    if dice_payload:
        payload["dice"] = dice_payload
    if hp_payload:
        payload["current_hp"] = hp_payload["current_hp"]
        payload["max_hp"] = hp_payload["max_hp"]
        payload["is_dead"] = hp_payload["current_hp"] == 0
    return payload


class CardClickView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character", "world", "scenario"),
            id=session_id,
            user=request.user,
        )

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return _error_payload("Invalid JSON", 400)

        label = body.get("label", "").strip()
        card_roll = body.get("roll")
        card_dc = body.get("dc")

        if not label:
            return _error_payload("Label is required", 400)

        Message.objects.create(
            session=session,
            role=Message.RoleChoices.USER,
            content=label,
        )

        try:
            ai_client = get_ai_client()
            full_prompt = build_prompt(session, label)
            ai_response_text = ai_client.generate(full_prompt)
        except AIProviderError as e:
            logger.warning("AI provider error: %s", e)
            return _error_payload("AI service temporarily unavailable. Please try again.", 503)
        except AIClientError as e:
            logger.error("AI client configuration error: %s", e)
            return _error_payload("AI service configuration error.", 500)
        except Exception as e:
            logger.error("Unexpected error calling AI: %s", e)
            return _error_payload("An unexpected error occurred.", 500)

        parsed = parse_ai_response(ai_response_text)

        Message.objects.create(
            session=session,
            role=Message.RoleChoices.ASSISTANT,
            content=ai_response_text,
        )

        parsed["cards"] = _filter_cards_by_inventory(
            parsed.get("cards", []), session.character
        )

        hp_payload = _apply_hp_change(session, parsed.get("hp_change"))

        loot = parsed.get("loot")
        if loot:
            session.pending_loot = loot
            session.save(update_fields=["pending_loot"])

        _process_quests(session, parsed)

        if card_roll:
            dice_payload = {
                "roll": card_roll,
                "dc": card_dc,
            }
            return JsonResponse(_build_response_payload(parsed, dice_payload, hp_payload))

        session.turn_count += 1
        session.save(update_fields=["turn_count"])

        return JsonResponse(_build_response_payload(parsed, hp_payload=hp_payload))


class ResolveView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character", "world", "scenario"),
            id=session_id,
            user=request.user,
        )

        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return _error_payload("Invalid JSON", 400)

        roll_result = body.get("roll_result")
        roll_total = body.get("roll_total")
        roll_success = body.get("roll_success")
        original_label = body.get("label", "action")

        if roll_result is None or roll_total is None:
            return _error_payload("roll_result and roll_total are required", 400)

        resolve_message = (
            f"{original_label} (Roll: {roll_result}, Total: {roll_total}, "
            f"{'Success' if roll_success else 'Failure'})"
        )

        Message.objects.create(
            session=session,
            role=Message.RoleChoices.USER,
            content=resolve_message,
        )

        try:
            ai_client = get_ai_client()
            full_prompt = build_prompt(session, resolve_message)
            ai_response_text = ai_client.generate(full_prompt)
        except AIProviderError as e:
            logger.warning("AI provider error on resolve: %s", e)
            return _error_payload("AI service temporarily unavailable. Please try again.", 503)
        except AIClientError as e:
            logger.error("AI client configuration error on resolve: %s", e)
            return _error_payload("AI service configuration error.", 500)
        except Exception as e:
            logger.error("Unexpected error calling AI on resolve: %s", e)
            return _error_payload("An unexpected error occurred.", 500)

        parsed = parse_ai_response(ai_response_text)

        Message.objects.create(
            session=session,
            role=Message.RoleChoices.ASSISTANT,
            content=ai_response_text,
        )

        parsed["cards"] = _filter_cards_by_inventory(
            parsed.get("cards", []), session.character
        )

        hp_payload = _apply_hp_change(session, parsed.get("hp_change"))

        loot = parsed.get("loot")
        if loot:
            session.pending_loot = loot
            session.save(update_fields=["pending_loot"])

        _process_quests(session, parsed)

        session.turn_count += 1
        session.save(update_fields=["turn_count"])

        return JsonResponse(_build_response_payload(parsed, hp_payload=hp_payload))
