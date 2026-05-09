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