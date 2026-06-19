from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Character

WIZARD_SESSION_KEY = "character_wizard"


class CharacterCreateStep1View(LoginRequiredMixin, View):
    def get(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        return render(request, "characters/create_step1.html", {"wizard_data": wizard_data})

    def post(self, request):
        name = request.POST.get("name", "").strip()
        race = request.POST.get("race", "").strip().upper()

        if race not in Character.RaceChoices.values:
            return redirect("characters:create_step1")

        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})
        wizard_data["name"] = name
        wizard_data["race"] = race
        request.session[WIZARD_SESSION_KEY] = wizard_data

        return redirect("characters:create_step2")


class CharacterCreateStep2View(LoginRequiredMixin, View):
    def get(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        if not wizard_data.get("name"):
            return redirect("characters:create_step1")

        return render(
            request,
            "characters/create_step2.html",
            {"wizard_data": wizard_data, "available_classes": ["Warrior", "Wizard", "Rogue", "Cleric"]},
        )

    def post(self, request):
        character_class = request.POST.get("character_class", "").strip().upper()

        if character_class not in Character.ClassChoices.values:
            return redirect("characters:create_step2")

        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})
        wizard_data["character_class"] = character_class
        request.session[WIZARD_SESSION_KEY] = wizard_data

        return redirect("characters:create_step3")


