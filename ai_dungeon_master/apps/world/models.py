from django.db import models

class WorldSetting(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField()

    ai_instructions = models.TextField()

    def __str__(self):
        return self.name


class Scenario(models.Model):
    world = models.ForeignKey(WorldSetting, on_delete=models.CASCADE, related_name='scenarios')

    title = models.CharField(max_length=200)

    intro_text = models.TextField()

    def __str__(self):
        return f"{self.title}, (World: {self.world.name})"