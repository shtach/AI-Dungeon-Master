from django.contrib import admin
from .models import GameSession, Message, DiceRoll

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ('character', 'world', 'status', 'turn_count')
    list_filter = ('status', 'world')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'created_at')
    list_filter = ('role', )

@admin.register(DiceRoll)
class DiceRollAdmin(admin.ModelAdmin):
    list_display = ('message', 'dice_type', 'result')