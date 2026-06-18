from django.db import models

from ai_dungeon_master.apps.game.models import GameSession


class Enemy(models.Model):
    class StatusChoices(models.TextChoices):
        ALIVE = "ALIVE", "Alive"
        DEAD = "DEAD", "Dead"

    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="enemies"
    )
    name = models.CharField(max_length=100)
    max_hp = models.IntegerField(default=10)
    current_hp = models.IntegerField(default=10)
    armor_class = models.IntegerField(default=10)
    attack_bonus = models.IntegerField(default=0)
    damage_die = models.CharField(max_length=10, default="1d6")
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.ALIVE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.current_hp}/{self.max_hp} HP)"

    @property
    def is_alive(self):
        return self.status == self.StatusChoices.ALIVE and self.current_hp > 0
