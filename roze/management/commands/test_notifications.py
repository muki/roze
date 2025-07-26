from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from roze.tasks import send_notification


class Command(BaseCommand):
    help = "Sends notifications to water the plants."

    def handle(self, *args, **options):
        title = f"[TEST] Just testing notifications"
        message = f"[TEST] Ignore me, please."
        url = f"{settings.URL_BASE}"
        notification_result = send_notification(title, message, url)

        self.stdout.write(self.style.SUCCESS(notification_result))
