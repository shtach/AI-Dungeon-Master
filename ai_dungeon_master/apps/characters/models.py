from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Character(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='characters')

    name = models.CharField(max_length=100)

    class RaceChoices(models.TextChoices):
        HUMAN = 'HUMAN', 'Human'
        ELF = 'ELF', 'Elf'
        DWARF = 'DWARF', 'Dwarf'
        ORC = 'ORC', 'Orc'

    class ClassChoices(models.TextChoices):
        WARRIOR = 'WARRIOR', 'Warrior'
        WIZARD = 'WIZARD', 'Wizard'
        ROGUE = 'ROGUE', 'Rogue'
        CLERIC = 'CLERIC', 'Cleric'

    race = models.CharField(max_length=20, choices=RaceChoices.choices, default=RaceChoices.HUMAN)
    character_class = models.CharField(max_length=20, choices=ClassChoices.choices, default=ClassChoices.WARRIOR)

    strength = models.IntegerField(default=10)
    dexterity = models.IntegerField(default=10)
    constitution = models.IntegerField(default=10)
    intelligence = models.IntegerField(default=10)
    wisdom = models.IntegerField(default=10)
    charisma = models.IntegerField(default=10)

    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)

    max_hp = models.IntegerField(default=10)
    current_hp = models.IntegerField(default=10)

    armor_class = models.IntegerField(default=10)
    speed = models.IntegerField(default=30)

    background = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_character_class_display()} {self.level} lvl.)"


class InventoryItem(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name='inventory')
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=50)
    damage = models.CharField(max_length=20, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_gold = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Owner: {self.character.name})"