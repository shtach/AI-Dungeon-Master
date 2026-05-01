from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.world.models import WorldSetting


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "game/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = Character.objects.filter(user=self.request.user)
        context['worlds'] = WorldSetting.objects.all()

        return context