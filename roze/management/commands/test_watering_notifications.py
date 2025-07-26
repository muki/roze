from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from roze.models import Flower
from roze.tasks import send_notification


class Command(BaseCommand):
    help = "Sends notifications to water the plants."

    def handle(self, *args, **options):
        flowers_that_need_watering = [
            flower
            for flower in Flower.non_archived_flowers.all()
            if flower.needs_watering(timezone.now())
        ]
        for flower in flowers_that_need_watering:
            title = f"[TEST] 🪻 {flower.name} needs 💧"
            message = f"[TEST] Time to water your {flower.name}."
            url = f"{settings.URL_BASE}/roza/{flower.id}/"
            notification_result = send_notification(title, message, url)

            self.stdout.write(self.style.SUCCESS(notification_result))
