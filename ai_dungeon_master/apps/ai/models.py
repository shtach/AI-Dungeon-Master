"""

    Model registration for the ``ai`` app.

    The UsageRecord model lives in metering.py next to the code that writes it;
    re-exporting it here lets Django discover it for migrations and the admin.

"""

from ai_dungeon_master.apps.ai.metering import UsageRecord  # noqa: F401

__all__ = ["UsageRecord"]
