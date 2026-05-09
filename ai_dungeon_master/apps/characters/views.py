from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

WIZARD_SESSION_KEY = 'character_wizard'


class CharacterCreateStep1View(LoginRequiredMixin, View):
    def get(self, request):
        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})

        return render(request, "characters/create_step1.html", {
            "wizard_data": wizard_data
        })

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

        return render(request, "characters/create_step2.html", {
            "wizard_data": wizard_data,
            "available_classes": ["Warrior", "Wizard", "Rogue", "Cleric"]
        })

    def post(self, request):
        character_class = request.POST.get("character_class", "").strip()

        allowed_classes = ["Warrior", "Wizard", "Rogue", "Cleric"]
        if character_class not in allowed_classes:
            return redirect("characters:create_step2")

        wizard_data = request.session.get(WIZARD_SESSION_KEY, {})
        wizard_data["character_class"] = character_class
        request.session[WIZARD_SESSION_KEY] = wizard_data

        return redirect("characters:create_step3")