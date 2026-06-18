from django.http import HttpResponse


def healthz(request):
    """Lightweight liveness probe for the container healthcheck (no DB hit)."""
    return HttpResponse("ok", content_type="text/plain")
