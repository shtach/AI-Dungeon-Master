from django.contrib import admin

from ai_dungeon_master.apps.ai.metering import UsageRecord


@admin.register(UsageRecord)
class UsageRecordAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "provider",
        "model",
        "prompt_tokens_est",
        "latency_ms",
        "status",
    )
    list_filter = ("provider", "model", "status")
    date_hierarchy = "created_at"
    readonly_fields = (
        "provider",
        "model",
        "prompt_tokens_est",
        "latency_ms",
        "status",
        "created_at",
    )

    def has_add_permission(self, request):
        return False
