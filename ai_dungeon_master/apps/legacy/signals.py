from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PlayerProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_player_profile(sender, instance, created, **kwargs):
    try:
        if created:
            PlayerProfile.objects.create(user=instance)
    except Exception:
        pass
