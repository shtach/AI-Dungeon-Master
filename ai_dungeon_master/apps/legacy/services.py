import math

from django.db import transaction

from ai_dungeon_master.apps.characters.models import Character, InventoryItem
from ai_dungeon_master.apps.game.models import GameSession

from .models import PlayerProfile, Relic, SessionSummary

SURVIVAL_BONUS = 20


def _compute_points(session: GameSession, verdict: str) -> int:
    points = (
        session.turn_count * 1
        + session.kills * 5
        + session.quests_completed * 8
        + session.gold_gathered // 10
    )
    if verdict != SessionSummary.VerdictChoices.DIED:
        points += SURVIVAL_BONUS
    return max(0, math.floor(points))


def _compute_deeds(session: GameSession) -> list[str]:
    deeds = []
    if session.kills > 0:
        deeds.append(f"Slew {session.kills} {'enemy' if session.kills == 1 else 'enemies'}")
    if session.quests_completed > 0:
        deeds.append(f"Completed {session.quests_completed} {'quest' if session.quests_completed == 1 else 'quests'}")
    if session.gold_gathered > 0:
        deeds.append(f"Gathered {session.gold_gathered} gold")
    if session.nat20s > 0:
        deeds.append(f"Rolled {session.nat20s} natural 20s")
    return deeds


def _snapshot_stats(character: Character) -> dict:
    return {
        "name": character.name,
        "level": character.level,
        "class": character.character_class,
        "hp": character.current_hp,
        "max_hp": character.max_hp,
        "ac": character.armor_class,
        "strength": character.strength,
        "dexterity": character.dexterity,
        "constitution": character.constitution,
        "intelligence": character.intelligence,
        "wisdom": character.wisdom,
        "charisma": character.charisma,
    }


def _snapshot_relics(session: GameSession) -> None:
    profile, _ = PlayerProfile.objects.get_or_create(user=session.user)
    items = InventoryItem.objects.filter(character=session.character)
    for item in items:
        Relic.objects.create(
            profile=profile,
            name=item.name,
            slot=item.slot,
            damage_die=item.damage_die,
            attack_stat=item.attack_stat,
            hit_bonus=item.hit_bonus,
            ac_bonus=item.ac_bonus,
            stat_bonuses=item.stat_bonuses,
            lore=f"Looted during session {session.id}",
            source_run=session,
        )


@transaction.atomic
def end_session(session: GameSession, verdict: str) -> SessionSummary:
    profile, _ = PlayerProfile.objects.get_or_create(user=session.user)

    if verdict == SessionSummary.VerdictChoices.DIED:
        session.status = GameSession.StatusChoices.DEAD
    elif verdict == SessionSummary.VerdictChoices.WON:
        session.status = GameSession.StatusChoices.COMPLETED
    else:
        session.status = GameSession.StatusChoices.COMPLETED
    session.save(update_fields=["status"])

    points = _compute_points(session, verdict)
    deeds = _compute_deeds(session)
    stat_snapshot = _snapshot_stats(session.character)

    summary = SessionSummary.objects.create(
        session=session,
        profile=profile,
        verdict=verdict,
        stat_snapshot=stat_snapshot,
        deeds=deeds,
        points_awarded=points,
    )

    profile.legacy_points += points
    profile.save(update_fields=["legacy_points"])

    _snapshot_relics(session)

    return summary
