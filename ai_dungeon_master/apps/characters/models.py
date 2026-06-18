from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Character(models.Model):
    CLASS_BASE_HP = {"WARRIOR": 16, "CLERIC": 14, "ROGUE": 12, "WIZARD": 10}
    CLASS_BASE_AC = {"WARRIOR": 12, "CLERIC": 11, "ROGUE": 10, "WIZARD": 10}

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="characters")
    name = models.CharField(max_length=100)

    class RaceChoices(models.TextChoices):
        HUMAN = "HUMAN", "Human"
        ELF = "ELF", "Elf"
        DWARF = "DWARF", "Dwarf"
        ORC = "ORC", "Orc"

    class ClassChoices(models.TextChoices):
        WARRIOR = "WARRIOR", "Warrior"
        WIZARD = "WIZARD", "Wizard"
        ROGUE = "ROGUE", "Rogue"
        CLERIC = "CLERIC", "Cleric"

    race = models.CharField(max_length=20, choices=RaceChoices.choices, default=RaceChoices.HUMAN)
    character_class = models.CharField(
        max_length=20,
        choices=ClassChoices.choices,
        default=ClassChoices.WARRIOR,
    )

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

    @staticmethod
    def ability_modifier(value: int) -> int:
        return (value - 10) // 2

    @property
    def str_mod(self) -> int:
        return self.ability_modifier(self.strength)

    @property
    def dex_mod(self) -> int:
        return self.ability_modifier(self.dexterity)

    @property
    def con_mod(self) -> int:
        return self.ability_modifier(self.constitution)

    @property
    def int_mod(self) -> int:
        return self.ability_modifier(self.intelligence)

    @property
    def wis_mod(self) -> int:
        return self.ability_modifier(self.wisdom)

    @property
    def cha_mod(self) -> int:
        return self.ability_modifier(self.charisma)

    def compute_derived_stats(self):
        c = self.character_class
        base_hp = self.CLASS_BASE_HP.get(c, 10)
        base_ac = self.CLASS_BASE_AC.get(c, 10)

        self.max_hp = base_hp + self.con_mod
        self.current_hp = self.max_hp
        self.armor_class = base_ac + self.dex_mod

    def save(self, *args, **kwargs):
        if not self.pk:
            self.compute_derived_stats()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.get_character_class_display()} {self.level} lvl.)"


class InventoryItem(models.Model):
    class SlotChoices(models.TextChoices):
        WEAPON = "WEAPON", "Weapon"
        ARMOR = "ARMOR", "Armor"
        TRINKET = "TRINKET", "Trinket"
        CONSUMABLE = "CONSUMABLE", "Consumable"
        MISC = "MISC", "Misc"

    class StatChoices(models.TextChoices):
        STRENGTH = "strength", "Strength"
        DEXTERITY = "dexterity", "Dexterity"
        INTELLIGENCE = "intelligence", "Intelligence"
        WISDOM = "wisdom", "Wisdom"

    character = models.ForeignKey(Character, on_delete=models.CASCADE, related_name="inventory")
    name = models.CharField(max_length=100)
    item_type = models.CharField(max_length=50)
    slot = models.CharField(max_length=20, choices=SlotChoices.choices, default=SlotChoices.MISC)
    equipped = models.BooleanField(default=False)
    damage_die = models.CharField(max_length=20, null=True, blank=True)
    attack_stat = models.CharField(max_length=20, choices=StatChoices.choices, null=True, blank=True)
    hit_bonus = models.IntegerField(default=0)
    ac_bonus = models.IntegerField(default=0)
    stat_bonuses = models.JSONField(default=dict, blank=True)
    damage = models.CharField(max_length=20, null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_gold = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} (Owner: {self.character.name})"
