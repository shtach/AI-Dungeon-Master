def _get_owned_perk_effects(character):
    try:
        from ai_dungeon_master.apps.legacy.models import OwnedPerk
        profile = getattr(character.user, "legacy_profile", None)
        if profile is None:
            return []
        return [
            op.perk.effect
            for op in OwnedPerk.objects.filter(profile=profile).select_related("perk")
        ]
    except Exception:
        return []


def get_equipped_items(character, provided_items=None):
    if provided_items is not None:
        return provided_items
    return character.inventory.filter(equipped=True)


def effective_stat(character, stat_name: str, equipped_items=None) -> int:
    base_value = getattr(character, stat_name.lower(), 10)
    bonus = 0

    items = get_equipped_items(character, equipped_items)
    for item in items:
        if getattr(item, "stat_bonus_type", "").lower() == stat_name.lower():
            bonus += getattr(item, "stat_bonus_value", 0)

    for effect in _get_owned_perk_effects(character):
        if effect.get("stat", "").lower() == stat_name.lower():
            bonus += effect.get("bonus", 0)

    return base_value + bonus


def ability_mod(character, stat_name: str, equipped_items=None) -> int:
    stat_value = effective_stat(character, stat_name, equipped_items)
    return (stat_value - 10) // 2


def armor_class(character, equipped_items=None) -> int:
    base_ac = character.CLASS_BASE_AC.get(character.character_class.upper(), 10)
    dex_mod = ability_mod(character, "dexterity", equipped_items)

    gear_ac_bonus = 0
    items = get_equipped_items(character, equipped_items)
    for item in items:
        gear_ac_bonus += getattr(item, "ac_bonus", 0)

    for effect in _get_owned_perk_effects(character):
        gear_ac_bonus += effect.get("ac_bonus", 0)

    return base_ac + dex_mod + gear_ac_bonus


def to_hit(character, weapon, equipped_items=None) -> int:
    attack_stat = getattr(weapon, "attack_stat", "strength")
    stat_mod = ability_mod(character, attack_stat, equipped_items)
    weapon_bonus = getattr(weapon, "hit_bonus", 0)

    for effect in _get_owned_perk_effects(character):
        weapon_bonus += effect.get("hit_bonus", 0)

    return stat_mod + weapon_bonus


def damage(character, weapon, equipped_items=None) -> dict:
    attack_stat = getattr(weapon, "attack_stat", "strength")
    stat_mod = ability_mod(character, attack_stat, equipped_items)
    weapon_damage_bonus = getattr(weapon, "damage_bonus", 0)

    multiplier = 1.0
    for effect in _get_owned_perk_effects(character):
        multiplier *= effect.get("damage_mult", 1.0)

    return {
        "dice": getattr(weapon, "damage", "1d4"),
        "bonus": int((stat_mod + weapon_damage_bonus) * multiplier),
    }
