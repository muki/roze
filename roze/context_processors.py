from django.conf import settings


def webpush_application_server_public_key(request):
    return {
        "WEB_PUSH_APPLICATION_SERVER_PUBLIC_KEY": settings.WEB_PUSH_APPLICATION_SERVER_PUBLIC_KEY,
    }
