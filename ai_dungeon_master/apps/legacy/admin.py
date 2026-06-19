from django.contrib import admin

from .models import PlayerProfile, Relic, LegacyPerk, OwnedPerk, SessionSummary


@admin.register(PlayerProfile)
class PlayerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "legacy_points", "created_at")
    search_fields = ("user__username",)


@admin.register(Relic)
class RelicAdmin(admin.ModelAdmin):
    list_display = ("name", "profile", "slot", "source_run")
    list_filter = ("slot",)


@admin.register(LegacyPerk)
class LegacyPerkAdmin(admin.ModelAdmin):
    list_display = ("key", "name", "cost")
    search_fields = ("name",)


@admin.register(OwnedPerk)
class OwnedPerkAdmin(admin.ModelAdmin):
    list_display = ("profile", "perk", "purchased_at")


@admin.register(SessionSummary)
class SessionSummaryAdmin(admin.ModelAdmin):
    list_display = ("session", "verdict", "points_awarded", "created_at")
    list_filter = ("verdict",)
