from datetime import timedelta

from django.db import models

from roze.models.abstract import Timestampable
from roze.models.event import Event


class Snooze(Timestampable):
    # Snooze messages
    class MESSAGES:
        @staticmethod
        def SNOOZE_SUCCESS(event_type: str, midnights: int) -> str:
            return f"⏰ {event_type.capitalize()} snoozed for {midnights} days. ⏰"

    flower: models.ForeignKey = models.ForeignKey(
        "Flower", on_delete=models.CASCADE, blank=False, null=False
    )
    midnights: models.IntegerField = models.IntegerField(
        default=2, blank=False, null=False
    )
    event_type: models.CharField = models.CharField(
        max_length=100,
        choices=Event.EVENT_TYPES,
        default=Event.WATERING,
        blank=False,
        null=False,
    )

    def __str__(self):
        return f"{self.flower.name} {self.event_type} snoozed for {self.midnights} midnights"

    def snoozed_until(self):
        return (self.created_at + timedelta(days=self.midnights)).strftime("%Y-%m-%d")
