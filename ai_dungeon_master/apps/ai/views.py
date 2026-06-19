"""

    Tiny JSON view to eyeball current AI usage rates (RPM / TPM / RPD),
    plus per-minute and per-day time series. Staff-only.

"""

from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.utils import timezone

from ai_dungeon_master.apps.ai.metering import UsageRecord


@staff_member_required
def usage_stats(request):
    now = timezone.now()
    return JsonResponse(
        {
            "rates": UsageRecord.recent_rates(now=now),
            "per_minute": UsageRecord.per_minute(since=now - timedelta(hours=1)),
            "per_day": UsageRecord.per_day(since=now - timedelta(days=7)),
        }
    )
