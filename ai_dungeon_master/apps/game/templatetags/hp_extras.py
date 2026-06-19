from django import template

register = template.Library()


@register.filter
def hp_percent(current, maximum):
    """Integer 0–100 percentage of current/maximum HP (0 when max is 0)."""
    try:
        current = int(current)
        maximum = int(maximum)
    except (TypeError, ValueError):
        return 0
    if maximum <= 0:
        return 0
    pct = round(current / maximum * 100)
    return max(0, min(100, pct))


@register.filter
def hp_wounded(current, maximum):
    """True when HP is at or below the wounded threshold (<= 33%)."""
    return hp_percent(current, maximum) <= 33