from django.contrib import admin
from .models import Character, InventoryItem


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "race", "character_class", "level")


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "character", "item_type", "damage", "price_gold")
