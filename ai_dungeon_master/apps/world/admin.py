from django.contrib import admin
from .models import WorldSetting, Scenario


@admin.register(WorldSetting)
class WorldSettingAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("world", "title")
