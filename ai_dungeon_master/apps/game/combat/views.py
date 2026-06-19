import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View

from ai_dungeon_master.apps.characters.models import InventoryItem
from ai_dungeon_master.apps.game.combat.engine import (
    attack, enemy_turn, flee, outwit, persuade,
)
from ai_dungeon_master.apps.game.combat.models import Enemy
from ai_dungeon_master.apps.game.models import GameSession

logger = logging.getLogger("ai_dungeon_master.apps.game.combat")


class StartCombatView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        enemy = Enemy.objects.create(
            session=session,
            name=body.get("name", "Enemy"),
            max_hp=body.get("hp", 10),
            current_hp=body.get("hp", 10),
            armor_class=body.get("ac", 10),
            attack_bonus=body.get("attack_bonus", 0),
            damage_die=body.get("damage_die", "1d6"),
        )
        return JsonResponse({
            "enemy_id": enemy.id, "name": enemy.name,
            "hp": enemy.current_hp, "ac": enemy.armor_class,
        })


class AttackView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        enemy = get_object_or_404(Enemy, id=body.get("enemy_id"), session=session, status=Enemy.StatusChoices.ALIVE)
        weapon = get_object_or_404(
            InventoryItem, id=body.get("weapon_id"), character=session.character,
        )

        result = attack(session.character, weapon, enemy)

        combat_over = not enemy.is_alive
        return JsonResponse({**result, "enemy_name": enemy.name, "combat_over": combat_over})


class EnemyTurnView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        enemy = get_object_or_404(Enemy, id=body.get("enemy_id"), session=session, status=Enemy.StatusChoices.ALIVE)
        result = enemy_turn(enemy, session.character)

        player_dead = session.character.current_hp <= 0
        if player_dead:
            session.status = GameSession.StatusChoices.DEAD
            session.save(update_fields=["status"])

        return JsonResponse({**result, "player_dead": player_dead})


class FleeView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        result = flee(session.character)
        if result["success"]:
            Enemy.objects.filter(session=session, status=Enemy.StatusChoices.ALIVE).update(
                status=Enemy.StatusChoices.DEAD,
            )
        return JsonResponse(result)


class OutwitView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        stat = body.get("stat", "intelligence")
        if stat not in ("intelligence", "wisdom"):
            stat = "intelligence"

        result = outwit(session.character, stat)
        if result["success"]:
            Enemy.objects.filter(session=session, status=Enemy.StatusChoices.ALIVE).update(
                status=Enemy.StatusChoices.DEAD,
            )
        return JsonResponse(result)


class PersuadeView(LoginRequiredMixin, View):
    def post(self, request, session_id):
        session = get_object_or_404(
            GameSession.objects.select_related("character"),
            id=session_id, user=request.user,
        )
        result = persuade(session.character)
        if result["success"]:
            Enemy.objects.filter(session=session, status=Enemy.StatusChoices.ALIVE).update(
                status=Enemy.StatusChoices.DEAD,
            )
        return JsonResponse(result)
