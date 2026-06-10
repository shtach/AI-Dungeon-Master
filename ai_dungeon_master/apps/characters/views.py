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
        race = request.POST.get("race", "").strip()
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
        character_class = request.POST.get("character_class", "").strip()

        allowed_classes = ["Warrior", "Wizard", "Rogue", "Cleric"]
        if character_class not in allowed_classes:
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

        if WIZARD_SESSION_KEY in request.session:
            del request.session[WIZARD_SESSION_KEY]

        url = reverse("game:create_session") + f"?character_id={character.id}"
        return redirect(url)