class CharacterCreateStep3View(LoginRequiredMixin, View):
    STATS = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]  # same
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]  # must be implemented in another way

    def get(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        if not wizard_data.get("character_class"):
            return redirect("characters:create_step2")

        return render(
            request,
            "characters/create_step3.html",
            {"wizard_data": wizard_data, "standard_array": self.STANDARD_ARRAY, "stats_list": self.STATS},
        )

    def post(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        player_stats = {}
        for stat in self.STATS:
            try:
                val = int(request.POST.get(stat, 0))
                player_stats[stat] = val
            except ValueError:
                player_stats[stat] = 0

        submitted_values = sorted(player_stats.values(), reverse=True)
        expected_values = sorted(self.STANDARD_ARRAY, reverse=True)

        if submitted_values != expected_values:
            return render(
                request,
                "characters/create_step3.html",
                {
                    "wizard_data": wizard_data,
                    "standard_array": self.STANDARD_ARRAY,
                    "stats_list": self.STATS,
                    "error": "You must use the exact standard array: 15, 14, 13, 12, 10, 8.",
                },
            )

        wizard_data["stats"] = player_stats
        request.session[WIZARD_SESSION_KEY] = wizard_data

        return redirect("characters:create_step4")


class CharacterCreateStep4View(LoginRequiredMixin, View):
    def get(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        if not wizard_data.get("stats"):
            return redirect("characters:create_step3")

        stats = wizard_data.get("stats", {})
        character_preview = Character(
            name=wizard_data.get("name"),
            race=wizard_data.get("race"),
            character_class=wizard_data.get("character_class"),
            strength=stats.get("strength"),
            dexterity=stats.get("dexterity"),
            constitution=stats.get("constitution"),
            intelligence=stats.get("intelligence"),
            wisdom=stats.get("wisdom"),
            charisma=stats.get("charisma"),
        )
        character_preview.compute_derived_stats()

        return render(
            request, "characters/create_step4.html", {"wizard_data": wizard_data, "character": character_preview}
        )

    def post(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        if not wizard_data:
            return redirect("characters:create_step1")

        background = request.POST.get("background", "").strip()
        stats = wizard_data.get("stats", {})

        character = Character(
            user=request.user,
            name=wizard_data.get("name"),
            race=wizard_data.get("race"),
            character_class=wizard_data.get("character_class"),
            background=background,
            strength=stats.get("strength"),
            dexterity=stats.get("dexterity"),
            constitution=stats.get("constitution"),
            intelligence=stats.get("intelligence"),
            wisdom=stats.get("wisdom"),
            charisma=stats.get("charisma"),
        )
        character.save()

        from .models import InventoryItem

        c_class = character.character_class
        if c_class == "WARRIOR":
            InventoryItem.objects.create(
                character=character,
                name="Longsword",
                item_type="Weapon",
                slot="WEAPON",
                equipped=True,
                damage_die="1d8",
                attack_stat="strength",
            )
            InventoryItem.objects.create(
                character=character, name="Chainmail", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=2
            )
        elif c_class == "WIZARD":
            InventoryItem.objects.create(
                character=character,
                name="Wooden Staff",
                item_type="Weapon",
                slot="WEAPON",
                equipped=True,
                damage_die="1d6",
                attack_stat="intelligence",
            )
            InventoryItem.objects.create(
                character=character, name="Scholar's Robe", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=1
            )
        elif c_class == "ROGUE":
            InventoryItem.objects.create(
                character=character,
                name="Steel Dagger",
                item_type="Weapon",
                slot="WEAPON",
                equipped=True,
                damage_die="1d4",
                attack_stat="dexterity",
            )
            InventoryItem.objects.create(
                character=character, name="Leather Armor", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=1
            )
        elif c_class == "CLERIC":
            InventoryItem.objects.create(
                character=character,
                name="Holy Mace",
                item_type="Weapon",
                slot="WEAPON",
                equipped=True,
                damage_die="1d6",
                attack_stat="strength",
            )
            InventoryItem.objects.create(
                character=character, name="Scale Mail", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=2
            )

        relic_id = request.session.pop("chosen_relic_id", None)
        if relic_id:
            from ai_dungeon_master.apps.legacy.models import Relic

            relic = Relic.objects.filter(id=relic_id, profile__user=request.user).first()
            if relic:
                InventoryItem.objects.create(
                    character=character, name=relic.name, item_type="Relic",
                    slot=relic.slot, equipped=True,
                    damage_die=relic.damage_die, attack_stat=relic.attack_stat,
                    hit_bonus=relic.hit_bonus, ac_bonus=relic.ac_bonus,
                    stat_bonuses=relic.stat_bonuses,
                )

        from ai_dungeon_master.apps.legacy.models import OwnedPerk, PlayerProfile
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
        for op in OwnedPerk.objects.filter(profile=profile).select_related("perk"):
            _apply_perk_to_character(character, op.perk)

        if WIZARD_SESSION_KEY in request.session:
            del request.session[WIZARD_SESSION_KEY]

        url = reverse("game:create_session") + f"?character_id={character.id}"
        return redirect(url)


class CharacterCreateLegacyView(LoginRequiredMixin, View):
    def get(self, request):
        from ai_dungeon_master.apps.legacy.models import OwnedPerk, PlayerProfile, Relic
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})
        if not wizard_data.get("stats"):
            return redirect("characters:create_step3")

        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
        relics = Relic.objects.filter(profile=profile)
        owned_perks = OwnedPerk.objects.filter(profile=profile).select_related("perk")

        return render(request, "characters/create_legacy.html", {
            "relics": relics,
            "owned_perks": [op.perk for op in owned_perks],
        })

    def post(self, request):
        relic_id = request.POST.get("relic_id")
        if relic_id:
            request.session["chosen_relic_id"] = int(relic_id)

        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})
        if not wizard_data:
            return redirect("characters:create_step1")

        background = request.POST.get("background", "").strip()
        stats = wizard_data.get("stats", {})

        character = Character(
            user=request.user,
            name=wizard_data.get("name"),
            race=wizard_data.get("race"),
            character_class=wizard_data.get("character_class"),
            background=background,
            strength=stats.get("strength"),
            dexterity=stats.get("dexterity"),
            constitution=stats.get("constitution"),
            intelligence=stats.get("intelligence"),
            wisdom=stats.get("wisdom"),
            charisma=stats.get("charisma"),
        )
        character.save()

        from .models import InventoryItem

        c_class = character.character_class
        if c_class == "WARRIOR":
            InventoryItem.objects.create(
                character=character, name="Longsword", item_type="Weapon",
                slot="WEAPON", equipped=True, damage_die="1d8", attack_stat="strength",
            )
            InventoryItem.objects.create(
                character=character, name="Chainmail", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=2
            )
        elif c_class == "WIZARD":
            InventoryItem.objects.create(
                character=character, name="Wooden Staff", item_type="Weapon",
                slot="WEAPON", equipped=True, damage_die="1d6", attack_stat="intelligence",
            )
            InventoryItem.objects.create(
                character=character, name="Scholar's Robe", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=1
            )
        elif c_class == "ROGUE":
            InventoryItem.objects.create(
                character=character, name="Steel Dagger", item_type="Weapon",
                slot="WEAPON", equipped=True, damage_die="1d4", attack_stat="dexterity",
            )
            InventoryItem.objects.create(
                character=character, name="Leather Armor", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=1
            )
        elif c_class == "CLERIC":
            InventoryItem.objects.create(
                character=character, name="Holy Mace", item_type="Weapon",
                slot="WEAPON", equipped=True, damage_die="1d6", attack_stat="strength",
            )
            InventoryItem.objects.create(
                character=character, name="Scale Mail", item_type="Armor", slot="ARMOR", equipped=True, ac_bonus=2
            )

        relic_id = request.session.pop("chosen_relic_id", None)
        if relic_id:
            from ai_dungeon_master.apps.legacy.models import Relic
            relic = Relic.objects.filter(id=relic_id, profile__user=request.user).first()
            if relic:
                InventoryItem.objects.create(
                    character=character, name=relic.name, item_type="Relic",
                    slot=relic.slot, equipped=True,
                    damage_die=relic.damage_die, attack_stat=relic.attack_stat,
                    hit_bonus=relic.hit_bonus, ac_bonus=relic.ac_bonus,
                    stat_bonuses=relic.stat_bonuses,
                )

        from ai_dungeon_master.apps.legacy.models import OwnedPerk, PlayerProfile
        profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
        for op in OwnedPerk.objects.filter(profile=profile).select_related("perk"):
            _apply_perk_to_character(character, op.perk)

        if WIZARD_SESSION_KEY in request.session:
            del request.session[WIZARD_SESSION_KEY]

        url = reverse("game:create_session") + f"?character_id={character.id}"
        return redirect(url)


def _apply_perk_to_character(character, perk):
    from .models import InventoryItem

    effect = perk.effect
    if "max_hp" in effect:
        character.max_hp += effect["max_hp"]
        character.current_hp += effect["max_hp"]
        character.save(update_fields=["max_hp", "current_hp"])
    if "stat" in effect and "bonus" in effect:
        stat_name = effect["stat"]
        if hasattr(character, stat_name):
            setattr(character, stat_name, getattr(character, stat_name) + effect["bonus"])
            character.save(update_fields=[stat_name])
    if "ac_bonus" in effect:
        InventoryItem.objects.create(
            character=character, name=perk.name, item_type="Perk",
            slot="TRINKET", equipped=True, ac_bonus=effect["ac_bonus"],
        )
