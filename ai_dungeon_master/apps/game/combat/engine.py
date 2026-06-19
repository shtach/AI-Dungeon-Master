import random
import re

from django.db.models import F

from ai_dungeon_master.apps.characters.stats import ability_mod, armor_class, to_hit
from ai_dungeon_master.apps.game.combat.models import Enemy


def roll_dice(notation: str) -> int:
    m = re.match(r"(\d+)d(\d+)(?:([+-])(\d+))?", notation)
    if not m:
        return 1
    count, sides, sign, bonus = int(m.group(1)), int(m.group(2)), m.group(3), int(m.group(4) or 0)
    total = sum(random.randint(1, sides) for _ in range(count))
    return total + bonus if sign == "+" else total - bonus


def attack(character, weapon, enemy: Enemy) -> dict:
    to_hit_bonus = to_hit(character, weapon)
    roll = random.randint(1, 20)
    hit_total = roll + to_hit_bonus
    hit = hit_total >= enemy.armor_class

    if not hit:
        return {"roll": roll, "total": hit_total, "hit": False, "damage": 0, "enemy_hp": enemy.current_hp}

    dmg_notation = getattr(weapon, "damage", "1d4") or "1d4"
    base_damage = roll_dice(dmg_notation)
    stat_mod = ability_mod(character, getattr(weapon, "attack_stat", "strength"))
    damage_total = max(1, base_damage + stat_mod)

    enemy.current_hp = max(0, enemy.current_hp - damage_total)
    if enemy.current_hp == 0:
        enemy.status = Enemy.StatusChoices.DEAD
    enemy.save(update_fields=["current_hp", "status"])

    from ai_dungeon_master.apps.game.models import GameSession
    updates = {"damage_dealt": F("damage_dealt") + damage_total}
    if enemy.current_hp == 0:
        updates["kills"] = F("kills") + 1
    GameSession.objects.filter(
        character=character, status=GameSession.StatusChoices.ACTIVE
    ).update(**updates)

    return {"roll": roll, "total": hit_total, "hit": True, "damage": damage_total, "enemy_hp": enemy.current_hp}


def enemy_turn(enemy: Enemy, character) -> dict:
    roll = random.randint(1, 20)
    hit_total = roll + enemy.attack_bonus
    player_ac = armor_class(character)
    hit = hit_total >= player_ac

    if not hit:
        return {"roll": roll, "total": hit_total, "hit": False, "damage": 0, "player_hp": character.current_hp}

    damage_total = max(1, roll_dice(enemy.damage_die))
    character.current_hp = max(0, character.current_hp - damage_total)
    character.save(update_fields=["current_hp"])

    from ai_dungeon_master.apps.game.models import GameSession
    GameSession.objects.filter(
        character=character, status=GameSession.StatusChoices.ACTIVE
    ).update(damage_taken=F("damage_taken") + damage_total)

    if character.current_hp == 0:
        GameSession.objects.filter(
            character=character, status=GameSession.StatusChoices.ACTIVE
        ).update(status=GameSession.StatusChoices.DEAD)

    return {"roll": roll, "total": hit_total, "hit": True, "damage": damage_total, "player_hp": character.current_hp}


def flee(character) -> dict:
    roll = random.randint(1, 20)
    dex_mod = ability_mod(character, "dexterity")
    success = (roll + dex_mod) >= 12
    return {"roll": roll, "modifier": dex_mod, "total": roll + dex_mod, "success": success}


def outwit(character, stat: str = "intelligence") -> dict:
    roll = random.randint(1, 20)
    mod = ability_mod(character, stat)
    success = (roll + mod) >= 14
    return {"roll": roll, "modifier": mod, "total": roll + mod, "success": success}


def persuade(character) -> dict:
    roll = random.randint(1, 20)
    cha_mod = ability_mod(character, "charisma")
    success = (roll + cha_mod) >= 13
    return {"roll": roll, "modifier": cha_mod, "total": roll + cha_mod, "success": success}
