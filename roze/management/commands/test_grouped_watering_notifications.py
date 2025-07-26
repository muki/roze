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

        if len(flowers_that_need_watering) > 0:
            title = "[TEST] 🪻 Your flowers need 💧"
            message = "[TEST] Today is the day to water some of your plants."
            url = f"{settings.URL_BASE}/"
            notification_result = send_notification(title, message, url)

            self.stdout.write(self.style.SUCCESS(f"Sent:\n{notification_result}"))
        else:
            return self.stdout.write(self.style.SUCCESS(f"Nothing to send."))
