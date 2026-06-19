from django.http import HttpResponse
from django.shortcuts import redirect, render


def healthz(request):
    """Lightweight liveness probe for the container healthcheck (no DB hit)."""
    return HttpResponse("ok", content_type="text/plain")


def landing_view(request):
    """Landing page for logged-out visitors; authenticated users redirect to dashboard."""
    if request.user.is_authenticated:
        return redirect("game:dashboard")

    from ai_dungeon_master.apps.world.models import WorldSetting
    worlds = WorldSetting.objects.all()[:3]

    return render(request, "landing.html", {"worlds": worlds})
