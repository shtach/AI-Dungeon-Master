from django.db import models

from ai_dungeon_master.apps.game.models import GameSession


class Quest(models.Model):
    class Status(models.TextChoices):
        OFFERED = "OFFERED", "Offered"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="quests"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.OFFERED
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.status})"
