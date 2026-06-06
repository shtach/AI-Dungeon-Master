from django.db import models
from django.contrib.auth import get_user_model

from ai_dungeon_master.apps.characters.models import Character
from ai_dungeon_master.apps.world.models import WorldSetting, Scenario

User = get_user_model()


class GameSession(models.Model):
    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        DEAD = "DEAD", "Dead"

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="game_sessions"
    )
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="game_sessions"
    )
    world = models.ForeignKey(
        WorldSetting, on_delete=models.CASCADE, related_name="game_sessions"
    )
    scenario = models.ForeignKey(
        Scenario, on_delete=models.CASCADE, related_name="game_sessions"
    )

    status = models.CharField(
        max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE
    )

    turn_count = models.IntegerField(default=0)
    summary = models.TextField(
        blank=True, help_text="Summary of old events for AI context"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=200, blank=True)
    last_played = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_played']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['user', 'last_played']),
        ]

    def __str__(self):
        return f"Session: {self.character.name} in {self.world.name} ({self.status})"


class Message(models.Model):
    class RoleChoices(models.TextChoices):
        USER = "USER", "User"
        ASSISTANT = "ASSISTANT", "Assistant"
        SYSTEM = "SYSTEM", "System"

    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=RoleChoices.choices)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    raw_response = models.TextField(blank=True, help_text="Raw JSON or text from AI for debugging")
    has_dice_roll = models.BooleanField(default=False)
    is_combat = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_role_display()}] {self.content[:30]}..."


class DiceRoll(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="dice_rolls"
    )
    dice_type = models.CharField(max_length=10, default="d20")
    result = models.IntegerField()

    breakdown = models.CharField(max_length=100, blank=True)
    skill = models.CharField(max_length=50, blank=True)
    dc = models.IntegerField(null=True, blank=True)
    success = models.BooleanField(null=True, blank=True)
    modifier = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.dc is not None and self.result is not None:
            self.success = (self.result + self.modifier) >= self.dc
        else:
            self.success = None
        super().save(*args, **kwargs)

    def __str__(self):
        skill_name = self.skill if self.skill else "free_roll"
        return f"{self.dice_type}({self.result}) [{skill_name}]"
