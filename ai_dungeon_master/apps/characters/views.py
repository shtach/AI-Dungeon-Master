from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Character
from .forms import CharacterCreationForm

class CharacterCreateView(LoginRequiredMixin, CreateView):
    model = Character
    form_class = CharacterCreationForm
    template_name = "characters/create.html"
    success_url = reverse_lazy("game:dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)