from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="legacy_profile")
    legacy_points = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username} ({self.legacy_points} pts)"


class Relic(models.Model):
    class SlotChoices(models.TextChoices):
        WEAPON = "WEAPON", "Weapon"
        ARMOR = "ARMOR", "Armor"
        TRINKET = "TRINKET", "Trinket"
        CONSUMABLE = "CONSUMABLE", "Consumable"
        MISC = "MISC", "Misc"

    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="relics")
    name = models.CharField(max_length=100)
    slot = models.CharField(max_length=20, choices=SlotChoices.choices, default=SlotChoices.MISC)
    damage_die = models.CharField(max_length=20, null=True, blank=True)
    attack_stat = models.CharField(max_length=20, null=True, blank=True)
    hit_bonus = models.IntegerField(default=0)
    ac_bonus = models.IntegerField(default=0)
    stat_bonuses = models.JSONField(default=dict, blank=True)
    lore = models.TextField(blank=True)
    source_run = models.ForeignKey(
        "game.GameSession", on_delete=models.SET_NULL, null=True, blank=True, related_name="relics"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Relic: {self.name} ({self.get_slot_display()})"


class LegacyPerk(models.Model):
    key = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    cost = models.IntegerField()
    effect = models.JSONField(
        help_text="Structured modifier the stat layer can read, e.g. "
        '{"stat": "strength", "bonus": 2} or {"damage_mult": 1.1}'
    )

    class Meta:
        ordering = ["cost"]

    def __str__(self):
        return f"{self.name} ({self.cost} pts)"


class OwnedPerk(models.Model):
    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="owned_perks")
    perk = models.ForeignKey(LegacyPerk, on_delete=models.CASCADE, related_name="owners")
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("profile", "perk")

    def __str__(self):
        return f"{self.profile} owns {self.perk}"


class SessionSummary(models.Model):
    class VerdictChoices(models.TextChoices):
        DIED = "DIED", "Died"
        WON = "WON", "Won"
        ABANDONED = "ABANDONED", "Abandoned"

    session = models.OneToOneField(
        "game.GameSession", on_delete=models.CASCADE, related_name="legacy_summary"
    )
    profile = models.ForeignKey(PlayerProfile, on_delete=models.CASCADE, related_name="session_summaries")
    verdict = models.CharField(max_length=20, choices=VerdictChoices.choices)
    stat_snapshot = models.JSONField(default=dict, help_text="Frozen stat snapshot at session end")
    deeds = models.JSONField(default=list, help_text="List of notable deeds during the run")
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary: {self.session} — {self.get_verdict_display()}"
