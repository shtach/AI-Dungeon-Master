from django import forms
from .models import Character

class CharacterCreationForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'race', 'character_class']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': "Your character's name"}),
        }